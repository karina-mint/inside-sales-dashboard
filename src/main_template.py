"""Agent entry point."""
import json
import sys
from .agent import create_agent


if __name__ == "__main__":
    # stdin読み込み
    input_data = json.loads(sys.stdin.read())

    # Agent実行
    agent = create_agent()
    result = Runner.run_sync(agent, input_data.get("message", ""))

    # stdout出力
    output = {"result": result.final_output}
    print(json.dumps(output, ensure_ascii=False))
