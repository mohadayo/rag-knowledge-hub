# RAG Knowledge Hub - 社内ナレッジ検索AI

社内マニュアル・FAQ・議事録・業務手順書などをアップロードし、自然文で質問すると根拠付きで回答する社内ナレッジ検索AIのMVPです。

## 技術スタック

| レイヤー | 技術 |
|----------|------|
| フロントエンド | Next.js 15 + React 19 + Tailwind CSS |
| バックエンド | Python + FastAPI |
| ベクトルDB | ChromaDB |
| メタデータDB | SQLite |
| LLM/Embedding | OpenAI API (gpt-4o-mini / text-embedding-3-small) |

## ディレクトリ構成

```
├── docker-compose.yml
├── backend/
│   ├── main.py              # FastAPIアプリケーション
│   ├── config.py             # 設定
│   ├── database.py           # DB接続
│   ├── models.py             # SQLAlchemyモデル
│   ├── schemas.py            # Pydanticスキーマ
│   ├── routers/
│   │   ├── documents.py      # 文書管理API
│   │   └── chat.py           # チャットAPI
│   └── services/
│       ├── document_processor.py  # テキスト抽出・チャンク分割
│       ├── embedding_service.py   # Embedding生成
│       ├── vector_store.py        # ChromaDB操作
│       └── rag_service.py         # RAGパイプライン
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx       # トップページ
│       │   ├── chat/page.tsx  # チャット画面
│       │   └── admin/page.tsx # 管理画面
│       ├── components/        # UIコンポーネント
│       └── lib/api.ts         # APIクライアント
└── sample_data/               # テスト用ダミーデータ
```

## セットアップ

### 前提条件

- Node.js 20+
- Python 3.12+
- OpenAI APIキー

### 1. バックエンド

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
# .env を編集して OPENAI_API_KEY を設定

# 起動
uvicorn main:app --reload --port 8000
```

### 2. フロントエンド

```bash
cd frontend
npm install
npm run dev
```

### 3. Docker Compose（一括起動）

```bash
# backend/.env を作成してAPIキーを設定
cp backend/.env.example backend/.env

docker compose up --build
```

ブラウザで http://localhost:3000 にアクセスしてください。

## API

| Method | Path | 説明 |
|--------|------|------|
| GET | `/api/health` | ヘルスチェック |
| POST | `/api/documents/upload` | 文書アップロード |
| GET | `/api/documents` | 文書一覧 |
| DELETE | `/api/documents/{id}` | 文書削除 |
| POST | `/api/chat` | RAG質問 |

## テスト用ダミーデータ

`sample_data/` に社内規定のサンプルファイルが入っています。管理画面からアップロードしてお試しください。
