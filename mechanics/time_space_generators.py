import numpy as np


class TimeSpaceBaseSignals:
    sample_rate = 44100
    s_16bit = 2 ** 15

    def __init__(self):
        self.triangle_rate = 4
        self.pulse_mult = 10
        self.alpha = 1
        self.factor = 0.5
        self.part = 0.7

    @property
    def triangle_tan(self):
        return self.triangle_rate/self.sample_rate

    def exponential_filter(self, val):
        return np.exp(-self.alpha * (val/10) / self.sample_rate)

    def pulse_rate(self, val):
        return np.sin(self.pulse_mult * val / self.sample_rate)

    def snarl(self, val):
        lenght = int(self.sample_rate * self.factor/10)
        return 1 if val % lenght < int(lenght * self.part/10) else 0

    def triangle_one_sided(self, val):
        return self.triangle_tan * (val % (self.sample_rate // self.triangle_rate))

    def triangle_pulse(self, val):
        median = self.sample_rate // self.triangle_rate
        tr_val = 2 * self.triangle_tan * (val % median)
        if tr_val < 1:
            return tr_val
        else:
            return 2 - tr_val
