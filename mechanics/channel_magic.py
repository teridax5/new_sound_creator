import wave
import numpy as np


class Channel:
    def __init__(self, filename='', from_file=True):
        self.frame_buffer = []
        if from_file:
            self.load_from_file(filename)

    def __add__(self, other):
        buffer1 = list(self.frame_buffer)
        buffer2 = list(other.frame_buffer)
        diff = abs(len(buffer2)-len(buffer1))
        if len(buffer1) > len(buffer2):
            buffer2 += [0]*diff
        elif len(buffer2) > len(buffer1):
            buffer1 += [0]*diff
        result_buffer = np.array(buffer1) + np.array(buffer2)
        factor = 255/max(result_buffer)
        result_buffer = result_buffer * factor
        print(min(result_buffer))
        result_buffer = bytes([int(frame) for frame in result_buffer])
        result = Channel(from_file=False)
        result.frame_buffer = result_buffer
        return result

    def load_from_file(self, filename):
        wav_file = wave.open(filename, 'rb')
        keys = ['nchannels', 'sampwidth', 'framerate',
                'nframes', 'comptype', 'compname']
        values = list(wav_file.getparams())
        # creating attribute's dictionary
        self.__setattr__('name', filename)
        for idx in range(len(keys)):
            self.__setattr__(keys[idx], values[idx])
        # main sound content
        self.frame_buffer = wav_file.readframes(values[3])

    @property
    def metadata(self):
        keys = ['nchannels', 'sampwidth', 'framerate',
                'nframes', 'comptype', 'compname', 'name']
        output = {k: self.__getattribute__(k) for k in keys}
        return output
