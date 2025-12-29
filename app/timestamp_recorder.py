import time
from datetime import timedelta
from pynput import keyboard

class TimestampRecorder:
    # 初期化
    def __init__(self):
        self.recording_start_time = None
        self.timestamps = []
        self.listener = None
        self.is_recording = False
        
        # キー設定
        self.key_bindings = {
            keyboard.Key.f1: "match_start",
            keyboard.Key.f2: "match_end",
            keyboard.Key.f3: "break_time",
        }
    
    # 録画開始・タイムスタンプ記録開始
    def start_recording(self):
        self.recording_start_time = time.time()
        self.timestamps = []
        self.is_recording = True
        
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()

    # 録画停止・タイムスタンプ記録停止
    def stop_recording(self):
        self.is_recording = False
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    # キー入力時の処理
    def _on_key_press(self, key):
        if not self.is_recording:
            return
        
        if key in self.key_bindings:
            elapsed_time = time.time() - self.recording_start_time
            event_type = self.key_bindings[key]
            self.add_timestamp(elapsed_time, event_type)
    
    # タイムスタンプを追加
    def add_timestamp(self, elapsed_seconds, event_label):
        timestamp = {
            "time": elapsed_seconds,
            "label": event_label
        }
        self.timestamps.append(timestamp)
        print(f"タイムスタンプ記録: {self._format_time(elapsed_seconds)} - {event_label}")
    
    # 秒数を 0:00 形式に変換
    def _format_time(self, seconds):
        td = timedelta(seconds=int(seconds))
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        secs = td.seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    # YouTube用チャプター文字列を生成
    def generate_youtube_chapters(self):
        if not self.timestamps:
            return ""
        
        # チャプター形式に変換
        chapters = []
        for ts in self.timestamps:
            time_str = self._format_time(ts["time"])
            label = ts["label"]
            chapters.append(f"{time_str} {label}")
        
        # 最初に0:00を追加（YouTubeの要件）
        if not chapters or not chapters[0].startswith("0:00"):
            chapters.insert(0, "0:00 開始")
        
        return "\n".join(chapters)
