import pytest
from unittest.mock import patch
from unittest.mock import MagicMock
from shared_db.conn import create_verified_connection_pool


def test_pool_closed_on_db_health_check_failure() -> None:
    """Pool should be closed if database health check fails during startup"""
    mock_pool = MagicMock()
    mock_pool.connection.side_effect = Exception("Connection refused")

    with patch("shared_db.conn.ConnectionPool", return_value=mock_pool):
        with pytest.raises(Exception, match="Connection refused"):
            create_verified_connection_pool(
                db_host="localhost",
                db_port=5432,
                db_name="test",
                db_user="test",
                db_password="test",
                logger=MagicMock(),
                service_name="test",
            )

        mock_pool.close.assert_called_once()
