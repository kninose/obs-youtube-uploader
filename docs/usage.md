# 使い方

## 初回設定

### 1. OBS WebSocketの設定
1. OBSを起動
2. 「ツール」→「WebSocketサーバー設定」
3. 「WebSocketサーバーを有効にする」にチェック
4. サーバーポート: `4455`（デフォルト）
5. パスワードを設定（覚えておく）
6. 「適用」→「OK」

### 2. 環境変数の設定
下記コマンドを実行
```sh
copy config\.env.example .env
```

`.env` ファイルを開いて編集
```sh
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=your_password
YOUTUBE_PLAYLIST_ID=  # 再生リストIDを設定（任意。未設定の場合は再生リストに追加されません）
```
⚠️ `OBS_PASSWORD` には，手順1で設定したパスワードを入力してください

### 3. YouTube API認証情報の取得

#### Google Cloud Consoleでの設定

1. https://console.cloud.google.com/ にアクセス
2. 新しいプロジェクトを作成
3. 「APIとサービス」→「ライブラリ」
4. 「YouTube Data API v3」を検索して有効化

#### OAuth 同意画面の設定
1. 「APIとサービス」→「OAuth 同意画面」-> 「開始」
2. 任意のアプリ名とメールアドレスを設定
3. 対象: **「外部」** を選択
4. 任意のメールアドレスを入力
5. 「続行」->「作成」
6. 「データアクセス」->「スコープを追加または削除」
   - `https://www.googleapis.com/auth/youtube` にチェック
   - 「更新」→「保存して次へ」
7. 「対象」->テストユーザー: 「+ Add Users」
   - **動画投稿したいYouTubeアカウントのGmailアドレス**を追加
   - 「保存」

#### OAuth クライアント ID の作成
1. 「APIとサービス」→「クライアント」->「+ クライアントを作成」
2. アプリケーションの種類: **「デスクトップ アプリ」**
3. 名前: 任意（例: OBS Uploader Client）
4. 「作成」
5. クライアントシークレット をダウンロード
6. ダウンロードしたファイルを `client_secrets.json` にリネーム
7. プロジェクトルート（`obs-uploader/`）に配置

#### YouTubeチャンネルの作成
1. https://www.youtube.com/ にアクセス
2. 認証に使うGoogleアカウントでログイン
3. YouTubeチャンネルを作成（未作成の場合）

#### 再生リストの設定（オプション）

再生リストに自動追加したい場合:

1. YouTubeで再生リストを作成（または既存のものを選択）
2. 再生リストのURLを開く
   - 例: `https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxx`
3. `list=` の後の文字列（再生リストID）をコピー
4. `.env` ファイルの `YOUTUBE_PLAYLIST_ID` に設定
   ```sh
   YOUTUBE_PLAYLIST_ID=PLxxxxxxxxxxxxxx
   ```

⚠️ **未設定の場合**: 動画はアップロードされますが、再生リストには追加されません

## アプリの起動
```sh
python app/main.py
```

## 初回実行時の認証

1. アプリを起動すると、ブラウザが自動的に開きます
2. Googleアカウントでログイン
3. 「このアプリは確認されていません」と表示された場合:
   - 「続行」→「続行」をクリック
4. ウィンドウを閉じる
