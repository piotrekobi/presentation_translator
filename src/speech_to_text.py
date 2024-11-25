from google.cloud import speech
from logger import Logger
from constants import SAMPLE_RATE, SPEECH_LANGUAGE

class GoogleCloudSpeechToText:
    def __init__(self):
        self.logger = Logger()
        self.client = speech.SpeechClient()
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code=SPEECH_LANGUAGE,
            enable_automatic_punctuation=True,
            model="latest_long",
            use_enhanced=True,
            enable_spoken_punctuation=True
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config,
            interim_results=True
        )