import wave
import numpy as np
import pyaudio as pa
from mechanics.time_space_generators import TimeSpaceBaseSignals


class SoundCreator(TimeSpaceBaseSignals):
    options = {}

    def __init__(self):
        super().__init__()
        self.add_cascade = None
        self.add_to_channel = None
        self.phase_func = None
        self.amplitude_func = None
        self.wave_info = None
        self.time = []
        self.sample = []
        self.coded_sample = []
        self.buffer_coded_sample = []
        self.options_setter()

        self.channels_buffer = []
        self.channels_buffer_index = 0
        self.channels_frame_shifts = []
        self.last_frame = 0
        self.cascade = None

        self.nchannels = 2
        self.channels = []

    def options_setter(self):
        self.options['none'] = None
        self.options['pulse'] = self.pulse_rate
        self.options['snarl'] = self.snarl
        self.options['triangle1'] = self.triangle_one_sided
        self.options['triangle2'] = self.triangle_pulse
        self.options['exponential'] = self.exponential_filter

    def apply_new_amp(self, amp_law):
        new_sample = [amp_law(idx)*self.sample[idx] for idx in
                      range(len(self.sample))]
        self.sample = np.array(new_sample)
        self.coded_sample = np.array([frame*self.s_16bit
                                      for frame in self.sample],
                                     dtype=np.int16)

    def clear_buffer(self):
        self.channels_buffer = []
        self.coded_sample = []

    def add_new_channel(self, shift):
        self.channels_buffer.append(self.coded_sample)
        self.channels_frame_shifts.append(shift if shift != 'no_shift' else 0)

    def apply(self, metadata=None):
        first_group = (metadata.get('freq') and
                       metadata.get('amp') and
                       metadata.get('dur'))
        second_group = (metadata.get('max_freq') or
                        metadata.get('ampl_func') or
                        metadata.get('phase_func'))
        if first_group and not second_group:
            self.generate_simple_sample(metadata['freq'],
                                        metadata['amp'],
                                        metadata['dur'])
            print("FIRST")
        elif first_group and second_group:
            self.generate_simple_sample(metadata['freq'],
                                        metadata['amp'],
                                        metadata['dur'],
                                        metadata['max_freq']
                                        if metadata.get('max_freq') else 0,
                                        metadata.get('ampl_func'),
                                        metadata.get('phase_func'))
            print("SECOND")

    def make_stereo(self, dur):
        for _ in range(self.nchannels):
            self.channels.append(self.coded_sample)
        result = []
        for idx in range(len(self.channels[0])):
            for channel in self.channels:
                result.append(channel[idx])
        self.channels = []
        self.time = np.arange(0, self.nchannels * np.round(self.sample_rate * dur))
        self.coded_sample = result

    def generate_tone(self, f, amp, duration):
        self.time = np.arange(0, 2 * np.round(self.sample_rate * duration))
        # some pulse tests
        afc = np.array([1] * self.time)
        # np.sin(2*k*np.pi*t_i/sample_rate) if t_i%2==0 else 1
        self.sample = np.array([amp * afc[idx] *
                                np.sin(2 * np.pi / self.sample_rate * f *
                                       self.time[idx])
                                for idx in range(len(self.time))])
        self.coded_sample = np.array([frame * self.s_16bit
                                      for frame in self.sample],
                                     dtype=np.int16)
        self.make_stereo(dur=duration)
        print('Created')
        self.wave_info['text'] = f'A={amp}, f={f}, duration={duration}'
        return self.coded_sample

    def generate_simple_sample(self, base_freq, ampl, dur, max_freq=None,
                               ampl_law=None, phase_law=None):
        self.time = np.arange(0, np.round(self.sample_rate * dur))
        len_track = len(self.time)
        freq_step = ((max_freq - base_freq) / len(self.time)) if max_freq else 0
        freqs = [base_freq + freq_step * i for i in range(len_track + 1)]
        ampl_vals = np.array([ampl * ampl_law(i) if ampl_law else ampl
                              for i in range(len_track)])
        phase_vals = np.array([phase_law(i) if phase_law else 0
                               for i in range(len_track)])

        self.sample = np.array([ampl_vals[idx] *
                                np.sin(2 * np.pi / self.sample_rate * freqs[idx] *
                                       self.time[idx] + phase_vals[idx])
                                for idx in range(len_track)])
        for _ in range(self.nchannels):
            self.channels.append(self.sample)
        result = []
        for idx in range(len(self.channels[0])):
            for channel in self.channels:
                result.append(channel[idx])
        self.channels = []
        self.time = np.arange(0, self.nchannels * np.round(self.sample_rate * dur))
        self.sample = result
        self.coded_sample = np.array([frame * self.s_16bit
                                      for frame in self.sample],
                                     dtype=np.int16)
        self.coded_sample = bytes(self.coded_sample)

    def play_sound(self):
        print('Started playing')
        # инициализируем
        p = pa.PyAudio()
        # создаём поток для вывода
        stream = p.open(format=pa.paInt16,
                        channels=self.nchannels, rate=self.sample_rate, output=True)
        stream.write(self.coded_sample)
        # останавливаем устройство
        stream.stop_stream()
        # завершаем работу PyAudio
        stream.close()
        print('Ended playing')

    @property
    def time_generator(self):
        return self.time

    @time_generator.setter
    def time_generator(self, val):
        self.time = np.arange(0, self.nchannels * np.round(val))

    def save(self, filename=None):
        wf = wave.open(filename + '.wav', 'wb')
        wf.setnchannels(self.nchannels)
        wf.setsampwidth(self.nchannels)
        wf.setframerate(self.sample_rate)
        wf.writeframes(self.coded_sample)
        wf.close()
