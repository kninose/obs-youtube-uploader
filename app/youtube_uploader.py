import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

class YouTubeUploader:
    # 初期化
    def __init__(self):
        self.credentials = None
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.token_path = os.path.join(self.project_root, "token.pickle")
        self.client_secrets_path = os.path.join(self.project_root, "client_secrets.json")
        
        # client_secrets.jsonがある場合のみ認証
        if os.path.exists(self.client_secrets_path):
            self._authenticate()
    
    # 認証処理
    def _authenticate(self):
        if os.path.exists(self.token_path):
            with open(self.token_path, "rb") as token:
                self.credentials = pickle.load(token)
        
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_path, SCOPES)
                self.credentials = flow.run_local_server(port=0)
            with open(self.token_path, "wb") as token:
                pickle.dump(self.credentials, token)
    
    # アップロード処理
    def upload(self, video_file, title, description):
        if not self.credentials:
            raise Exception("YouTube認証が完了していません．client_secrets.jsonを配置してください．")
        
        youtube = build("youtube", "v3", credentials=self.credentials)
        
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "20"  # Gaming
            },
            "status": {
                "privacyStatus": "private"  # private, unlisted, public
            }
        }
        
        media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = request.execute()
        return response     # YouTubeから返されるレスポンス（動画ID等が含まれる）       
