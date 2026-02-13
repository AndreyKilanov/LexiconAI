from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_process_text_endpoint(client: AsyncClient):
    # Mocking the graph invocation
    with patch("src.services.linguistic.graph.app_graph.ainvoke", new_callable=AsyncMock) as mock_graph_invoke:
        mock_graph_invoke.return_value = {
            "result": ["тест", "проверка"],
            "error": None
        }

        response = await client.post(
            "/linguistic/process",
            json={
                "text": "эксперимент",
                "request_type": "synonym",
                "language": "ru"
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_text"] == "эксперимент"
        assert data["request_type"] == "synonym"
        assert data["status"] == "completed"
        assert data["result"] == ["тест", "проверка"]
