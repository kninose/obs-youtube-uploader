import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube"]

class YouTubeUploader:
    # 初期化
    def __init__(self):
        self.credentials = None
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.token_path = os.path.join(self.project_root, "token.pickle")
        self.client_secrets_path = os.path.join(self.project_root, "client_secrets.json")
        self.playlist_id = os.getenv("YOUTUBE_PLAYLIST_ID", "")
        
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
    
    # 動画を再生リストに追加
    def add_to_playlist(self, video_id):
        if not self.credentials:
            raise Exception("YouTube認証が完了していません")
        
        youtube = build("youtube", "v3", credentials=self.credentials)
        
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": self.playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        
        response = request.execute()
        return response
    
    # アップロード処理
    def upload(self, video_file, title, description, add_to_playlist=True):
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
        video_id = response["id"]
        
        # 再生リストに追加（設定されている場合のみ）
        if self.playlist_id:
            try:
                self.add_to_playlist(video_id)
            except Exception as e:
                print(f"再生リスト追加エラー: {e}")
        
        return response
