# translator.py
from google.cloud import translate
from logger import Logger
from constants import TRANSLATION_SOURCE, TRANSLATION_TARGET, GOOGLE_PROJECT_ID


class GoogleTranslate:
    def __init__(self):
        self.logger = Logger()
        self.client = translate.TranslationServiceClient()
        # Use project ID from constants
        self.project_id = GOOGLE_PROJECT_ID
        self.location = "global"
        self.parent = f"projects/{self.project_id}/locations/{self.location}"
        self.logger.info(f"Initialized translator with project ID: {self.project_id}")

    def translate(self, text):
        if not text:
            return ""
        try:
            self.logger.debug(f"Attempting to translate text: {text}")
            response = self.client.translate_text(
                request={
                    "parent": self.parent,
                    "contents": [text],
                    "mime_type": "text/plain",
                    "source_language_code": TRANSLATION_SOURCE,
                    "target_language_code": TRANSLATION_TARGET,
                }
            )
            translated_text = response.translations[0].translated_text
            self.logger.info(f"Successfully translated: '{text}' → '{translated_text}'")
            return translated_text
        except Exception as e:
            self.logger.error(f"Translation error for text '{text}': {str(e)}")
            return f"Translation error: {text}"
