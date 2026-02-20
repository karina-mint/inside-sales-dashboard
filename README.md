# inside sales dashboard

OpenAI Agents SDKを使用したエージェントプロジェクト。

**対象タスク**: シートにあるinside salesのデータをリアルに反映するHTML

**期待される効果**: 全体ダッシュボードシートの案件獲得数、リード獲得数。それぞれ

> **🤖 エージェント開発者へ**:
> - このプロジェクトでは**uv**を使用します。Python実行時は`uv run`、パッケージ管理は`uv add`/`uv sync`を使用してください。
> - プロジェクトを変更する際は、変更内容に応じてREADME.mdを必ず更新してください。特に以下の変更時:
>   - プロジェクト構造の変更（新しいディレクトリ/ファイル追加）
>   - 開発ワークフローの変更（ビルド手順、テスト方法など）
>   - 依存関係の追加・変更
>   - セットアップ手順の変更

## クイックスタート

### 前提条件

- Python 3.11以上
- **[uv](https://github.com/astral-sh/uv)** (必須) - 高速なPythonパッケージマネージャー
  ```bash
  # uvのインストール（macOS/Linux）
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # uvのインストール（Windows）
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

  # ngrokのインストール（--ngrokオプションを使用する場合）
  https://ngrok.com/download を参照してインストールしておく
  ```

### セットアップ

#### 1. 変更をトラックするためまずは git init する

```bash
git init
git add .
git commit -m "Initial commit"
```

#### 2. 関連ソフトウェアのインストール確認

```bash
uv --version
ngrok version
```

インストールされていない場合は、前提条件のセクションを参照してインストールしてください。

#### 3. 環境変数の設定

`.env` ファイルを作成して、OpenAI API キーを設定します:

```bash
# .envファイルを作成
cat > .env << 'EOF'
OPENAI_API_KEY=your-openai-api-key-here
EOF
```

または、エディタで直接編集:

```bash
# エディタで.envファイルを作成・編集
vim .env
```

`.env` ファイルの内容:
```
OPENAI_API_KEY=sk-...
```

#### 4. 依存関係のインストール

本番用の依存関係をインストール:

```bash
uv sync
```

開発用の依存関係（pytest など）もインストール:

```bash
uv sync --extra dev
```

#### 5. ビルドの実行

`src/` ディレクトリから `main.py` を生成:

```bash
uv run python build.py
```

成功すると、`main.py` が生成されます。

#### 6. テストの実行（オプション）

単体テストを実行して、セットアップが正しいことを確認:

```bash
# 単体テストのみ実行（API キー不要）
uv run pytest tests/unit/ -v

# すべてのテストを実行
uv run pytest -v
```

**注意**: 統合テストは実際の OpenAI API を呼び出すため、有効な `OPENAI_API_KEY` が必要です。API キーが設定されていない場合、統合テストは自動的にスキップされます。

### 実行

エージェントの実行は `agentize-dev-cli serve` コマンドでローカル MCP サーバーを起動し、toggle Agent などのクライアントから接続します。

```bash
# 基本的な実行
agentize-dev-cli serve --ngrok
```

ターミナルに表示されたURLを、toggle AgentのMCPサーバー設定に追加します。

## プロジェクト構造

```
.
├── src/                    # 開発ソース
│   ├── functions/         # Function実装
│   ├── agent.py           # Agent定義
│   └── main_template.py   # エントリーポイント
├── tests/                 # テストコード
├── main.py                # ビルド済み本番ファイル
├── build.py               # ビルドスクリプト
├── pyproject.toml         # プロジェクト設定
└── .env                   # 環境変数
```

## 開発ワークフロー

このプロジェクトでは**uv**を使用します。全てのPython実行は`uv run`を使用してください。

1. **機能開発**: `src/functions/`に実装（**重要**: エージェントが利用する関数には`@function_tool`デコレーターが必須）
2. **依存関係追加**: `uv add <package>`
3. **テスト**: `uv run pytest -v`
4. **ビルド**: `uv run python build.py`
5. **Agentize EngineへPush**: `agentize-dev-cli push`

詳細は [CLAUDE.md](./CLAUDE.md) を参照してください。

## ドキュメント

- **[CLAUDE.md](./CLAUDE.md)**: 詳細な開発ガイド
- **[AGENTS.md](./AGENTS.md)**: OpenAI Agents SDK実装パターン
- **[TESTING.md](./TESTING.md)**: テスト戦略とCI/CD設定

## デプロイ詳細

本番環境へのデプロイは `agentize-dev-cli push` でAgentize Engineにプログラムを登録したのち `agentize-dev-cli deploy --production-env .env.production` コマンドを使用します。
.env.production ファイルには本番環境用の環境変数を設定してください。このファイルは .gitignore に含まれているので、勝手にコミットされることはありません。

## 技術スタック

- [OpenAI Agents SDK](https://platform.openai.com/docs/agents) - エージェントフレームワーク
- [Open-Meteo API](https://open-meteo.com/) - 無料の天気予報API（API キー不要）
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - 高速パッケージマネージャー
- pytest (テスト)

## トラブルシューティング

### `uv: command not found`

uvがインストールされていません。前提条件のセクションを参照してインストールしてください:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### `pytest: command not found`

開発用依存関係がインストールされていません:

```bash
uv sync --extra dev
```

### `OPENAI_API_KEY not found`

`.env` ファイルが作成されていないか、API キーが設定されていません:

```bash
# .envファイルを作成
echo "OPENAI_API_KEY=your-api-key" > .env
```

### `main.py not found`

ビルドが実行されていません:

```bash
uv run python build.py
```

### 統合テストがスキップされる

統合テストは実際の OpenAI API を呼び出すため、`OPENAI_API_KEY` が設定されていない場合は自動的にスキップされます。これは正常な動作です。単体テストのみを実行する場合:

```bash
uv run pytest tests/unit/ -v
```
