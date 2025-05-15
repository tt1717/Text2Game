# Text2Game

テキストベースのゲームを実行するためのPythonプロジェクトです。

## 概要
このプロジェクトは、様々なボードゲームやテキストベースのゲームを実行するためのフレームワークを提供します。現在、以下のゲームが実装されています：

- どうぶつしょうぎ (doubutsu)
- ゴブレット (gobblet)
- コリドール (quoridor)
- 将棋 (shogi)
- オセロ (othello)

## 必要条件
- Python 3.9以上
- tkinter (GUIインターフェース用)
- Django 4.2以上 (Webアプリケーション用)

## セットアップ
1. リポジトリをクローン
```bash
git clone https://github.com/tt1717/Text2Game.git
```

2. プロジェクトディレクトリに移動
```bash
cd Text2Game
```

3. 仮想環境を作成して有効化
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
.\venv\Scripts\activate  # Windowsの場合
```

4. 必要なパッケージをインストール
```bash
pip install -r requirements.txt
```

## 使用方法

### デスクトップアプリケーションとして実行
以下のコマンドでゲームを実行できます：

```bash
python main.py <game_name>
```

利用可能なゲーム名：
- doubutsu
- gobblet
- quoridor
- shogi
- othello

例：
```bash
python main.py doubutsu
```

### Webアプリケーションとして実行
1. データベースのマイグレーションを実行
```bash
python manage.py migrate
```

2. 開発サーバーを起動
```bash
python manage.py runserver
```

3. ブラウザで http://localhost:8000 にアクセス

## プロジェクト構造
```
Text2Game/
├── main.py          # メイン実行ファイル
├── manage.py        # Django管理スクリプト
├── requirements.txt # 依存パッケージ一覧
├── text2game/       # Djangoプロジェクト設定
├── games/           # Djangoゲームアプリケーション
├── game/            # ゲームモジュールディレクトリ
│   ├── doubutsu.py  # どうぶつしょうぎ
│   ├── gobblet.py   # ゴブレット
│   ├── quoridor.py  # コリドール
│   ├── shogi.py     # 将棋
│   └── othello.py   # オセロ
└── README.md        # このファイル
```

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。

## 貢献
バグ報告や機能の提案は、GitHubのIssueを通じてお願いします。プルリクエストも歓迎します。 