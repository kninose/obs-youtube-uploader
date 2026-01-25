import os
import json
import threading
import customtkinter as ctk
from datetime import datetime
from obs_controller import OBSController
from timestamp_recorder import TimestampRecorder
from youtube_uploader import YouTubeUploader

class App(ctk.CTk):
    # 初期化
    def __init__(self):
        super().__init__()
        
        # ウィンドウ設定
        self.title("OBS YouTube Uploader")
        self.geometry("550x370")
        
        # カラーテーマ設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # パス設定
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # コントローラー初期化
        self.obs = OBSController()
        self.youtube = YouTubeUploader()
        self.timestamp_recorder = TimestampRecorder(obs_controller=self.obs)

        # 動画タイトル
        self.video_title = None
        self.recording_date = None
        
        # UI構築
        self._create_widgets()
    
    # UI作成
    def _create_widgets(self):
        # タイトル
        self.label = ctk.CTkLabel(
            self,
            text="OBS YouTube Uploader",
            font=ctk.CTkFont(family="Meiryo UI", size=20, weight="bold")
        )
        self.label.pack(pady=20)
        
        # OBS接続ボタン
        self.connect_button = ctk.CTkButton(
            self,
            text="OBSに接続",
            font=ctk.CTkFont(family="Meiryo UI", size=16, weight="bold"),
            command=self.connect_obs
        )
        self.connect_button.pack(pady=10)
        
        # 録画開始ボタン
        self.record_button = ctk.CTkButton(
            self,
            text="録画開始",
            font=ctk.CTkFont(family="Meiryo UI", size=16, weight="bold"),
            command=self.start_recording,
            state="disabled"
        )
        self.record_button.pack(pady=10)
        
        # 録画停止ボタン
        self.stop_button = ctk.CTkButton(
            self,
            text="録画停止",
            font=ctk.CTkFont(family="Meiryo UI", size=16, weight="bold"),
            command=self.stop_recording,
            state="disabled"
        )
        self.stop_button.pack(pady=10)

        # アップロードボタン
        self.upload_button = ctk.CTkButton(
            self,
            text="YouTubeに投稿",
            font=ctk.CTkFont(family="Meiryo UI", size=16, weight="bold"),
            command=self.upload_to_youtube,
            state="disabled"
        )
        self.upload_button.pack(pady=10)
        
        # ステータス表示
        self.status_label = ctk.CTkLabel(
            self,
            text="準備完了",
            font=ctk.CTkFont(family="Meiryo UI", size=20, weight="bold"),
        )
        self.status_label.pack(pady=20)

    # OBSに接続
    def connect_obs(self):
        try:
            self.obs.connect()
            self.status_label.configure(text="OBSに接続しました")
            self.record_button.configure(state="normal")
            self.upload_button.configure(state="disabled")
        except Exception as e:
            print(f"接続エラー: {e}")
            self.status_label.configure(text="OBSとの接続に失敗しました\n（OBSは起動していますか？）")
    
    # 録画開始
    def start_recording(self):
        try:
            self.obs.start_recording()
            self.timestamp_recorder.start_recording()
            self.recording_date = datetime.now()
            self.status_label.configure(text="録画中... (F1-F3でタイムスタンプ追加)")
            self.record_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
        except Exception as e:
            print(f"録画開始エラー: {e}")
            self.status_label.configure(text="録画開始に失敗しました")
    
    # 録画停止
    def stop_recording(self):
        try:
            self.obs.stop_recording()
            self.timestamp_recorder.stop_recording()
            self.status_label.configure(text="録画を停止しました")
            self.stop_button.configure(state="disabled")
            self.upload_button.configure(state="normal")
        except Exception as e:
            print(f"録画停止エラー: {e}")
            self.status_label.configure(text="録画停止に失敗しました")
    
    # YouTubeにアップロード
    def upload_to_youtube(self):
        # ボタンを無効化してダブルクリックを防ぐ
        self.upload_button.configure(state="disabled")
        
        # 別スレッドでアップロード処理を実行
        upload_thread = threading.Thread(target=self._upload_worker, daemon=True)
        upload_thread.start()
    
    # アップロード処理用のサブスレッド
    def _upload_worker(self):
        try:
            # UIの更新はメインスレッドで実行
            self.after(0, lambda: self.status_label.configure(text="アップロード中..."))

            # OBSから録画ファイルパスを取得
            video_path = self.obs.recording_file
            if not video_path or not os.path.exists(video_path):
                raise FileNotFoundError("録画ファイルが見つかりません")

            # タイムスタンプレコーダーからチャプターを取得
            chapters = self.timestamp_recorder.generate_youtube_chapters()
            description = f"タイムスタンプ:\n{chapters}"

            # 動画タイトルを設定（初期値は録画開始時の日時）
            title = self.video_title or self.recording_date.strftime("%Y-%m-%d")

            # Youtubeに投稿
            self.youtube.upload(video_path, title, description)
            
            # UIの更新はメインスレッドで実行
            self.after(0, lambda: self.status_label.configure(text="アップロード完了"))
            self.after(0, lambda: self.record_button.configure(state="normal"))
        except Exception as e:
            print(f"アップロードエラー: {e}")
            # UIの更新はメインスレッドで実行
            self.after(0, lambda: self.status_label.configure(text="YouTubeへの投稿に失敗しました"))
            self.after(0, lambda: self.upload_button.configure(state="normal"))
