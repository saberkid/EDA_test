import math
class sin(object):
    def __init__(self, vi_o, vi_a, freq, td=0., theta=0., phi=0.):
        self.vi_o = vi_o
        self.vi_a = vi_a
        self.freq = freq
        self.td = td
        self.theta = theta
        self.phi = phi
    def calculate_value(self,t):
        value = self.vi_o + self.vi_a*math.sin(2*math.pi*self.freq*t)
        return value