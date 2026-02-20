"""Unit tests for example function."""
import pytest
from unittest.mock import AsyncMock
from src.functions.example import get_weather_data_impl


@pytest.mark.asyncio
async def test_get_weather_with_mock_client():
    """Test weather retrieval with injected mock client.

    Note: get_weather_data_impl は実装関数で、Dependency Injection パターンを使用しています。
    モッククライアントを注入することで、外部APIを呼ばずにテストできます。
    """
    # モッククライアント作成
    mock_client = AsyncMock()
    mock_client.get_weather.return_value = {
        "city": "Tokyo",
        "temperature": 25,
        "condition": "Sunny"
    }

    # テスト実行
    result = await get_weather_data_impl("Tokyo", client=mock_client)

    # 検証
    assert result["city"] == "Tokyo"
    assert result["temperature"] == 25
    assert result["condition"] == "Sunny"
    mock_client.get_weather.assert_called_once_with("Tokyo")


@pytest.mark.asyncio
async def test_get_weather_different_city():
    """Test weather retrieval for different city."""
    mock_client = AsyncMock()
    mock_client.get_weather.return_value = {
        "city": "Osaka",
        "temperature": 20,
        "condition": "Cloudy"
    }

    # テスト実行
    result = await get_weather_data_impl("Osaka", client=mock_client)

    assert result["city"] == "Osaka"
    assert result["temperature"] == 20
