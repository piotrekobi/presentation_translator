import os
import pyaudio
import queue
import threading
from datetime import datetime
from google.cloud import speech

from constants import CREDENTIALS_PATH, SAMPLE_RATE, CHUNK_SIZE, CHANNELS
from logger import Logger
from voice_detector import VoiceDetector
from speech_to_text import GoogleCloudSpeechToText
from translator import GoogleTranslate
from gui import TranslatorGUI


class SpeechTranslator:
    def __init__(self):
        self.logger = Logger()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

        self.is_running = False
        self.audio_thread = None
        self.audio_buffer = queue.Queue()

        self.voice_detector = VoiceDetector()
        self.speech_to_text = GoogleCloudSpeechToText()
        self.translator = GoogleTranslate()
        self.audio = pyaudio.PyAudio()

        self.gui = TranslatorGUI()
        self.gui.set_callbacks(
            self.start_translation, self.stop_translation, self.gui.clear_text
        )

    def start_translation(self):
        try:
            self.is_running = True
            self.gui.update_status("Running", "green")
            self.voice_detector.reset()
            self.audio_thread = threading.Thread(
                target=self.process_audio_stream, daemon=True
            )
            self.audio_thread.start()
            self.logger.info("Translation started")
        except Exception as e:
            self.logger.error(f"Error starting translation: {e}")
            self.gui.update_status(f"Error: {str(e)}", "red")

    def stop_translation(self):
        self.is_running = False
        self.gui.update_status("Stopped", "red")
        if self.audio_thread:
            self.audio_thread.join(timeout=1)
        self.logger.info("Translation stopped")

    def process_audio_stream(self):
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                stream_callback=self.audio_callback,
            )

            stream.start_stream()

            def audio_generator():
                speech_count = 0
                while self.is_running:
                    if not self.audio_buffer.empty():
                        chunk = self.audio_buffer.get()
                        if self.voice_detector.process_audio(chunk, datetime.now()):
                            speech_count += 1
                            if speech_count > 3:
                                yield speech.StreamingRecognizeRequest(
                                    audio_content=chunk
                                )
                        else:
                            speech_count = 0

            responses = self.speech_to_text.client.streaming_recognize(
                self.speech_to_text.streaming_config, audio_generator()
            )

            for response in responses:
                if not self.is_running:
                    break
                if not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives:
                    continue

                transcript = result.alternatives[0].transcript

                if result.is_final:
                    translation = self.translator.translate(transcript)
                    self.gui.update_final_text(transcript, translation)
                    self.gui.update_interim_text("")
                else:
                    self.gui.update_interim_text(f"Listening: {transcript}")

        except Exception as e:
            self.logger.error(f"Error in process_audio_stream: {e}")
            self.gui.update_status(f"Error: {str(e)}", "red")
        finally:
            stream.stop_stream()
            stream.close()

    def audio_callback(self, in_data, frame_count, time_info, status):
        if self.is_running:
            try:
                self.audio_buffer.put(in_data)
            except Exception as e:
                self.logger.error(f"Error in audio callback: {e}")
        return (None, pyaudio.paContinue)

    def run(self):
        self.gui.run()

    def __del__(self):
        self.audio.terminate()


def main():
    try:
        app = SpeechTranslator()
        app.run()
    except Exception as e:
        logger = Logger()
        logger.error(f"Fatal error in main: {e}")
        raise


if __name__ == "__main__":
    main()
