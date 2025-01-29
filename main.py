import mss
import mss.tools
import sounddevice as sd
import numpy as np
import time
import os
import threading
from datetime import datetime
from PIL import Image
import wave


class ScreenRecorder:
    def __init__(self, output_dir="recordings", framerate=30, duration=5, samplerate=44100):
        self.output_dir = output_dir
        self.framerate = framerate
        self.duration = duration
        self.samplerate = samplerate
        self.is_recording = False
        self.screen_record_thread = None
        self.audio_record_thread = None

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _record_screen(self, file_name_screen):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            width = monitor["width"]
            height = monitor["height"]

            frame_rate_delay = 1 / self.framerate
            output_path = os.path.join(self.output_dir, file_name_screen)
            last_time = time.time()

            with open(output_path, "wb") as output_file:
                while self.is_recording:
                    if (time.time() - last_time) > frame_rate_delay:
                        last_time = time.time()
                        sct_img = sct.grab(monitor)
                        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                        img_bytes = img.tobytes()
                        output_file.write(img_bytes)

    def _record_audio(self, file_name_audio):
        channels = 1
        audio_format = 'int16'
        output_path = os.path.join(self.output_dir, file_name_audio)
        try:
            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)
                wf.setframerate(self.samplerate)
                
                def callback(indata, frames, time, status):
                    if status:
                        print(status)
                    wf.writeframes(indata.tobytes())

                stream = sd.InputStream(samplerate=self.samplerate, channels=channels, callback=callback, dtype=audio_format)
                with stream:
                   while self.is_recording:
                     sd.sleep(100)
        except Exception as e:
              print(f"Error recording audio: {e}")
              self.is_recording = False

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
