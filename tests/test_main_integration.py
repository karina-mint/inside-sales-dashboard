"""Integration tests for bundled main.py."""
import asyncio
import json
import os
import pytest
from pathlib import Path


@pytest.fixture
def agent_script():
    """Path to main agent script."""
    return Path(__file__).parent.parent / "main.py"


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set (required for integration tests)"
)
async def test_agent_execution_basic(agent_script, mock_env):
    """Test basic agent execution via stdin/stdout."""
    if not agent_script.exists():
        pytest.skip("main.py not found (run build.py first)")

    # 入力データ
    input_data = {"message": "こんにちは"}

    # agent実行 (uv run経由)
    process = await asyncio.create_subprocess_exec(
        "uv", "run", str(agent_script),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate(
        input=json.dumps(input_data).encode()
    )

    # 検証
    if process.returncode != 0:
        print(f"STDERR: {stderr.decode()}")

    assert process.returncode == 0, f"Agent failed: {stderr.decode()}"

    # stdout解析
    output = json.loads(stdout.decode())
    assert "result" in output


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set (required for integration tests)"
)
async def test_agent_with_empty_message(agent_script, mock_env):
    """Test agent with empty message."""
    if not agent_script.exists():
        pytest.skip("main.py not found (run build.py first)")

    input_data = {"message": ""}

    process = await asyncio.create_subprocess_exec(
        "uv", "run", str(agent_script),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate(
        input=json.dumps(input_data).encode()
    )

    assert process.returncode == 0
    output = json.loads(stdout.decode())
    assert "result" in output
