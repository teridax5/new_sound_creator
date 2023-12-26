from tkinter import *
from tkinter import filedialog
from mechanics import Channel
import pyaudio as pa


class ChannelFrame(Frame):
    def __init__(self, host, channel_num):
        super().__init__(host)
        self.channel_num_label = Label(self, text=f'Channel {channel_num}: ')
        self.channel_num_label.pack(side=LEFT, anchor=W)
        self.channel_info_label = Label(self, text=f'empty')
        self.channel_info_label.pack(side=LEFT, anchor=W)

    def add_channel_info(self, info: dict):
        text = []
        for key, item in info.items():
            text.append(f'{key} - {item}')
        text = ', '.join(text)
        self.channel_info_label['text'] = text


class ChannelEditor:
    channels_num = 4

    def __init__(self):
        self.root = Tk()
        self.root.title('Channel Editor v0.0.1')
        self.root.geometry('1240x768')
        self.root.option_add("*tearOff", FALSE)

        self.channels = []

        self.menu = Menu()
        self.file_menu = Menu()
        self.file_menu.add_command(label='Add new channel', command=self.load_channel)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.root.config(menu=self.menu)

        self.channel_frames = []
        self.upload_channel_frames()
        self.play_button = Button(text='Play result', command=self.play_result_sound)
        self.play_button.pack()

        self.root.mainloop()

    def upload_channel_frames(self):
        for num in range(self.channels_num):
            self.channel_frames.append(ChannelFrame(self.root, num+1))
            self.channel_frames[-1].pack()

    def load_channel(self):
        filename = filedialog.askopenfilename(filetypes=(('WAV-files', '.wav'),))
        self.channels.append(Channel(filename))
        index = len(self.channels) - 1
        self.channel_frames[index].add_channel_info(self.channels[index].metadata)

    @property
    def shared_buffer(self):
        output_buffer = None
        for channel in self.channels:
            if output_buffer:
                output_buffer += channel
            else:
                output_buffer = channel
        return bytes(output_buffer.frame_buffer)

    def play_result_sound(self):
        print('Started playing')
        # инициализируем
        p = pa.PyAudio()
        frames = self.shared_buffer
        # создаём поток для вывода
        stream = p.open(format=pa.paInt16,
                        channels=2,
                        rate=44100,
                        output=True)
        stream.write(frames)
        # останавливаем устройство
        stream.stop_stream()
        # завершаем работу PyAudio
        stream.close()
        print('Ended playing')


if __name__ == '__main__':
    ChannelEditor()
