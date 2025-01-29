import cv2
import mss
import numpy as np
import time
import os
import sounddevice as sd
from scipy.io.wavfile import write as wav_write


def record_screen(output_file="output.mp4", fps=30, duration=10, region=None):
    """
    Записывает экран в видеофайл.

    Args:
        output_file (str): Путь к файлу, куда будет сохранено видео.
        fps (int): Кадры в секунду.
        duration (int): Длительность записи в секундах.
        region (tuple): Координаты для записи конкретной области экрана (x, y, width, height).
                      Если None, записывается весь экран.
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1] if region is None else region

        if region is not None:
            # В случае указания region, используем его
            monitor = {"top": region[1], "left": region[0], "width": region[2], "height": region[3]}

        width = monitor["width"]
        height = monitor["height"]

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        start_time = time.time()
        while (time.time() - start_time) < duration:
            sct_img = sct.grab(monitor)
            img = np.array(sct_img)

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

            out.write(img_rgb)

        out.release()
        print(f"Видео сохранено в {output_file}")


def record_audio(output_file="output.wav", duration=10, samplerate=44100, channels=2):
    """
    Записывает аудио с микрофона в файл .wav.

    Args:
        output_file (str): Путь к файлу, куда будет сохранено аудио.
        duration (int): Длительность записи в секундах.
        samplerate (int): Частота дискретизации.
        channels (int): Количество каналов (обычно 1 для моно, 2 для стерео).
    """
    print("Начало записи аудио...")
    try:
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels)
        sd.wait()  # Ждем окончания записи
        wav_write(output_file, samplerate, audio)
        print(f"Аудио сохранено в {output_file}")
    except Exception as e:
        print(f"Произошла ошибка записи аудио: {e}")


if __name__ == "__main__":
    from datetime import datetime as dt
    output_filename = f"{dt.now().strftime('%d-%m-%Y_%H-%M-%S')}_screen.mp4"
    output_audio_filename = f"{dt.now().strftime('%d-%m-%Y_%H-%M-%S')}_audio_.wav"
    record_time = 60
    region_of_screen = None  # (100, 100, 600, 400)  # (x, y, width, height) - region экрана
    frame_rate = 25
    samplerate = 44100  # Частота дискретизации
    channels = 2  # Кол-во каналов (стерео)

    # Запускаем запись экрана и аудио одновременно
    import threading
    audio_thread = threading.Thread(target=record_audio, args=(output_audio_filename, record_time, samplerate, channels))
    screen_thread = threading.Thread(target=record_screen, args=(output_filename, frame_rate, record_time, region_of_screen))

    audio_thread.start()
    screen_thread.start()

    audio_thread.join()
    screen_thread.join()

    print("Запись завершена")