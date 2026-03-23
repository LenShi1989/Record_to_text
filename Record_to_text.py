import os
import sys
import ctypes
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QProgressBar
)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from pydub import AudioSegment
import whisper
from docx import Document


# 🔥 這行是關鍵（Taskbar icon）
myappid = "JQuan.com.tw"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.abspath(".")


def get_ffmpeg_path():
    return os.path.join(get_base_path(), "ffmpeg", "ffmpeg.exe")


def get_ffprobe_path():
    return os.path.join(get_base_path(), "ffmpeg", "ffprobe.exe")


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


AudioSegment.converter = get_ffmpeg_path()
AudioSegment.ffmpeg = get_ffmpeg_path()
AudioSegment.ffprobe = get_ffprobe_path()


class TranscribeThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)

    def __init__(self, file_path, model_name="base"):
        super().__init__()
        self.file_path = file_path
        self.model_name = model_name

    def run(self):
        try:
            self.progress.emit(10)
            file_path = Path(self.file_path)
            wav_file = file_path.with_suffix(".wav")

            # 轉換成 wav
            sound = AudioSegment.from_file(file_path)
            sound = sound.set_frame_rate(16000).set_channels(1)
            sound.export(wav_file, format="wav")

            self.progress.emit(30)

            # 語音辨識
            model = whisper.load_model(self.model_name)
            result = model.transcribe(str(wav_file), language="zh")

            text = result["text"]
            self.progress.emit(70)

            # 生成大綱
            sentences = [
                s.strip() for s in text.replace("，", "，\n").replace("。", "。\n").split("\n") if s.strip()
            ]
            outline = "\n".join(
                [f"{i+1}. {s}" for i, s in enumerate(sentences)])

            self.progress.emit(100)
            self.finished.emit(text, outline)

        except Exception as e:
            self.finished.emit(f"(錯誤: {e})", "")


class SpeechToTextApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("語音轉文字工具")
        self.setGeometry(300, 200, 600, 550)

        layout = QVBoxLayout()

        self.label = QLabel("請選擇一個音檔 (m4a/wav)")
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        self.btn_open = QPushButton("選擇音檔")
        self.btn_open.clicked.connect(self.open_file)
        layout.addWidget(self.btn_open)

        self.btn_transcribe = QPushButton("開始轉換")
        self.btn_transcribe.clicked.connect(self.transcribe_audio)
        self.btn_transcribe.setEnabled(False)
        layout.addWidget(self.btn_transcribe)

        self.btn_export = QPushButton("匯出 Word 檔")
        self.btn_export.clicked.connect(self.export_word)
        self.btn_export.setEnabled(False)
        layout.addWidget(self.btn_export)

        self.setLayout(layout)

        self.audio_file = None
        self.transcript_text = ""
        self.outline_text = ""

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選擇音檔", "", "音訊檔 (*.m4a *.wav)")
        if file_path:
            self.audio_file = file_path
            self.label.setText(f"已選擇檔案：{Path(file_path).name}")
            self.btn_transcribe.setEnabled(True)

    def transcribe_audio(self):
        if not self.audio_file:
            self.text_area.setText("請先選擇檔案")
            return

        self.text_area.setText("轉換中，請稍候...")
        self.progress_bar.setValue(0)
        self.btn_transcribe.setEnabled(False)
        self.btn_export.setEnabled(False)

        # 背景執行
        self.thread = TranscribeThread(self.audio_file, "base")
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_transcription_finished)
        self.thread.start()

    def on_transcription_finished(self, text, outline):
        self.transcript_text = text
        self.outline_text = outline
        self.text_area.setText(
            f"==== 語音轉文字 ====\n{text}\n\n==== 內容大綱 ====\n{outline}"
        )
        self.btn_transcribe.setEnabled(True)
        if text and not text.startswith("(錯誤"):
            self.btn_export.setEnabled(True)

    def export_word(self):
        if not self.transcript_text:
            self.text_area.setText("沒有可匯出的內容")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "儲存 Word 檔", "轉換結果.docx", "Word 檔 (*.docx)")
        if not save_path:
            return

        doc = Document()
        doc.add_heading("語音轉文字結果", level=1)

        doc.add_heading("完整文字稿", level=2)
        doc.add_paragraph(self.transcript_text)

        doc.add_heading("內容大綱", level=2)
        for line in self.outline_text.split("\n"):
            doc.add_paragraph(line)

        doc.save(save_path)
        self.text_area.append(f"\n✅ 已匯出 Word 檔：{save_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = resource_path("Record.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = SpeechToTextApp()
    window.setWindowIcon(QIcon(icon_path))
    window.show()
    sys.exit(app.exec_())
