class KalmanFilter():
    def __init__(self, R = 1, Q = 1, A = 1, B = 0, C = 1):
        self.R = R
        self.Q = Q
        self.A = A
        self.C = C
        self.B = B
        self.cov = None
        self.x = None
    
    def filter(self, z, u = 0):
        if not self.x:
            self.x = (1 / self.C) * z
            self.cov = (1 / self.C) * self.Q * (1 / self.C)
        else:
            predX = self.predict(u)
            predCov = self.uncertainty()
            K = predCov * self.C * (1 / ((self.C * predCov * self.C) + self.Q))
            self.x = predX + K * (z - (self.C * predX))
            self.cov = predCov - (K * self.C * predCov)
        return self.x

    def predict(self, u = 0):
        return (self.A * self.x) + (self.B * u)
    
    def uncertainty(self):
        return ((self.A * self.cov) * self.A) + self.R
    
    def lastMeasurement(self):
        return self.x
    
    def setMeasurementNoise(self, noise):
        self.Q = noise
    
    def setProcessNoise(self, noise):
        self.R = noise

if __name__ == '__main__':
    kf = KalmanFilter()
    print(kf.filter(3))
    print(kf.filter(2))
    print(kf.filter(1))
























