# テスト実行ガイド

## 概要

このプロジェクトは3層テスト戦略を採用しています:
1. **単体テスト**: src/functions/の各functionを個別にテスト
2. **統合テスト**: bundled main.pyをstdin/stdout経由でテスト
3. **E2Eテスト**: 実環境での動作確認（制限的）

## テスト実行

### 単体テスト

```bash
# 全単体テスト実行
pytest tests/unit/ -v

# 特定のテスト実行
pytest tests/unit/test_example.py -v

# カバレッジ付き
pytest tests/unit/ --cov=src --cov-report=html
open htmlcov/index.html
```

### ビルド

```bash
# src/を統合してmain.pyを生成
uv run python build.py

# ビルド成果物の確認
head -n 50 main.py
python -m py_compile main.py
```

### 統合テスト

```bash
# bundled main.pyの統合テスト
pytest tests/test_main_integration.py -v

# 手動実行テスト
echo '{"message": "test"}' | uv run main.py
```

## CI/CD

GitHub Actionsで自動テスト:

1. **unit-tests**: src/の単体テスト + カバレッジ
2. **build**: main.py生成
3. **integration-tests**: bundled main.pyのテスト
4. **lint**: ruff check

`.github/workflows/agent-tests.yml`を参照。

## 既存エージェントの移行ガイド

既存のmain.pyのみのエージェントを、新しいsrc/構造に移行する手順:

### ステップ1: バックアップ

```bash
cp main.py main.py.backup
```

### ステップ2: src/ディレクトリ作成

```bash
mkdir -p src/functions
touch src/__init__.py
touch src/functions/__init__.py
```

### ステップ3: functionの抽出

main.py内のfunction定義を`src/functions/`に移動。

**例: 天気取得functionの場合**

main.pyから以下のコードを抽出:

```python
async def get_weather_data(city: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(...)
        return response.json()
```

→ `src/functions/weather.py`に移動。

**重要**: OpenAI Agents SDK 0.7.0+ では `@function_tool` デコレーターが必要です:

```python
from agents import function_tool

@function_tool
async def get_weather_data(city: str) -> dict:
    # ...
```

### ステップ4: Agent定義の抽出

main.py内のAgent定義を`src/agent.py`に移動。

### ステップ5: main_template.py作成

`src/main_template.py`を作成（PEP 723メタデータは不要、pyproject.tomlから自動生成される）。

### ステップ6: pyproject.toml作成

```toml
[project]
name = "my-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "openai-agents>=0.7.0",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "respx>=0.21",
    "ruff>=0.4",
]
```

### ステップ7: build.pyをコピー

新規プロジェクト生成時のbuild.pyを参考にコピー。

### ステップ8: ビルド

```bash
uv run python build.py
```

### ステップ9: 動作確認

```bash
# 新旧main.pyの比較
diff main.py.backup main.py

# 動作テスト
echo '{"message": "test"}' | uv run main.py
```

### ステップ10: テスト追加

`tests/unit/`にfunction単体テストを追加。

### 移行完了チェックリスト

- [ ] src/functions/にfunctionを抽出（@function_tool追加）
- [ ] src/agent.pyにAgent定義を抽出
- [ ] src/main_template.pyを作成
- [ ] pyproject.tomlを作成
- [ ] build.pyをコピー
- [ ] uv run python build.pyでビルド成功
- [ ] 動作確認（echo ... | uv run main.py）
- [ ] tests/unit/に単体テスト追加
- [ ] pytest tests/unit/ -v でテスト成功

## トラブルシューティング

### import エラー

```bash
# AST解析エラーの場合
python -m py_compile src/**/*.py
```

### テスト失敗

```bash
# 依存関係の確認
uv pip list

# モック設定の確認
cat tests/mocks/openai_mock.py
```

### @function_tool エラー

```bash
# エラー: AttributeError: 'function' object has no attribute 'name'
# 原因: 関数に @function_tool デコレーターがない
# 解決: src/functions/*.py の全関数に @function_tool を追加
```
