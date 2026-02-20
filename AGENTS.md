# OpenAI Agents SDK 実装ガイド

## 概要

このエージェントは OpenAI Agents SDK を使用して実装されています。
OpenAI Agents SDK は、AIエージェントを簡単に構築・実行できる公式SDKです。

## 基本構造

```python
from agents import Agent, Runner

# エージェント定義
agent = Agent(
    name="My Agent",
    instructions="あなたは親切なアシスタントです。"
)

# 実行
result = Runner.run_sync(agent, "こんにちは！")
print(result.final_output)
```

## ツールの使い方

エージェントにツール（関数）を追加することで、外部データにアクセスしたり操作を実行できます。

**重要**: OpenAI Agents SDK 0.7.0+ では、関数を `@function_tool` デコレーターでラップする必要があります。

```python
from agents import function_tool

@function_tool
def get_weather(location: str) -> str:
    """天気情報を取得する

    Args:
        location: 地名
    """
    return f"{location}の天気は晴れです。"

# ツール付きエージェント
agent = Agent(
    name="Weather Agent",
    instructions="あなたは天気情報アシスタントです。",
    tools=[get_weather]
)

result = Runner.run_sync(agent, "東京の天気は？")
```

### なぜ @function_tool が必要か

- SDK は内部で `tool.name` 属性にアクセスします
- 生のPython関数には `name` 属性がありません（`__name__` はありますが）
- `@function_tool` デコレーターが関数を `FunctionTool` オブジェクトに変換し、必要な属性を追加します
- デコレーターなしで関数を渡すと `AttributeError: 'function' object has no attribute 'name'` エラーが発生します

## PEP 723 インラインメタデータ

依存関係は main.py の冒頭に記述します:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai-agents>=0.7.0",
#     "httpx>=0.27",
# ]
# ///
```

## 環境変数

`.env`ファイルに API キーなどを記述:

```
OPENAI_API_KEY=your-api-key-here
OPENAI_DEFAULT_MODEL=gpt-5.2
LOG_LEVEL=INFO
```

## Agent Runner I/O仕様

<!-- See also: agent_development.html I/O仕様セクション -->

Agent Runnerがスクリプト（main.py）を実行する際の入出力仕様です。

### 入力（stdin）

Agent RunnerはJSON文字列をstdinに渡します。スクリプト側では `sys.stdin.read()` で読み取り、`json.loads()` でパースします。

```json
{
  "prompt": "ユーザーからの入力テキスト",
  "runner_request_id": "uuid-string",
  "client_request_id": "optional-uuid-string"
}
```

- `prompt` など入力フィールドはエージェントの `input_schema.json` で定義されたデータ
- `runner_request_id`: Agent Runnerが付与するリクエスト識別子（常に付与）
- `client_request_id`: クライアント指定のリクエストID（オプション）

```python
import sys, json
input_data = json.loads(sys.stdin.read())
prompt = input_data.get("prompt", "")
```

### 出力（stdout）

stdoutに出力された各行は以下の6タイプに自動分類されます:

| タイプ | 判定条件 | 用途 |
|--------|----------|------|
| `json_output` | 有効なJSON行（typeフィールドなし、または未知のtype） | 構造化データ出力 |
| `text_output` | JSONパース失敗のテキスト行 | テキスト出力 |
| `image_output` | JSON + `"type": "image_output"` | 画像データ（base64） |
| `audio_output` | JSON + `"type": "audio_output"` | 音声データ（base64） |
| `resource_output` | JSON + `"type": "resource_output"` | ファイル/URIリソース |
| `error` | stderrから自動抽出 | エラー情報 |

**パース処理**: 各行にJSONパースを試行 → 成功かつ `type` が `image_output`/`audio_output`/`resource_output` なら該当タイプ → その他の有効なJSONは `json_output` → JSONパース失敗は `text_output`。

### 出力タイプ別サンプルコード

```python
import json

# json_output: 構造化データ（typeフィールドなし）
print(json.dumps({"result": "success", "data": [1, 2, 3]}))

# text_output: そのままテキスト出力（JSON以外）
print("処理が完了しました")

# image_output: 画像データ
print(json.dumps({
    "type": "image_output",
    "data": "<base64-encoded-image>",
    "mimeType": "image/png"
}))

# audio_output: 音声データ
print(json.dumps({
    "type": "audio_output",
    "data": "<base64-encoded-audio>",
    "mimeType": "audio/wav"
}))

# resource_output: ファイル/URIリソース
print(json.dumps({
    "type": "resource_output",
    "uri": "file:///path/to/output.csv",
    "text": "CSVファイルを生成しました",
    "mimeType": "text/csv"
}))

# error: stderrに出力 + 非ゼロ終了コード
import sys
print("エラー詳細メッセージ", file=sys.stderr)
sys.exit(1)
```

### メタデータフィールドの自動除外

以下のフィールドは `json_output` からAPI応答時に自動除外されます（エンドユーザーには返されません）:

- `_llm_usage` — LLMトークン使用量
- `_profile_data` — プロファイリングデータ
- `_trace_data` — トレーシングデータ

これらはAgent Runnerが内部で抽出・管理します。

### 環境変数

Agent Runnerは以下の環境変数を設定してスクリプトを実行します:

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `PYTHONUNBUFFERED` | `"1"` | Python出力バッファリング無効化（リアルタイムストリーミング用） |
| `OPENAI_DEFAULT_MODEL` | 設定値 | デフォルトのOpenAIモデル名 |
| カスタム変数 | `.env`定義値 | 本番デプロイ時は `--production-env` で指定した値が優先 |

### テスト方法

ローカルでテスト:

```bash
echo '{"prompt": "test"}' | uv run main.py
```

実行ログは `logs/` ディレクトリに保存されます。

> **Note**: `update-docs` コマンドによるI/O仕様の自動更新は別Issueで対応予定です。

## 参考資料

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
- [PEP 723: Inline Script Metadata](https://peps.python.org/pep-0723/)
