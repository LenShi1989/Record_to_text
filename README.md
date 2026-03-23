# Record_to_text
Python-語音轉文字


## 安裝套件
```sh
pip install openai-whisper pydub python-docx pyqt5 numba==0.56.4 llvmlite==0.39.1
```

## ffmpeg 下載網址:`https://ffmpeg.org/download.html`
1. 將資料夾放到C槽
2. 設定環境變數ex:C:\ffmpeg\bin (要執行底下的exe)
3. cmd 查看版本指令：ffmpeg -version

## 專案結構
```sh
Record_to_text/
 ├─ ffmpeg/
 │   ├─ ffmpeg.exe
 │   └─ ffprobe.exe
 ├─ Record_to_text.py
 └─ Record.ico
```

## 注意事項
打包exe檔時需加入
```sh
--collect-data whisper
```


