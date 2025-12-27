import os
import customtkinter as ctk
from obs_controller import OBSController
from youtube_uploader import YouTubeUploader

class App(ctk.CTk):
    # 初期化
    def __init__(self):
        super().__init__()
        
        # ウィンドウ設定
        self.title("OBS YouTube Uploader")
        self.geometry("800x600")
        
        # カラーテーマ設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # コントローラー初期化
        self.obs = OBSController()
        self.youtube = YouTubeUploader()
        
        # UI構築
        self._create_widgets()
    
    # UI作成
    def _create_widgets(self):
        # タイトル
        self.label = ctk.CTkLabel(
            self,
            text="OBS YouTube Uploader",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.label.pack(pady=20)
        
        # OBS接続ボタン
        self.connect_button = ctk.CTkButton(
            self,
            text="OBSに接続",
            command=self.connect_obs
        )
        self.connect_button.pack(pady=10)
        
        # 録画開始ボタン
        self.record_button = ctk.CTkButton(
            self,
            text="録画開始",
            command=self.start_recording,
            state="disabled"
        )
        self.record_button.pack(pady=10)
        
        # 録画停止ボタン
        self.stop_button = ctk.CTkButton(
            self,
            text="録画停止",
            command=self.stop_recording,
            state="disabled"
        )
        self.stop_button.pack(pady=10)
        
        # アップロードボタン
        self.upload_button = ctk.CTkButton(
            self,
            text="YouTubeにアップロード",
            command=self.upload_to_youtube,
            state="disabled"
        )
        self.upload_button.pack(pady=10)
        
        # ステータス表示
        self.status_label = ctk.CTkLabel(
            self,
            text="準備完了",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=20)
    
    # イベントハンドラ
    # OBSに接続
    def connect_obs(self):
        try:
            self.obs.connect()
            self.status_label.configure(text="OBSに接続しました")
            self.record_button.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text=f"接続エラー: {e}")
    
    # 録画開始
    def start_recording(self):
        try:
            self.obs.start_recording()
            self.status_label.configure(text="録画中...")
            self.record_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text=f"録画開始エラー: {e}")
    
    # 録画停止
    def stop_recording(self):
        try:
            self.obs.stop_recording()
            self.status_label.configure(text="録画を停止しました")
            self.stop_button.configure(state="disabled")
            self.upload_button.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text=f"録画停止エラー: {e}")
    
    # YouTubeにアップロード
    def upload_to_youtube(self):
        try:
            self.status_label.configure(text="アップロード中...")
            self.update()
            # TODO: 最新の録画ファイルを取得してアップロード
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            video_path = os.path.join(project_root, "video.mp4")

            if not os.path.exists(video_path):
                raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")

            video_path = video_path = r"C:\Users\0827k\obs-uploader\video.mp4"
            self.youtube.upload(video_path, "動画タイトル", "概要欄テキスト")
            self.status_label.configure(text="アップロード完了！")
            self.upload_button.configure(state="disabled")
            self.record_button.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text=f"YouTubeアップロードエラー: {e}")
