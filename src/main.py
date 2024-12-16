import os
from audio_handler import AudioHandler
from speech_recognizer import SpeechRecognizer
from subtitle_display import SubtitleDisplay
import threading
import time


class SubtitleApp:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        credentials_path = os.path.join(project_root, "credentials.json")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        self.audio_handler = AudioHandler()
        self.speech_recognizer = SpeechRecognizer()
        self.subtitle_display = SubtitleDisplay()
        self.is_running = False
        self.last_audio_time = time.time()
        self.silence_threshold = 2  # seconds

    def start(self):
        self.is_running = True
        self.audio_handler.start_recording()
        self.speech_recognizer.start_recognition()

        processing_thread = threading.Thread(target=self._process_audio)
        transcription_thread = threading.Thread(target=self._process_transcription)

        processing_thread.start()
        transcription_thread.start()

        self.subtitle_display.start()

        self.is_running = False
        self.audio_handler.stop_recording()
        self.speech_recognizer.stop_recognition()

    def _process_audio(self):
        while self.is_running:
            audio_data = self.audio_handler.get_audio_data()
            if audio_data:
                self.last_audio_time = time.time()
                self.speech_recognizer.process_audio(audio_data)
            time.sleep(0.001)

    def _process_transcription(self):
        while self.is_running:
            transcript, is_final = self.speech_recognizer.get_transcript()
            if transcript:
                self.subtitle_display.update_subtitle(transcript, is_final)
            time.sleep(0.001)


if __name__ == "__main__":
    app = SubtitleApp()
    app.start()
