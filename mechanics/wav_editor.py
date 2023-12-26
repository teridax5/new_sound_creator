import wave


class WavEditor:
    def __init__(self, filename):
        self.frame_buffer = []
        self.load_from_file(filename)

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

    def read_bytes(self):
        counter = 0
        to_print = []
        for frame in self.frame_buffer[200:310]:
            to_print.append(int(frame))
            counter += 1
            if counter%4 == 0:
                counter = 0
                print(to_print)
                to_print = []


if __name__ == '__main__':
    new_wav = WavEditor("C:\\Users\\New\\Desktop\\sound_creator\\good_samples\\convert_best.wav")
    new_wav.read_bytes()
