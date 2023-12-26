import wave


class Tone:
    pass


class WavSample:
    def __init__(self, filename):
        self.frame_buffer = []
        keys = ['nchannels', 'sampwidth', 'framerate',
                'nframes', 'comptype', 'compname']
        self.metadata = {k: '' for k in keys}
        self.load_from_file(filename)

    def load_from_file(self, filename):
        wav_file = wave.open(filename, 'rb')
        values = list(wav_file.getparams())
        # creating attribute's dictionary
        self.__setattr__('name', filename)
        for idx, key in enumerate(self.metadata.keys()):
            self.metadata[key] = values[idx]
        # main sound content
        self.frame_buffer = wav_file.readframes(values[3])

    def make_one_channel(self):
        frames = [self.frame_buffer[4*i:4*i+4] for i in range(len(self.frame_buffer)//4)]
        int_frames = [[int(byte) for byte in frame] for frame in frames]
        for frame in int_frames:
            frame[0:2] = [0, 0]
        result = []
        for frame in int_frames:
            result += frame
        self.frame_buffer = bytes(result)
        self.save('../good_samples/pulsating_beam2')

    def __add__(self, other):
        buffer1 = self.frame_buffer
        buffer2 = other.frame_buffer
        result_buffer = []
        for idx in range(max(len(buffer1), len(buffer2))):
            if (idx < len(buffer1)) and (idx < len(buffer2)):
                result = max(int(buffer1[idx]), int(buffer2[idx]))
            elif idx >= len(buffer1):
                result = int(buffer2[idx])
            else:
                result = int(buffer1[idx])
            result_buffer.append(min(255, result))
        self.frame_buffer = bytes(result_buffer)
        self.save('../result')

    def save(self, filename=None):
        wf = wave.open(filename + '.wav', 'wb')
        wf.setnchannels(self.metadata['nchannels'])
        wf.setsampwidth(self.metadata['sampwidth'])
        wf.setframerate(self.metadata['framerate'])
        wf.writeframes(self.frame_buffer)
        wf.close()


if __name__ == '__main__':
    new_wav = WavSample('../samples_tones/Hz200.wav')
    second_wav = WavSample('../good_samples/2channels200Hz_using_snarl_using_pulse_rate.wav')
    new_wav+second_wav
