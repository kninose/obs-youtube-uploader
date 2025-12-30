# 開発環境のセットアップ

## 初回セットアップ

1. リポジトリをクローン
```sh
git clone <repository-url>
cd obs-uploader
```

2. 開発環境の作成
```sh
py -3.12 -m venv venv
```

3. 仮想環境の有効化
```sh
venv\Scripts\activate
```

4. 依存関係のインストール
```sh
pip install -r requirements.txt
```

5. 環境変数の設定
```sh
copy config\.env.example .env
```
.env ファイルを開いて，OBSのサーバーパスワードを設定してください

## 二回目以降の開発
開発開始時
```sh
venv\Scripts\activate
```

開発終了時
```sh
deactivate
```

## 依存関係の管理
新しいパッケージを追加した場合
```sh
pip install <package-name>
pip freeze > requirements.txt
```

パッケージをアップグレードした場合
```sh
pip install --upgrade <package-name>
pip freeze > requirements.txt
```

## トラブルシューティング
仮想環境が壊れた場合
```sh
deactivate
rmdir /s venv
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```