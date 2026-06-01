from config import (
    LAKE_DB_HOST,
    LAKE_DB_PORT,
    LAKE_DB_NAME,
    LAKE_DB_USER,
    LAKE_DB_PASSWORD,
)


def lake_connection_string():
    return (
        f"postgresql://{LAKE_DB_USER}:{LAKE_DB_PASSWORD}"
        f"@{LAKE_DB_HOST}:{LAKE_DB_PORT}/{LAKE_DB_NAME}"
    )