import mss
import mss.tools
import sounddevice as sd
import numpy as np
import time
import os
import threading
from datetime import datetime
import cv2
from scipy.io.wavfile import write as wav_write


class ScreenRecorder:
    def __init__(
            self,
            output_dir="recordings",
            framerate=30,
            duration=5,
            samplerate=44100
    ):
        self.output_dir = output_dir
        self.framerate = framerate
        self.duration = duration
        self.samplerate = samplerate
        self.is_recording = False
        self.screen_record_thread = None
        self.audio_record_thread = None

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _record_screen(self, output_file="output.mp4", fps=30, duration=10, region=None):
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

    def _record_audio(self, output_file="output.wav", duration=10, samplerate=44100, channels=2):
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

    def start_recording(self):
        if self.is_recording:
            print("Recording is already in progress.")
            return

        self.is_recording = True
        file_name_base = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name_screen = f"screen_{file_name_base}.mp4"
        file_name_audio = f"audio_{file_name_base}.wav"

        self.screen_record_thread = threading.Thread(target=self._record_screen, args=[file_name_screen])
        self.audio_record_thread = threading.Thread(target=self._record_audio, args=[file_name_audio])

        self.screen_record_thread.start()
        self.audio_record_thread.start()

        print("Recording started...")

    def stop_recording(self):
        if not self.is_recording:
            print("No recording in progress.")
            return

        self.is_recording = False
        if self.screen_record_thread:
            self.screen_record_thread.join()
        if self.audio_record_thread:
            self.audio_record_thread.join()
        print("Recording stopped.")


if __name__ == "__main__":
    recorder = ScreenRecorder()
    recorder.start_recording()
    time.sleep(10)  # Record for 10 seconds
    recorder.stop_recording()
    print("Recording saved.")
