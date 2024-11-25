from googletrans import Translator
from logger import Logger
from constants import TRANSLATION_SOURCE, TRANSLATION_TARGET

class GoogleTranslate:
    def __init__(self):
        self.logger = Logger()
        self.translator = Translator()

    def translate(self, text):
        if not text:
            return ""
        try:
            translation = self.translator.translate(
                text, 
                src=TRANSLATION_SOURCE, 
                dest=TRANSLATION_TARGET
            )
            return translation.text
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return f"Translation error: {text}"