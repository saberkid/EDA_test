import math
class Sin(object):
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


class Pulse(object):
    def __init__(self, v1, v2, td, tr, tf, pw, per ):
        self.v1 = v1
        self.v2 = v2
        self.td = td
        self.tr = tr
        self.tf = tf
        self.pw = pw
        self.per = per

    def calculate_value(self, t):
        rate1 = (self.v2 - self.v1)/self.tr
        rate2 = (self.v1 - self.v2)/self.tf
        time = (t-self.td) % self.per
        if t <= self.td:
            value = self.v1
        elif 0 < time < self.tr:
            value = self.v1 + time * rate1
        elif self.tr <= time <= self.tr + self.pw:
            value = self.v2
        elif self.tr + self.pw < time < self.tr + self.pw + self.tf:
            value = self.v2 + rate2 * (time - self.tr - self.pw)
        else:
            value = self.v1
        return value

