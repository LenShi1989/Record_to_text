# Python-語音轉文字

## 專案目標
- 語音檔（.wav/.m4a） → 中文文字稿 + 大綱
- 高準確辨識（faster-whisper medium / large-v3 + beam search）
- PyQt5 GUI
- 可匯出 Word 檔
- 支援 CPU/GPU，可選 VAD
- 可打包成 EXE（可選）

## 安裝套件

| 套件                 | 版本建議   | 功能                      |
| ------------------ | ------ | ----------------------- |
| PyQt5              | 最新     | GUI                     |
| pydub              | 最新     | 音訊轉 wav                 |
| faster-whisper     | 最新     | 語音辨識核心                  |
| ctranslate2        | 最新     | faster-whisper CPU 推理加速 |
| docx / python-docx | 最新     | 匯出 Word                 |
| onnxruntime        | 最新（可選） | VAD 過濾靜音（非必須）           |
| ffmpeg             | 外部可執行檔 | 音訊轉換                    |

安裝方式
```sh
pip install PyQt5 pydub python-docx faster-whisper ctranslate2 onnxruntime
```

⚡ GPU 版本：
```sh
pip install onnxruntime-gpu
```

外部依賴：
- ffmpeg.exe（放在專案 ffmpeg/ffmpeg.exe，程式中已指定路徑）
  - ffmpeg 官方下載：https://ffmpeg.org/download.html

## ffmpeg 下載網址:`https://ffmpeg.org/download.html`

## 專案結構
建議架構如下：
```sh
Record_to_text/
│
├─ Record_to_text.py           # 主程式 (你的 PyQt5 GUI + faster-whisper)
├─ Record.ico                  # GUI icon
├─ ffmpeg/
│   ├─ ffmpeg.exe              # ffmpeg 執行檔
│   └─ ffprobe.exe             # ffprobe 執行檔
├─ models/                     # faster-whisper 下載模型存放目錄（可選）
├─ audio/                      # 測試音檔資料夾（可選）
└─ output/                     # 匯出 Word 檔資料夾（可選）
```

## 專案程式結構概述
```sh
Record_to_text.py
│
├─ PyQt5 GUI
│   ├─ QLabel : 顯示選檔
│   ├─ QProgressBar : 顯示轉換進度
│   ├─ QTextEdit : 顯示文字稿 & 大綱
│   ├─ QPushButton : 選擇音檔 / 開始轉換 / 匯出 Word
│
├─ 音訊處理
│   ├─ pydub : 轉 wav + 設定 16kHz 單聲道
│   └─ ffmpeg : 轉檔
│
├─ 語音辨識
│   ├─ faster-whisper : medium / large-v3
│   ├─ beam_size=5
│   ├─ language="zh"
│   └─ vad_filter=True / False
│
├─ 背景執行
│   └─ QThread : 轉換不阻塞 GUI
│
└─ 匯出 Word
    └─ python-docx : 文字稿 + 大綱
```

## 注意事項

### 1. VAD 過濾
- 需要 onnxruntime
- 若不想裝，可設 vad_filter=False，程式仍能正常運行

### 2. 模型大小
- medium → 準確 + 速度平衡
- large-v3 → 準確最佳，但 CPU 慢

### 3. EXE 打包
- 建議用 PyInstaller
- 如果使用 VAD，需要加入 --hidden-import=onnxruntime
- ffmpeg 可直接放專案內，不用安裝全域

### 4. 外部資源
- ffmpeg、ffprobe 必須存在，程式會自動設定路徑
- icon 可自行換，保存在專案根目錄


