import base64
import cv2
import numpy as np
import os
import shutil
import time
from obswebsocket import obsws, requests
from dotenv import load_dotenv

load_dotenv()

class OBSController:
    # 初期化
    def __init__(self):
        self.host = os.getenv("OBS_HOST", "localhost")
        self.port = int(os.getenv("OBS_PORT", 4455))
        self.password = os.getenv("OBS_PASSWORD", "")
        self.ws = None
        self.recording_file = None
    
    # 接続
    def connect(self):
        self.ws = obsws(self.host, self.port, self.password)
        self.ws.connect()
    
    # 切断
    def disconnect(self):
        if self.ws:
            self.ws.disconnect()
    
    # 録画開始
    def start_recording(self):
        self.ws.call(requests.StartRecord())
    
    # 録画停止
    def stop_recording(self):
        response = self.ws.call(requests.StopRecord())

        if hasattr(response, "datain") and "outputPath" in response.datain:
            self.recording_file = response.datain["outputPath"]
    
    # 画面キャプチャを取得
    def get_screenshot(self):
        try:
            temp_path = os.path.abspath("temp_screenshot.png")
            
            # シーンのリストを取得
            scenes_response = self.ws.call(requests.GetSceneList())
            current_scene = scenes_response.datain.get("currentProgramSceneName") or scenes_response.datain.get("currentSceneName")
            
            # シーンのスクリーンショットを取得
            response = self.ws.call(requests.SaveSourceScreenshot(
                sourceName=current_scene,  # シーン名を指定
                imageFormat="png",
                imageFilePath=temp_path,
                imageWidth=1920,
                imageHeight=1080
            ))
            
            # ファイル書き込み完了を待つ
            for i in range(10):
                if os.path.exists(temp_path):
                    break
                time.sleep(0.1)
            
            if not os.path.exists(temp_path):
                raise Exception(f"スクリーンショットファイルの作成に失敗しました: {temp_path}")
            
            # ファイルを読み込み
            img = cv2.imread(temp_path)
            
            if img is None:
                raise Exception("スクリーンショットの読み込みに失敗しました")
            
            # 一時ファイルを削除
            os.remove(temp_path)
            
            return img
            
        except Exception as e:
            print(f"エラー: {e}")
            raise

    # 録画ファイルを指定フォルダに移動
    def move_recording_to_folder(self, destination_folder):
        if not self.recording_file:
            raise Exception("録画ファイルが見つかりません")
        
        if not os.path.exists(self.recording_file):
            raise FileNotFoundError(f"録画ファイルが存在しません: {self.recording_file}")
        
        # OBSがファイルを開放するまで待機
        time.sleep(1)
        max_retries = 10
        for i in range(max_retries):
            try:
                if not os.path.exists(self.recording_file):
                    raise FileNotFoundError(f"録画ファイルが存在しません: {self.recording_file}")
                
                # 移動先フォルダを作成
                os.makedirs(destination_folder, exist_ok=True)
                
                # ファイル名を取得
                filename = os.path.basename(self.recording_file)
                destination_path = os.path.join(destination_folder, filename)
                
                # ファイルを移動
                shutil.move(self.recording_file, destination_path)  # ファイル名を自動で変更させないため，第2引数にフルパスを指定する
                self.recording_file = destination_path        
                break
            
            except PermissionError as e:
                if i < max_retries - 1:
                    print(f"ファイルがロック中です．1秒後に再試行... ({i + 1}/{max_retries})")
                    time.sleep(1)
                else:
                    raise Exception(f"ファイル移動に失敗しました．OBSがファイルを使用中の可能性があります: {e}")
