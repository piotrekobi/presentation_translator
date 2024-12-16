from google.cloud import translate
import json
import os
from typing import Dict, Optional, Tuple
from threading import Lock
import time


class Translator:
    def __init__(self):
        self.client = translate.TranslationServiceClient()
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        with open(credentials_path) as f:
            project_id = json.load(f)["project_id"]

        self.parent = f"projects/{project_id}/locations/global"
        self.translation_cache: Dict[str, Tuple[str, float]] = {}
        self.cache_lock = Lock()
        self.cache_ttl = 300  # 5 minutes
        self.max_cache_size = 1000

        self.supported_languages = {
            "pl": "Polish",
            "en": "English",
            "de": "German",
            "ru": "Russian",
            "uk": "Ukrainian",
        }

        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests to avoid rate limiting

        self.retries = 3
        self.retry_delay = 1.0

        self.batch_size = 5
        self.pending_translations = {}
        self.last_interim_texts = {}

    def get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        return f"{source_lang}:{target_lang}:{text}"

    def clean_cache(self) -> None:
        with self.cache_lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, (_, timestamp) in self.translation_cache.items()
                if current_time - timestamp > self.cache_ttl
            ]
            for key in expired_keys:
                del self.translation_cache[key]

            if len(self.translation_cache) > self.max_cache_size:
                items = sorted(
                    self.translation_cache.items(), key=lambda x: x[1][1]
                )  # Sort by timestamp
                self.translation_cache = dict(items[-self.max_cache_size :])

    def get_from_cache(self, cache_key: str) -> Optional[str]:
        with self.cache_lock:
            if cache_key in self.translation_cache:
                text, timestamp = self.translation_cache[cache_key]
                if time.time() - timestamp <= self.cache_ttl:
                    return text
                del self.translation_cache[cache_key]
        return None

    def add_to_cache(self, cache_key: str, translated_text: str) -> None:
        with self.cache_lock:
            self.translation_cache[cache_key] = (translated_text, time.time())

        if len(self.translation_cache) > self.max_cache_size:
            self.clean_cache()

    def rate_limit(self) -> None:
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def is_valid_language(self, lang_code: str) -> bool:
        return lang_code in self.supported_languages

    def get_language_name(self, lang_code: str) -> str:
        return self.supported_languages.get(lang_code, lang_code)

    def translate_with_retries(
        self, text: str, source_lang: str, target_lang: str
    ) -> Optional[str]:
        for attempt in range(self.retries):
            try:
                self.rate_limit()

                response = self.client.translate_text(
                    request={
                        "parent": self.parent,
                        "contents": [text],
                        "mime_type": "text/plain",
                        "source_language_code": source_lang,
                        "target_language_code": target_lang,
                    }
                )

                if response.translations:
                    return response.translations[0].translated_text

            except Exception as e:
                if attempt == self.retries - 1:
                    print(f"Translation error after {self.retries} attempts: {e}")
                    return None
                time.sleep(self.retry_delay * (attempt + 1))

        return None

    def translate(
        self, text: str, source_lang: str, target_lang: str, is_final: bool = False
    ) -> str:
        if not text or source_lang == target_lang:
            return text

        if not self.is_valid_language(source_lang) or not self.is_valid_language(
            target_lang
        ):
            return text

        # Handle interim text consistency
        if not is_final:
            section_key = f"{source_lang}:{target_lang}"
            if text == self.last_interim_texts.get(section_key):
                return self.pending_translations.get(section_key, text)
            self.last_interim_texts[section_key] = text

        cache_key = self.get_cache_key(text, source_lang, target_lang)

        # Check cache for non-final translations
        if not is_final:
            cached_translation = self.get_from_cache(cache_key)
            if cached_translation is not None:
                if not is_final:
                    self.pending_translations[f"{source_lang}:{target_lang}"] = (
                        cached_translation
                    )
                return cached_translation

        # Perform translation
        translated_text = self.translate_with_retries(text, source_lang, target_lang)

        if translated_text is None:
            return text

        # Cache successful translations
        if not is_final:
            self.add_to_cache(cache_key, translated_text)
            self.pending_translations[f"{source_lang}:{target_lang}"] = translated_text

        return translated_text

    def batch_translate(self, texts: list, source_lang: str, target_lang: str) -> list:
        if not texts:
            return []

        if not self.is_valid_language(source_lang) or not self.is_valid_language(
            target_lang
        ):
            return texts

        translated_texts = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]

            try:
                self.rate_limit()

                response = self.client.translate_text(
                    request={
                        "parent": self.parent,
                        "contents": batch,
                        "mime_type": "text/plain",
                        "source_language_code": source_lang,
                        "target_language_code": target_lang,
                    }
                )

                translated_texts.extend(
                    [t.translated_text for t in response.translations]
                )

            except Exception as e:
                print(f"Batch translation error: {e}")
                translated_texts.extend(batch)  # Fall back to original text

        return translated_texts

    def clear_cache(self) -> None:
        with self.cache_lock:
            self.translation_cache.clear()
            self.pending_translations.clear()
            self.last_interim_texts.clear()

    def update_cache_settings(self, ttl: int = None, max_size: int = None) -> None:
        if ttl is not None:
            self.cache_ttl = ttl
        if max_size is not None:
            self.max_cache_size = max_size
        self.clean_cache()
