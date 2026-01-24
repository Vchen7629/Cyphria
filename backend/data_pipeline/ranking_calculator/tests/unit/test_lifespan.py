import pytest
from fastapi import FastAPI
from unittest.mock import MagicMock, patch
import os                                                                                                 
os.environ.setdefault("BAYESIAN_PARAMS", "10")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASS", "test_pass")                                                  
from src.core.lifespan import lifespan                    

@pytest.mark.asyncio
async def test_lifespan_closes_pool_on_db_health_check_failure() -> None:
    """Pool should be closed if database health check fails during startup"""
    mock_pool = MagicMock()
    mock_pool.connection.side_effect = Exception("Connection refused")

    with patch('src.core.lifespan.create_connection_pool', return_value=mock_pool):
        app = FastAPI(lifespan=lifespan)

        with pytest.raises(Exception, match="Connection refused"):
            async with lifespan(app):
                pass
    
        mock_pool.close.assert_called_once()