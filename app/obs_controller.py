import os
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
        self.ws.call(requests.StopRecord())
