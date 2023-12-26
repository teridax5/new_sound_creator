from tkinter import *
from tkinter import filedialog, messagebox
from matplotlib import pyplot as plt

from mechanics import SoundCreator
import wave

from functools import wraps


def exception_handler_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except TypeError:
            messagebox.showerror('No sample',
                                 'Enter params and press "Apply" button to '
                                 'confirm!')
    return wrapper


class MainWindow:
    def __init__(self):
        self.channel_labels = []
        self.sc = SoundCreator()

        self.root = Tk()
        self.root.geometry('500x400')
        self.root.title('Sound Creator GUI v0.8.0')

        self.megaframe = Frame()
        self.megaframe.pack()

        self.common_frame = Frame(self.megaframe)
        self.common_frame.pack(side=LEFT, anchor=N)

        self.option_frame1 = Frame(self.common_frame)
        self.option_frame1.pack(anchor=W)
        self.frequency_label = Label(self.option_frame1, text='Frequency: ')
        self.frequency_label.pack(side=LEFT)
        self.frequency_entry = Entry(self.option_frame1)
        self.frequency_entry.pack(side=LEFT)

        self.option_frame2 = Frame(self.common_frame)
        self.option_frame2.pack(anchor=W)
        self.amplitude_label = Label(self.option_frame2, text='Amplitude: ')
        self.amplitude_label.pack(side=LEFT)
        self.amplitude_entry = Entry(self.option_frame2)
        self.amplitude_entry.pack(side=RIGHT)

        self.shift_frame = Frame(self.common_frame)
        self.shift_frame.pack(anchor=W)
        self.shift_label = Label(self.shift_frame, text='Start time: ')
        self.shift_label.pack(side=LEFT)
        self.shift_entry = Entry(self.shift_frame)
        self.shift_entry.pack(side=RIGHT)

        self.option_frame3 = Frame(self.common_frame)
        self.option_frame3.pack(anchor=W)
        self.delay_label = Label(self.option_frame3, text='End time: ')
        self.delay_label.pack(side=LEFT)
        self.delay_entry = Entry(self.option_frame3)
        self.delay_entry.pack(side=RIGHT)

        self.additional_frame = Frame(self.megaframe)
        self.additional_frame.pack(side=LEFT, anchor=N)

        self.option_frame4 = Frame(self.additional_frame)
        self.option_frame4.pack(anchor=E)
        self.max_freq_label = Label(self.option_frame4, text='Max frequency: ')
        self.max_freq_label.pack(side=LEFT)
        self.max_freq_entry = Entry(self.option_frame4)
        self.max_freq_entry.pack(side=RIGHT)

        self.option_frame5 = Frame(self.additional_frame)
        self.option_frame5.pack(anchor=E)
        chooses = list(self.sc.options.keys())
        self.option_var = StringVar()
        self.option_var.set('none')
        self.amplitude_func = OptionMenu(self.option_frame5, self.option_var,
                                         *chooses)
        self.amplitude_func.pack()

        self.option_frame6 = Frame(self.additional_frame)
        self.option_frame6.pack(anchor=E)
        self.option_var1 = StringVar()
        self.option_var1.set('none')
        self.phase_func = OptionMenu(self.option_frame6, self.option_var1,
                                     *chooses)
        self.phase_func.pack()

        self.button_frame = Frame()
        self.button_frame.pack()

        self.accept_button = Button(self.button_frame,
                                    text='Apply',
                                    command=self.apply_interface())
        self.accept_button.pack(side=LEFT)

        self.show_button = Button(self.button_frame,
                                  text='Grid',
                                  command=self.visualize)
        self.show_button.pack(side=LEFT)

        self.play_button = Button(self.button_frame,
                                  text='Play',
                                  command=exception_handler_decorator(
                                      self.sc.play_sound))
        self.play_button.pack(side=LEFT)

        self.save_button = Button(self.button_frame,
                                  text='Save',
                                  command=self.save_interface())
        self.save_button.pack(side=LEFT)

        self.wave_info = Label(self.button_frame, text='')
        self.wave_info.pack()

        self.channel_button_frame = Frame()
        self.channel_button_frame.pack()

        self.add_cascade = Button(self.channel_button_frame,
                                  text="Add cascaded sample",
                                  command=self.add_cascaded)
        self.add_cascade.pack(side=LEFT)

        self.scales = {}
        self.scale_pack()

        self.root.mainloop()

    def scale_pack(self):
        def scale_action(action_name):
            def setter(value):
                self.sc.__setattr__(action_name, float(value))
            return setter

        keys = ['alpha', 'pulse_mult', 'triangle_rate', 'factor', 'part']
        from_ = [20, 100, 100, 10, 10]
        to = [1, 1, 1, 1, 1]
        for idx, key in enumerate(keys):
            scale_frame = Frame()
            scale_frame.pack(side=LEFT, anchor=N)
            Label(scale_frame, text=key).pack()
            self.scales[key] = Scale(scale_frame,
                                     orient='vertical',
                                     from_=from_[idx], to=to[idx],
                                     command=scale_action(key))
            self.scales[key].pack()

    def add_cascaded(self):
        new_amp_key = self.option_var.get()
        if self.sc.options.get(new_amp_key):
            self.sc.apply_new_amp(self.sc.options[new_amp_key])

    @property
    def sample_metadata(self):
        freq = int(self.frequency_entry.get()) if self.frequency_entry.get() else None
        amp = float(self.amplitude_entry.get()) if self.amplitude_entry.get() else None
        dur = float(self.delay_entry.get()) if self.delay_entry.get() else None
        max_freq = int(self.max_freq_entry.get()) if self.max_freq_entry.get() else None
        ampl_func = self.sc.options.get(self.option_var.get())
        phase_func = self.sc.options.get(self.option_var1.get())
        metadata = {
            'freq': freq,
            'amp': amp,
            'dur': dur,
            'max_freq': max_freq,
            'ampl_func': ampl_func,
            'phase_func': phase_func
        }
        for key, data in metadata.copy().items():
            if not data:
                metadata.pop(key)
        return metadata

    def clear_buffer_interface(self):
        func = self.sc.clear_buffer

        @wraps(func)
        def wrapper():
            func()
            for label in self.channel_labels:
                label.destroy()
            self.channel_labels = []
        return wrapper

    def apply_interface(self):
        func = self.sc.apply

        @wraps(func)
        def wrapper(*args, **kwargs):
            metadata = self.sample_metadata
            kwargs['metadata'] = metadata
            func(*args, **kwargs)
        return wrapper

    def visualize(self):
        plt.plot(self.sc.time[:self.sc.sample_rate],
                 self.sc.sample[:self.sc.sample_rate])
        plt.grid()
        plt.show()

    def save_interface(self):
        func = self.sc.save

        @wraps(func)
        def wrapper(*args, **kwargs):
            filename = filedialog.asksaveasfilename(
                filetypes=(('WAV-files', '.wav'),))
            kwargs['filename'] = filename
            func(*args, **kwargs)
        return wrapper
