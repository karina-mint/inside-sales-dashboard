"""Agent definition."""
from agents import Agent, Runner
from .functions.example import get_weather_data


def create_agent() -> Agent:
    """Create OpenAI Agents SDK agent.

    Note: 関数は @function_tool デコレーターでラップする必要があります。
    詳細は src/functions/example.py を参照してください。

    Returns:
        Configured agent
    """
    return Agent(
        name="Example Agent",
        instructions=(
            "あなたは親切なアシスタントです。\n"
            "天気情報が必要な場合は、get_weather_data関数を使用してください。"
        ),
        tools=[get_weather_data],
    )
