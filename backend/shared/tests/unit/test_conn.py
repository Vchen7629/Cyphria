import pytest
from fastapi import FastAPI
from unittest.mock import patch
from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_pool_closed_on_db_health_check_failure() -> None:
    """Pool should be closed if database health check fails during startup"""
    mock_pool = MagicMock()
    mock_pool.connection.side_effect = Exception("Connection refused")

    with patch("shared_db.conn.create_verified_connection_pool", return_value=mock_pool):
        app = FastAPI(lifespan=lifespan)

        with pytest.raises(Exception, match="Connection refused"):
            async with lifespan(app):
                pass

        mock_pool.close.assert_called_once()
