#!/bin/bash
# IS ダッシュボード起動スクリプト

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== IS ダッシュボード起動 ==="
echo ""

# バックエンド起動
echo "[1/2] バックエンド起動中 (port 8000)..."
cd "$SCRIPT_DIR/backend"
uv run uvicorn app.main:app --port 8000 --reload &
BACKEND_PID=$!
echo "  → Backend PID: $BACKEND_PID"

# 少し待つ
sleep 2

# フロントエンド起動
echo ""
echo "[2/2] フロントエンド起動中 (port 5173)..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "  → Frontend PID: $FRONTEND_PID"

echo ""
echo "=== 起動完了 ==="
echo "  ダッシュボード: http://localhost:5173"
echo "  API:           http://localhost:8000/api/dashboard"
echo "  API ドキュメント: http://localhost:8000/docs"
echo ""
echo "終了するには Ctrl+C を押してください"

# 両方のプロセスを待つ
wait $BACKEND_PID $FRONTEND_PID
