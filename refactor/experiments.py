import pyaudio as pa
import numpy as np
from tkinter import *
from matplotlib import pyplot as plt

# частота дискретизации
SAMPLE_RATE = 50000
# 16-ти битный звук (2 ** 16 -- максимальное значение для int16)
S_16BIT = 2 ** 16


def generate_sample(freq, duration, volume):
    # амплитуда
    amplitude = np.round(S_16BIT * volume)
    # длительность генерируемого звука в сэмплах
    total_samples = np.round(SAMPLE_RATE * duration)
    # частоте дискретизации (пересчитанная)
    w = 2.0 * np.pi * freq / SAMPLE_RATE
    # массив сэмплов
    k = np.arange(0, total_samples)
    # массив значений функции (с округлением)
    print(amplitude, total_samples, w, k, sep='\n')
    plt.plot(k, np.round(amplitude * np.sin(k * w)))
    plt.grid()
    plt.show()
    return np.round(amplitude * np.sin(k * w))


#                      до      ре      ми     фа       соль    ля      си
freq_array = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88])


def generate_tones(duration):
    tones = []
    for freq in freq_array:
        # np.array нужен для преобразования данных под формат 16 бит (dtype=np.int16)
        tone = np.array(generate_sample(freq, duration, 0.1), dtype=np.int16)
        tones.append(tone)
    return tones


tones = generate_tones(3)


# наши клавиши
key_names = ['a', 's', 'd', 'f', 'g', 'h', 'j']
# коды клавиш
key_list = list(map(lambda x: ord(x), key_names))
# состояние клавиш (нажато/не нажато)
key_dict = dict([(key, False) for key in key_list])

# инициализируем
p = pa.PyAudio()
# создаём поток для вывода
stream = p.open(format=pa.paInt16,
                channels=2, rate=SAMPLE_RATE, output=True)

# размер окна
window_size = '320x240'
# настраиваем экран
root = Tk()
root.geometry(window_size)


def play(index):
    stream.write(tones[index])


buttons = [Button(text=f'w{i+1}', command=lambda x=i: play(x)).pack()
           for i in range(len(key_names))]


# закрываем окно
root.mainloop()
# останавливаем устройство
stream.stop_stream()
# завершаем работу PyAudio
stream.close()
p.terminate()
print(tones[0])