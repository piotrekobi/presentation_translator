import tkinter as tk
from logger import Logger


class TranslatorGUI:
    def __init__(self):
        self.logger = Logger()
        self.root = tk.Tk()
        self.root.title("Polish to English Speech Translator")
        self._setup_gui()

    def _setup_gui(self):
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(expand=True, fill="both")

        self.status_label = tk.Label(main_frame, text="Status: Stopped", fg="red")
        self.status_label.pack(anchor="w", pady=5)

        tk.Label(main_frame, text="Polski tekst:").pack(anchor="w")
        self.original_text = tk.Text(main_frame, height=5, wrap=tk.WORD)
        self.original_text.pack(fill="x", pady=5)

        self.interim_label = tk.Label(main_frame, text="", fg="gray")
        self.interim_label.pack(anchor="w", fill="x")

        tk.Label(main_frame, text="English translation:").pack(anchor="w")
        self.translated_text = tk.Text(main_frame, height=5, wrap=tk.WORD)
        self.translated_text.pack(fill="x", pady=5)

        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        self.start_button = tk.Button(button_frame, text="Start Translation")
        self.start_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear")
        self.clear_button.pack(side="left", padx=5)

    def set_callbacks(self, start_cb, stop_cb, clear_cb):
        self.start_button.config(command=lambda: self._handle_toggle(start_cb, stop_cb))
        self.clear_button.config(command=clear_cb)

    def _handle_toggle(self, start_cb, stop_cb):
        if self.start_button["text"] == "Start Translation":
            self.start_button.config(text="Stop Translation")
            start_cb()
        else:
            self.start_button.config(text="Start Translation")
            stop_cb()

    def update_status(self, status, color="black"):
        self.status_label.config(text=f"Status: {status}", fg=color)

    def update_interim_text(self, text):
        self.interim_label.config(text=text)

    def update_final_text(self, original_text, translated_text):
        self.original_text.insert(tk.END, original_text + "\n")
        self.original_text.see(tk.END)
        self.translated_text.insert(tk.END, translated_text + "\n")
        self.translated_text.see(tk.END)

    def clear_text(self):
        self.original_text.delete(1.0, tk.END)
        self.translated_text.delete(1.0, tk.END)
        self.interim_label.config(text="")

    def run(self):
        self.root.mainloop()
