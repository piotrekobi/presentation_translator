from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QSplitter,
    QComboBox,
    QLabel,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QPalette, QColor, QTextCharFormat, QTextCursor
import sys
from translator import Translator


class SubtitleWorker(QObject):
    update_signal = pyqtSignal(str, bool)


class SubtitleDisplay:
    def __init__(self):
        self.transcript = []
        self.translator = Translator()
        self.current_interim_text = ""
        self.full_final_text = ""
        self.translations = {}  # {language_code: (final_text, interim_text)}

        self.language_codes = {
            "Polish": "pl",
            "English": "en",
            "German": "de",
            "Russian": "ru",
            "Ukrainian": "uk",
        }

        self.final_format = QTextCharFormat()
        self.final_format.setForeground(QColor("white"))

        self.interim_format = QTextCharFormat()
        self.interim_format.setForeground(QColor("gray"))

        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle("Conference Live Subtitles")
        self.window.showFullScreen()

        self.central_widget = QWidget()
        self.window.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.create_controls()
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_layout.addWidget(self.splitter)

        self.text_displays = []
        self.worker = SubtitleWorker()
        self.worker.update_signal.connect(self._update_display)

        # Create initial transcription section
        self.create_transcription_section()

    def create_controls(self):
        self.controls_layout = QHBoxLayout()

        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet(
            "background-color: red; color: white; font-size: 12px;"
        )
        self.exit_button.setFixedSize(50, 30)
        self.exit_button.clicked.connect(self.app.quit)
        self.controls_layout.addWidget(self.exit_button)

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet(
            "background-color: orange; color: white; font-size: 12px;"
        )
        self.clear_button.setFixedSize(50, 30)
        self.clear_button.clicked.connect(self.clear_all)
        self.controls_layout.addWidget(self.clear_button)

        # Font size control
        self.controls_layout.addWidget(QLabel("Font Size:"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(
            ["24", "28", "32", "36", "40", "44", "48", "52", "56", "60"]
        )
        self.font_size_combo.setCurrentText("36")
        self.font_size_combo.currentTextChanged.connect(self.update_font_size)
        self.controls_layout.addWidget(self.font_size_combo)

        # Transcription language control
        self.controls_layout.addWidget(QLabel("Transcription Language:"))
        self.transcription_language = QComboBox()
        self.transcription_language.addItems(self.language_codes.keys())
        self.transcription_language.setCurrentText("Polish")
        self.transcription_language.currentTextChanged.connect(
            self.update_transcription_language
        )
        self.controls_layout.addWidget(self.transcription_language)

        # Add translation section controls
        self.controls_layout.addWidget(QLabel("Add Translation:"))
        self.add_language_combo = QComboBox()
        self.add_language_combo.addItems(self.language_codes.keys())
        self.add_language_combo.setCurrentText("English")
        self.controls_layout.addWidget(self.add_language_combo)

        self.add_section_button = QPushButton("Add Translation")
        self.add_section_button.clicked.connect(self.add_translation_section)
        self.controls_layout.addWidget(self.add_section_button)

        # Remove section button
        self.remove_section_button = QPushButton("Remove Translation")
        self.remove_section_button.clicked.connect(self.remove_section)
        self.controls_layout.addWidget(self.remove_section_button)

        self.controls_layout.addStretch()
        self.main_layout.addLayout(self.controls_layout)

    def create_transcription_section(self):
        text_display = QTextEdit()
        text_display.setReadOnly(True)
        text_display.setFont(
            QFont("Arial", int(self.font_size_combo.currentText()), QFont.Weight.Bold)
        )

        palette = text_display.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("black"))
        palette.setColor(QPalette.ColorRole.Text, QColor("white"))
        text_display.setPalette(palette)

        self.splitter.addWidget(text_display)
        self.text_displays.append(
            {"display": text_display, "language": "transcription"}
        )
        self.update_remove_button_state()

    def add_translation_section(self):
        selected_language = self.add_language_combo.currentText()
        language_code = self.language_codes[selected_language]

        # Check if this language already has a translation section
        if any(display["language"] == language_code for display in self.text_displays):
            return

        text_display = QTextEdit()
        text_display.setReadOnly(True)
        text_display.setFont(
            QFont("Arial", int(self.font_size_combo.currentText()), QFont.Weight.Bold)
        )

        palette = text_display.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("black"))
        palette.setColor(QPalette.ColorRole.Text, QColor("white"))
        text_display.setPalette(palette)

        self.splitter.addWidget(text_display)
        self.text_displays.append({"display": text_display, "language": language_code})
        self.translations[language_code] = ("", "")
        self.update_remove_button_state()
        self._refresh_display()

    def remove_section(self):
        if len(self.text_displays) > 1:
            removed_section = self.text_displays.pop()
            removed_section["display"].setParent(None)
            removed_section["display"].deleteLater()
            if removed_section["language"] in self.translations:
                del self.translations[removed_section["language"]]
        self.update_remove_button_state()

    def update_remove_button_state(self):
        self.remove_section_button.setEnabled(len(self.text_displays) > 1)
        self.remove_section_button.setStyleSheet(
            "background-color: gray; color: white;"
            if len(self.text_displays) <= 1
            else "background-color: red; color: white;"
        )

    def clear_all(self):
        self.full_final_text = ""
        self.current_interim_text = ""
        self.translations.clear()
        self._refresh_display()

    def update_font_size(self, size):
        for section in self.text_displays:
            font = section["display"].font()
            font.setPointSize(int(size))
            section["display"].setFont(font)

    def update_transcription_language(self, language):
        self._refresh_display()

    def update_subtitle(self, text, is_final):
        self.worker.update_signal.emit(text, is_final)

    def _refresh_display(self):
        source_lang = self.language_codes[self.transcription_language.currentText()]

        # Update transcription display
        transcription_display = next(
            section["display"]
            for section in self.text_displays
            if section["language"] == "transcription"
        )
        transcription_display.clear()
        cursor = transcription_display.textCursor()
        cursor.insertText(self.full_final_text, self.final_format)
        if self.current_interim_text:
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(
                (
                    " " + self.current_interim_text
                    if self.full_final_text
                    else self.current_interim_text
                ),
                self.interim_format,
            )

        # Update translation displays
        for section in self.text_displays:
            if section["language"] == "transcription":
                continue

            target_lang = section["language"]
            display = section["display"]
            display.clear()
            cursor = display.textCursor()

            # Translate final text
            if self.full_final_text:
                translated_final = self.translator.translate(
                    self.full_final_text, source_lang, target_lang, True
                )
                cursor.insertText(translated_final, self.final_format)

            # Translate interim text
            if self.current_interim_text:
                translated_interim = self.translator.translate(
                    self.current_interim_text, source_lang, target_lang, False
                )
                cursor.movePosition(QTextCursor.MoveOperation.End)
                if translated_interim:
                    cursor.insertText(
                        (
                            " " + translated_interim
                            if self.full_final_text
                            else translated_interim
                        ),
                        self.interim_format,
                    )

            # Scroll to bottom
            scrollbar = display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _update_display(self, text, is_final):
        if is_final:
            if self.full_final_text:
                self.full_final_text += " " + text
            else:
                self.full_final_text = text
            self.current_interim_text = ""
        else:
            self.current_interim_text = text

        self._refresh_display()

    def start(self):
        self.window.show()
        self.app.exec()

    def stop(self):
        self.app.quit()
