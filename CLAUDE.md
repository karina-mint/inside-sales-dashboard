# inside sales dashboard

## 対象タスク
シートにあるinside salesのデータをリアルに反映するHTML

## 期待される効果
全体ダッシュボードシートの案件獲得数、リード獲得数。それぞれ

## 実装方針
月データを反映、それぞれの目標、実達成率

## 現在の手順

## 自動化する手順

## ファイル構成

### 開発時のソース（src/）
- `src/functions/`: 各functionの実装（ツール/機能）
  - `example.py`: サンプル - 天気情報取得
- `src/agent.py`: OpenAI Agents SDK Agent定義
- `src/main_template.py`: エントリーポイント（stdin/stdout）

### ビルド成果物
- `main.py`: 本番用統合ファイル（build.pyで自動生成）

### テスト
- `tests/unit/`: Function単体テスト
- `tests/test_main_integration.py`: Agent統合テスト
- `tests/conftest.py`: 共通フィクスチャ
- `tests/mocks/`: モックヘルパー

### その他
- `build.py`: ビルドスクリプト（src/ → main.py）
- `pyproject.toml`: プロジェクト設定・依存関係
- `.env`: 環境変数（API キーなど）
- `input_schema.json`: 入力スキーマ

## 開発フロー

### 1. 機能実装

```bash
# src/functions/に新しいfunctionを追加
vim src/functions/my_function.py

# Agent定義を更新（functionsを登録）
vim src/agent.py
```

**重要**: OpenAI Agents SDK 0.7.0+ では、関数を `@function_tool` デコレーターでラップする必要があります。

```python
from agents import function_tool

@function_tool
async def my_function(param: str) -> dict:
    """Function description.

    Args:
        param: Parameter description
    """
    # 実装
    return {"result": "success"}
```

デコレーターなしで関数を渡すと `AttributeError: 'function' object has no attribute 'name'` エラーが発生します。

### 2. 単体テスト

```bash
# Function単体テスト実行
pytest tests/unit/ -v

# カバレッジ付き
pytest tests/unit/ --cov=src --cov-report=html
```

### 3. ビルド

```bash
# src/を統合してmain.pyを生成
uv run python build.py
```

### 4. 統合テスト

```bash
# bundled main.pyの統合テスト
pytest tests/test_main_integration.py -v

# 手動実行テスト
echo '{"message": "test"}' | uv run main.py
```

### 5. プッシュ

```bash
# Admin Consoleにアップロード（main.pyのみ）
agentize-dev-cli push

# ※ src/が更新されている場合、警告が表示されます
```

### 6. ドキュメント更新

プロジェクトの変更に応じて、ドキュメントを更新してください：

```bash
# README.mdを更新（特に以下の変更時）
# - プロジェクト構造の変更
# - 開発ワークフローの変更
# - 依存関係の追加・変更
# - セットアップ手順の変更
```

**AIコーディングエージェントへ**:
- このプロジェクトでは**uv**を使用します。Python実行時は`uv run`、依存関係追加は`uv add`を使用してください。
- プロジェクトを変更する際は、README.mdを必ず最新に保ってください。

### 7. MCPサーバーとして起動

```bash
agentize-dev-cli serve
```

Claude Desktopの設定ファイル（`~/.config/Claude/claude_desktop_config.json`）に追加:

```json
{
  "mcpServers": {
    "inside-sales-dashboard": {
      "command": "agentize-dev-cli",
      "args": ["serve"],
      "cwd": "/path/to/this/directory"
    }
  }
}
```

## テスト戦略

詳細は `TESTING.md` を参照してください。

### 3層テストアプローチ

1. **単体テスト**: src/functions/の各functionを個別にテスト（完全モック）
2. **統合テスト**: bundled main.pyをstdin/stdout経由でテスト（APIモック）
3. **E2Eテスト**: 実環境での動作確認（制限的）

### CI/CD

- CI: GitHub Actions（unit-tests → build → integration-tests）
- CD: agentize-dev-cli push

## agentize-dev-cli コマンドリファレンス

