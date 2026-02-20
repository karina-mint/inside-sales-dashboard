"""OpenAI API mocks using respx."""
import respx
from httpx import Response


def mock_openai_chat_completion(content: str = "Mocked response"):
    """Mock OpenAI chat completion endpoint.

    Args:
        content: Response content

    Returns:
        respx route
    """
    return respx.post(
        "https://api.openai.com/v1/chat/completions"
    ).mock(
        return_value=Response(
            200,
            json={
                "id": "chatcmpl-test",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15
                }
            }
        )
    )
