import pyaudio
import webrtcvad
import array
import queue
from threading import Thread


class AudioHandler:
    def __init__(self, sample_rate=16000, frame_duration=30):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.vad = webrtcvad.Vad(1)
        self.audio = pyaudio.PyAudio()
        self.frames_queue = queue.Queue()
        self.is_recording = False
        self.buffer_size = 5

    def start_recording(self):
        self.is_recording = True
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=int(self.sample_rate * self.frame_duration / 1000),
            stream_callback=self._audio_callback,
        )
        self.stream.start_stream()

    def stop_recording(self):
        self.is_recording = False
        if hasattr(self, "stream"):
            self.stream.stop_stream()
            self.stream.close()

    def _audio_callback(self, in_data, frame_count, time_info, status):
        if self.is_recording:
            self.frames_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def get_audio_data(self):
        if not self.frames_queue.empty():
            return self.frames_queue.get()
        return None

    def __del__(self):
        self.stop_recording()
        self.audio.terminate()
