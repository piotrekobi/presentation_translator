# Real-Time Conference Subtitle System

## Core Functionality

- Real-time speech-to-text transcription of spoken audio
- Multi-language translation support (Polish, English, Ukrainian)
- Split-screen display for original + translations
- WebRTC VAD for voice activity detection
- Caching system for translation optimization

## Technical Components

### Audio Processing (`audio_handler.py`)

- Uses PyAudio for audio capture (16kHz, 16-bit)
- WebRTC VAD integration for voice detection
- Frame-based audio processing with 30ms duration
- Queue-based audio buffering system

### Speech Recognition (`speech_recognizer.py`)

- Google Cloud Speech-to-Text integration
- Streaming recognition with interim results
- Enhanced model with automatic punctuation
- Language code mapping for supported languages

### Translation System (`translator.py`)

- Google Cloud Translation integration
- Cache implementation with TTL (300s)
- Rate limiting (100ms between requests)
- Batch translation support (5 texts per batch)
- Error handling with 3 retries
- Memory optimization (max 1000 cached items)

### Display Interface (`subtitle_display.py`)

- PyQt6-based fullscreen UI
- Dynamic font size control (24-60pt)
- Black background with white/gray text
- Split display sections for each language
- Controls for adding/removing translations
- Final/interim text differentiation

### Main Application (`main.py`)

- Thread management for audio/transcription
- Google Cloud credentials handling
- Component orchestration
- Silence detection (2s threshold)

## Environment Requirements

- Python packages: google-cloud-speech, google-cloud-translate, pyaudio, webrtcvad, PyQt6
- Google Cloud credentials with Speech-to-Text and Translation API access
- Audio input device support

## Architecture Flow

1. Audio capture → Frame buffering
2. Speech recognition → Interim/final text
3. Translation requests → Cache check/update
4. UI updates → Multi-language display

## Data Flow

Audio → Frames → Recognition → Translation → Display

- Interim results shown in gray
- Final results shown in white
- Translations cached when possible
- Real-time updates with threading

## Technical Notes

- Translation rate limiting prevents API overload
- Cache system optimizes common translations
- Thread safety for shared resources
- Memory management for long sessions
