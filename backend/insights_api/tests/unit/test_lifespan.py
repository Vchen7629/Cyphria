import pytest
from fastapi import FastAPI
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.lifespan import lifespan

@pytest.mark.asyncio
async def test_lifespan_closes_pool_on_db_health_check_failure() -> None:
    """Pool should be closed if database health check fails during startup"""
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = Exception("Connection refused")
    mock_engine.dispose = AsyncMock()

    with patch("src.core.lifespan.engine", mock_engine):
        app = FastAPI()

        with pytest.raises(Exception, match="Connection refused"):
            async with lifespan(app):
                pass

        mock_engine.dispose.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan_success() -> None:
    """Lifespan should complete successfully when database is healthy"""
    mock_conn = MagicMock()
    mock_conn.execute = AsyncMock()

    mock_engine = MagicMock()
    mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=None)
    mock_engine.dispose = AsyncMock()

    mock_async_session = MagicMock()

    with patch("src.core.lifespan.engine", mock_engine), \
         patch("src.core.lifespan.async_session", mock_async_session):
        app = FastAPI()

        async with lifespan(app):
            # Verify app state was set during startup
            assert app.state.async_session == mock_async_session
            assert app.state.logger is not None

        # Verify cleanup happened on shutdown
        mock_engine.dispose.assert_called_once()