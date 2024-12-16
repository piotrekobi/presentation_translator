from google.cloud import speech
from google.cloud import translate
import queue
import threading


class SpeechRecognizer:
    def __init__(self, language_code="pl-PL"):
        self.client = speech.SpeechClient()
        self.translate_client = translate.TranslationServiceClient()
        self.project_id = "presentationtranslator"
        self.location = "global"
        self.parent = f"projects/{self.project_id}/locations/{self.location}"
        self.language_codes = {
            "pl": "pl-PL",
            "en": "en-US",
            "de": "de-DE",
            "ru": "ru-RU",
            "uk": "uk-UA",
        }
        self.language_code = self.language_codes.get(language_code, language_code)
        self.update_config()
        self.responses_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        self.is_running = False

    def update_config(self):
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=self.language_code,
            enable_automatic_punctuation=True,
            use_enhanced=True,
            model="latest_long",
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config, interim_results=True
        )

    def set_language(self, language_code):
        self.language_code = self.language_codes.get(language_code, language_code)
        self.update_config()

    def start_recognition(self):
        self.is_running = True
        self.recognition_thread = threading.Thread(target=self._run_recognition)
        self.recognition_thread.start()

    def stop_recognition(self):
        self.is_running = False
        if hasattr(self, "recognition_thread"):
            self.recognition_thread.join()

    def process_audio(self, audio_data):
        self.audio_queue.put(audio_data)

    def _run_recognition(self):
        while self.is_running:

            def audio_generator():
                while self.is_running:
                    if not self.audio_queue.empty():
                        data = self.audio_queue.get()
                        yield speech.StreamingRecognizeRequest(audio_content=data)

            try:
                requests = audio_generator()
                responses = self.client.streaming_recognize(
                    self.streaming_config, requests
                )

                for response in responses:
                    if not response.results:
                        continue

                    result = response.results[0]
                    if not result.alternatives:
                        continue

                    transcript = result.alternatives[0].transcript
                    is_final = result.is_final

                    self.responses_queue.put((transcript, is_final))

            except Exception as e:
                print(f"Error in recognition: {e}")
                continue

    def get_transcript(self):
        if not self.responses_queue.empty():
            return self.responses_queue.get()
        return None, False
