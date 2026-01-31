import cv2
import os
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
