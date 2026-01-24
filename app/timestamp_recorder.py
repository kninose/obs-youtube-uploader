import time
import os
import cv2
import threading
from datetime import timedelta
from pynput import keyboard

class TimestampRecorder:
    # 初期化
    def __init__(self, obs_controller=None):
        self.recording_start_time = None
        self.timestamps = []
        self.listener = None
        self.is_recording = False
        self.templates = []
        self.masks = []
        self.game_count = 0
        self.last_detection_time = None
        self.obs_controller = obs_controller

        # スレッド管理
        self.detection_thread = None
        self.stop_detection = False
        
        # キー設定
        self.key_bindings = {
            keyboard.Key.f1: "Casual Match",
            keyboard.Key.f2: "Ranked Match",
            keyboard.Key.f3: "Custom Match"
        }

        # テンプレート画像
        self._load_templates()
    
    # テンプレート画像の読み込み
    def _load_templates(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_folder = os.path.join(project_root, "templates")
        mask_folder = os.path.join(template_folder, "masks")
  
        for i in range(2):
            template_path = os.path.join(template_folder, f"image{i}.png")
            template = cv2.imread(template_path)
            if template is not None:
                self.templates.append(template)
            
            # マスク画像を読み込み
            mask_path = os.path.join(mask_folder, f"image{i}_mask.png")
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if mask is not None:
                self.masks.append(mask)
    
    # 画面からテンプレート画像を検出
    def detect_template(self, screenshot):
        # テンプレートマッチング
        result = []
        result.append(cv2.matchTemplate(screenshot[60:1020, 0:1100], self.templates[0], cv2.TM_CCOEFF_NORMED, mask=self.masks[0]))
        result.append(cv2.matchTemplate(screenshot[900:1050, 620:1300], self.templates[1], cv2.TM_CCOEFF_NORMED, mask=self.masks[1]))

        # マッチング結果
        return max(r.max() for r in result) > 0.85
    
    # 録画開始・タイムスタンプ記録開始
    def start_recording(self):
        self.recording_start_time = time.time()
        self.timestamps = []
        self.is_recording = True
        self.last_detection_time = None
        
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()
        
        # 検出スレッド開始
        self.stop_detection = False
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()

    # 録画停止・タイムスタンプ記録停止
    def stop_recording(self):
        self.is_recording = False

        self.listener.stop()
        self.listener = None

        # 検出スレッド停止
        self.stop_detection = True
        self.detection_thread.join(timeout=2)
        self.detection_thread = None
    
    # OBSから画面を取得
    def _detection_loop(self):
        while not self.stop_detection:
            try:
                screenshot = self.obs_controller.get_screenshot()

                # テンプレート画像を検出
                if self.detect_template(screenshot):
                    current_time = time.time()
                    
                    # 前回検出から5秒以上経過している場合のみ記録
                    if self.last_detection_time is None or (current_time - self.last_detection_time) >= 5:
                        elapsed_time = time.time() - self.recording_start_time
                        self.game_count += 1
                        self.add_timestamp(elapsed_time, f"GAME{self.game_count}")

            except Exception as e:
                print(f"画面取得エラー: {e}")
            
            # 0.5秒毎に検出
            time.sleep(0.5)
    
    # キー入力時の処理
    def _on_key_press(self, key):
        if not self.is_recording:
            return
        
        if key in self.key_bindings:
            elapsed_time = time.time() - self.recording_start_time
            event_type = self.key_bindings[key]
            self.add_timestamp(elapsed_time, event_type)
    
    # タイムスタンプを追加
    def add_timestamp(self, elapsed_time, event_label):
        timestamp = {
            "time": elapsed_time,
            "label": event_label
        }
        self.timestamps.append(timestamp)
        print(f"タイムスタンプ記録: {self._format_time(elapsed_time)} - {event_label}")
    
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
            chapters.insert(0, "0:00 recording")
        
        return "\n".join(chapters)