### push - Admin Consoleに開発版をアップロード

```bash
agentize-dev-cli push [--dry-run]
```

| オプション | 説明 |
|-----------|------|
| `--dry-run` | バリデーションのみ実行（アップロードしない） |

**アップロード対象ファイル**:
- `main.py`（必須）
- `.env`（オプション）
- `input_schema.json`（オプション）

### deploy - 本番環境へデプロイ

```bash
agentize-dev-cli deploy [--version VERSION] [--note NOTE] [--production-env FILE] [--yes]
```

| オプション | 説明 |
|-----------|------|
| `--version` | バージョンラベル（例: v1.0.0） |
| `--note` | デプロイメント説明 |
| `--production-env` | 本番用.envファイルパス |
| `--yes` / `-y` | 確認プロンプトをスキップ |
| `--dry-run` | バリデーションのみ実行 |

### serve - ローカルMCPサーバー起動

```bash
agentize-dev-cli serve [--ngrok] [--port PORT] [--verbose]
```

| オプション | 説明 |
|-----------|------|
| `--ngrok` | ngrokトンネル経由でHTTP公開 |
| `--port` | HTTPサーバーポート（デフォルト: 8080） |
| `--verbose` / `-v` | 詳細ログ出力 |

## Claude Code向け自動化ワークフロー

### コード変更後のpush手順

1. `uv run python build.py` でmain.pyを再生成
2. `uv run pytest tests/` でテスト実行（全テストパス必須）
3. `agentize-dev-cli push --dry-run` でバリデーション確認
4. `agentize-dev-cli push` でアップロード

### 本番リリース手順

1. pushが完了していることを確認
2. `agentize-dev-cli deploy --dry-run` で確認
3. `agentize-dev-cli deploy --version vX.Y.Z --note "変更内容の説明" --yes` で実行

### 重要な注意事項

- **ビルド必須**: src/配下を編集したら必ず `uv run python build.py` を実行してからpush
- **テスト必須**: push前に `uv run pytest tests/` でテストをパス
- **バージョン命名**: セマンティックバージョニング（vX.Y.Z）を使用
- **環境変数**: `.env`は開発用。本番用は別途 `--production-env` オプションで指定
- **--yesオプション**: CI/CD環境や自動化時に使用。対話的確認をスキップ

## トラブルシューティング

### ビルドエラー

```bash
# src/ディレクトリ確認
ls src/

# 構文エラーチェック
python -m py_compile src/**/*.py
```

### テスト失敗

```bash
# ログ確認
cat logs/<timestamp>/stderr.txt

# モック設定確認
cat tests/mocks/openai_mock.py
```

### pushで警告が表示される

```bash
# src/が更新されているため、再ビルドが必要
uv run python build.py
agentize-dev-cli push
```

## I/O制約

Agent Runnerとのstdin/stdout通信における制約ルールです。

### MUST（必須）
- stdinからJSON文字列を `json.loads(sys.stdin.read())` で読み取ること
- stdoutへの出力は1行1JSON（`print(json.dumps(...))`）またはテキスト行で行うこと
- `image_output` / `audio_output` / `resource_output` を出力する場合は `"type"` フィールドを明示すること
- エラー時はstderr（`print(..., file=sys.stderr)`）に出力し、非ゼロ終了コードで終了すること
- 出力バッファリングに依存しないこと（`PYTHONUNBUFFERED=1` が設定されます）

### MUST NOT（禁止）
- メタデータフィールド（`_llm_usage`, `_profile_data`, `_trace_data`）をスクリプト出力に含めないこと（Agent Runnerが自動管理）
- stdinの `runner_request_id` / `client_request_id` をstdoutに出力しないこと（内部メタデータ）
- 複数行にまたがるJSON出力を行わないこと（1行=1出力として解析されます）

## 参考資料

- [README.md](./README.md): プロジェクト概要とクイックスタート
- [TESTING.md](./TESTING.md): テスト実行ガイド
- [AGENTS.md](./AGENTS.md): OpenAI Agents SDK実装ガイド
- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
