import re
import wave
import numpy as np
from matplotlib import pyplot as plt
import pyaudio as pa
import subprocess
from tkinter import *
import os
from threading import Thread


def time_format(num):
    minutes = int(num // 60)
    seconds = int(num % 60)
    if minutes >= 10 and seconds >= 10:
        return f'{minutes}:{seconds}'
    elif minutes >= 10:
        return f'{minutes}:0{seconds}'
    elif seconds >= 10:
        return f'0{minutes}:{seconds}'
    else:
        return f'0{minutes}:0{seconds}'


class MyScaleWidget:
    # width of the scroll widget
    width = 500
    # height of the scroll widget
    height = 60

    def __init__(self, host, length, current_time=0,
                 bg_color='lightgreen', widget_colour='gray17',
                 dot_size=6):
        self.host = host
        self.pause = False
        self.length = length
        self.current_time = current_time
        self.time_step = 0
        self.update_info()
        self.bg_color = bg_color
        self.widget_color = widget_colour
        self.dot_size = dot_size
        self.scroll_field = None
        self.start = False
        self.initialize()

    def update_info(self, track_length=0):
        self.length = track_length
        if self.length != 0:
            self.time_step = (self.width - 6*self.dot_size) / (self.length)
        else:
            self.time_step = 0

    def initialize(self):
        self.scroll_field = Canvas(self.host, width=self.width,
                                   height=self.height, bg=self.bg_color)
        self.scroll_field.pack()
        self.scroll_field.create_line((3*self.dot_size, self.height / 2),
                                      (self.width - 3*self.dot_size, self.height / 2),
                                      fill=self.widget_color, tag='mainline')
        x, y = 3*self.dot_size, self.height / 2
        x1, y1 = x - self.dot_size, y - self.dot_size
        x2, y2 = x + self.dot_size, y + self.dot_size
        self.scroll_field.create_oval((x1, y1), (x2, y2),
                                      fill=self.widget_color,
                                      tag='to_control')
        self.current_time = 0

    def time_info(self):
        self.scroll_field.update()
        self.scroll_field.create_text((3*self.dot_size, self.height / 2 + 20), text='00:00',
                                      tag='sound timeline current')
        self.scroll_field.create_text((self.width - 3*self.dot_size, self.height / 2 + 20),
                                      text=f'{time_format(self.length)}',
                                      tag='sound timeline')

    def scale_update(self):
        if self.start:
            self.scroll_field.delete('to_control')
            self.scroll_field.delete('sound timeline current')
            x, y = 3*self.dot_size + self.current_time*self.time_step, \
                   self.height / 2
            x1, y1 = x - self.dot_size, y - self.dot_size
            x2, y2 = x + self.dot_size, y + self.dot_size
            self.scroll_field.create_oval((x1, y1), (x2, y2), fill='gray17',
                                          tag='to_control')
            self.scroll_field.create_text(x, y - 20,
                                text=f'{time_format(self.current_time)}',
                                tag='to_control')
            self.current_time += 1
            self.host.after(1000, self.scale_update)
        elif self.pause:
            self.current_time -= 1


class MusicTools:
    # specify the sound type: mono, stereo
    types = {1: np.int8, 2: np.int16, 3: np.int32}

    def __init__(self):
        # initialize the main window
        self.root = Tk()
        # window title
        self.root.title('MP3 Editor v 1.0.0')

        # initialize variables:
        # sound wav-name
        self.music_name = ''
        # a variable for OptionMenu widget
        self.melody_set = ''
        # main sound content
        self.content = bytearray()
        # sound parameters
        self.sound_info = {}
        # sound content buffer (not used yet)
        self.buffer = []
        # current frame (for pause)
        self.frame = 0
        # logic variable for play/pause/stop
        self.is_playing = False
        # testing a new thread (maybe later it'll be deleted)
        self.test_thread = None
        # main music thread for Pyaudio
        self.music_thread = None
        # a thread for the scale widget
        self.animation_thread = None
        # a variable for a Pyaudio object
        self.pyaudio = None
        # tome counter
        self.timeline = 0
        # full sound length in secs
        self.track_length = 0
        # a step for the scale widget
        self.step_time = 0
        # a boolean variable to pause
        self.pause = False

        self.image_frame = Frame()
        self.image_frame.pack()

        self.scale_widget = MyScaleWidget(self.image_frame, 0)

        self.button_frame = Frame()
        self.button_frame.pack()

        self.play_button = Button(self.button_frame, text='Play',
                                  command=self.start_play)
        self.play_button.pack(side=LEFT)

        self.pause_button = Button(self.button_frame, text='Pause',
                                   command=self.pause_play)
        self.pause_button.pack(side=LEFT)

        self.stop_button = Button(self.button_frame, text='Stop',
                                  command=self.stop_play)
        self.stop_button.pack(side=LEFT)

        self.search_button = Button(self.button_frame,
                                    text='Choose a track',
                                    command=self.subwindow)
        self.search_button.pack(side=LEFT)

        self.audio_formats = r'mp3|MP3|m4a'
        self.files = os.listdir(os.getcwd())
        self.files = list(filter(lambda x:
                                 re.search(self.audio_formats, x),
                                 self.files))
        self.root.mainloop()

    def start_play(self):
        if not self.is_playing:
            self.stop_button['state'] = 'normal'
            self.pause_button['state'] = 'normal'
            self.music_thread = Thread(name='Music', target=self.play,
                                       daemon=True)
            self.is_playing = True
            self.scale_widget.start = True
            self.scale_widget.scale_update()
            self.music_thread.start()

    def stop_play(self):
        if self.is_playing:
            self.is_playing = False
            self.scale_widget.start = False
            self.pause_button['state'] = 'disabled'
            self.music_thread.join()
            self.music_thread = None
            self.frame = 0
            self.scale_widget.current_time = 0

    def pause_play(self):
        if self.is_playing:
            self.pause = True
            self.is_playing = False
            self.scale_widget.start = False
            self.scale_widget.pause = True
            self.stop_button['state'] = 'disabled'
            self.music_thread.join()

    def subwindow(self):
        def apply_changes():
            self.scale_widget.scroll_field.destroy()
            self.scale_widget.initialize()
            self.convert_to_wav(options.get())
            self.info()
            self.melody_set = options.get()
            os.remove(self.music_name)
            self.scale_widget.time_info()

            window.destroy()

        window = Toplevel()
        window.geometry('300x100')
        options = StringVar(window)
        if self.melody_set == '':
            options.set('Select a melody')
        else:
            options.set(self.melody_set)
        dropdown = OptionMenu(window, options, *self.files)
        dropdown.pack()
        Button(window, text='Apply', command=apply_changes).pack()

    def convert_to_wav(self, source: str):
        src = source
        name = src.split('.')[0]
        self.music_name = f'converted_{name}.wav'
        subprocess.call(['ffmpeg', '-i', src, self.music_name])

    def info(self):
        # load wav-file and its params
        wav_file = wave.open(self.music_name, 'r')
        keys = ['nchannels', 'sampwidth', 'framerate',
                'nframes', 'comptype', 'compname']
        values = list(wav_file.getparams())
        # creating attribute's dictionary
        for idx in range(len(keys)):
            self.sound_info.update({keys[idx]: values[idx]})
        # main sound content
        print(self.sound_info)
        self.content = wav_file.readframes(self.sound_info['nframes'])
        self.track_length = self.sound_info['nframes'] \
                            // self.sound_info['framerate']
        self.scale_widget.update_info(self.track_length)

    def content_in_secs(self, start_time, end_time):
        start = int(start_time*2*self.sound_info['framerate']
                    * self.sound_info['nchannels'])
        end = int(end_time*2*self.sound_info['framerate']
                  * self.sound_info['nchannels'])
        self.buffer = self.content[start:end]

    def vizualization(self):
        data = np.frombuffer(self.content,
                             dtype=self.types[self.sound_info['sampwidth']])
        frames = np.array([frame for frame in range(len(data))])
        plt.plot(frames, data)
        plt.grid()
        plt.show()

    def play(self):
        print('Started playing')
        self.pyaudio = pa.PyAudio()
        # создаём поток для вывода
        stream = self.pyaudio.open(format=pa.paInt16,
                        channels=2,
                        rate=self.sound_info['framerate'],
                        output=True)
        stream.start_stream()
        while self.is_playing:
            if self.frame < len(self.content):
                next_frame = self.frame + self.sound_info['framerate']
                stream.write(self.content[self.frame:next_frame])
                self.frame = next_frame
            else:
                self.is_playing = False
                self.scale_widget.start = False
                self.frame = 0
                self.scale_widget.current_time = 0
        # останавливаем устройство
        stream.stop_stream()
        # завершаем работу PyAudio
        stream.close()
        self.pyaudio.terminate()
        print('Ended playing')

    def save(self, filename: str):
        wf = wave.open(f'{filename}.wav', 'wb')
        wf.setnchannels(self.sound_info['nchannels'])
        wf.setsampwidth(self.sound_info['sampwidth'])
        wf.setframerate(self.sound_info['framerate'])
        wf.writeframes(self.buffer)
        wf.close()


if __name__ == '__main__':
    MusicTools()