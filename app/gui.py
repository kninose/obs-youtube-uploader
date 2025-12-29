import os
import customtkinter as ctk
from obs_controller import OBSController
from timestamp_recorder import TimestampRecorder
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
        self.timestamp_recorder = TimestampRecorder()
        
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
        
        # タイムスタンプ表示エリア
        self.timestamp_label = ctk.CTkLabel(
            self,
            text="タイムスタンプ (F1:試合開始 F2:試合終了 F3:ハイライト)",
            font=ctk.CTkFont(size=12)
        )
        self.timestamp_label.pack(pady=10)
        
        self.timestamp_textbox = ctk.CTkTextbox(
            self,
            width=700,
            height=150
        )
        self.timestamp_textbox.pack(pady=10)

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
            self.timestamp_recorder.start_recording()
            self.timestamp_textbox.delete("1.0", "end")
            self.status_label.configure(text="録画中... (F1-F3でタイムスタンプ追加)")
            self.record_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text=f"録画開始エラー: {e}")
    
    # 録画停止
    def stop_recording(self):
        try:
            self.obs.stop_recording()
            self.timestamp_recorder.stop_recording()

            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            video_folder = os.path.join(project_root, "video")

            try:
                moved_path = self.obs.move_recording_to_folder(video_folder)
            except Exception as e:
                print(f"ファイル移動エラー: {e}")

            chapters = self.timestamp_recorder.generate_youtube_chapters()
            self.timestamp_textbox.delete("1.0", "end")
            self.timestamp_textbox.insert("1.0", chapters)

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

            chapters = self.timestamp_textbox.get("1.0", "end").strip()
            description = f"ゲームプレイ動画\n\nチャプター:\n{chapters}" if chapters else "概要欄テキスト"

            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            video_folder = os.path.join(project_root, "video")

            if not os.path.exists(video_folder):
                raise FileNotFoundError(f"videoフォルダが見つかりません: {video_folder}")

            video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]
            
            if not video_files:
                raise FileNotFoundError(f"videoフォルダに動画ファイルが見つかりません: {video_folder}")
            
            video_files_path = [os.path.join(video_folder, f) for f in video_files]
            latest_video = max(video_files_path, key=os.path.getmtime)

            self.youtube.upload(latest_video, "動画タイトル", description)
            self.status_label.configure(text="アップロード完了！")
            self.upload_button.configure(state="disabled")
            self.record_button.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text=f"YouTubeアップロードエラー: {e}")
