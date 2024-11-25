import webrtcvad
import collections
from logger import Logger
from constants import SAMPLE_RATE, VAD_FRAME_DURATION, VAD_PADDING, VAD_AGGRESSIVENESS

class VoiceDetector:
    def __init__(self):
        self.logger = Logger()
        self.frame_duration_ms = VAD_FRAME_DURATION
        self.frame_samples = int(SAMPLE_RATE * self.frame_duration_ms / 1000)
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        self.ring_buffer = collections.deque(maxlen=VAD_PADDING // self.frame_duration_ms)
        self.reset()

    def reset(self):
        self.voiced_frames = []
        self.triggered = False

    def process_audio(self, audio_chunk, timestamp):
        try:
            if len(audio_chunk) != self.frame_samples * 2:
                self.logger.warning(f"Invalid chunk size: {len(audio_chunk)}")
                return False
            return self.vad.is_speech(audio_chunk, SAMPLE_RATE)
        except Exception as e:
            self.logger.error(f"Error in process_audio: {str(e)}")
            return False