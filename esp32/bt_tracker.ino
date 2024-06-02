
#include <WiFi.h>
#include <WiFiClient.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

// Configuration
#define SSID "your ssid"
#define WIFI_PASSWORD "your wifi password"
#define SERVER_HOSTNAME ".local server hostname"
#define SERVER_PORT 9000
//

#define TRACKER_ID 1
#define INIT_OK 1
#define INIT_FAIL 0

struct Message {
  uint8_t type;
  int32_t payload;
};

struct MessageWithName {
  uint8_t type;
  char beacon_name[50];
};

const char* ssid = SSID; 
const char* password = WIFI_PASSWORD;
const char* host = SERVER_HOSTNAME; 
const int port = SERVER_PORT; 

std::string beacon_name = "tmp";

BLEScan* pBLEScan;
int32_t rssi_to_send;
WiFiClient client;
Message  msg;

class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
      if (advertisedDevice.getName() == beacon_name) {
        Serial.printf("Advertised Device: %s \n", advertisedDevice.toString().c_str());
        rssi_to_send = advertisedDevice.getRSSI();
        pBLEScan->stop();
      }
    }
};

void connect_to_wifi() {
    Serial.println();
    Serial.println("******************************************************");
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        WiFi.begin(ssid, password);
        delay(5000);
        Serial.print(".");   
    }
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void init_ble_scanner() {
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); 
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks(), true);
  pBLEScan->setActiveScan(true);
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);
}

bool initialize_conn_to_server() {
    Message msg;
    int res;

    if (!client.connect(host, port)) {
      Serial.printf("Could not connect to the hostname %s on port %d \n", host, port);
      return false;
    }

    msg.type = 1; 
    client.write((uint8_t*)&msg, sizeof(Message));
    int start = millis();
    MessageWithName msgName;
    while (client.available() < sizeof(MessageWithName)) {
      if (millis() - start > 1000) {
        Serial.printf("Timout on ACK from server \n");
        return false;
      }
    }

    res = client.read((uint8_t*)&msgName, sizeof(MessageWithName));
    Serial.printf("GOT BEACON NAME: %s\n", msgName.beacon_name);
    beacon_name = msgName.beacon_name;
    return true;
}

void setup() {
    Serial.begin(115200);
    connect_to_wifi();
    init_ble_scanner();

    Serial.println("Trying to initialize connection to the server...");
    while (!initialize_conn_to_server()) {
      Serial.printf("Reconnecting to the server...\n");
    }
}


void loop() {
  pBLEScan->start(0, false);

  Serial.printf("sending message to server \n\r");
  msg.type = 2;
  msg.payload = rssi_to_send;
  

  if (client.connected()) {
    client.write((uint8_t*)&msg, sizeof(Message)); 
  }
  else {
    Serial.println("Server disconneted, trying to reconnect...");
    while (!initialize_conn_to_server()) {
      Serial.printf("Reconnecting to the server...\n");
    }
  }
}
