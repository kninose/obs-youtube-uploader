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

    # TODO: 任意のフォルダに保存
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
