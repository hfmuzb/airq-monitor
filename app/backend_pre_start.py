"""
Pre-start script which is aimed:
 - wait until connection to db is established;
"""

from loguru import logger

from tenacity import retry, stop_after_attempt, wait_fixed
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from core.config import settings as config


max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=lambda *_: logger.info("Retrying..."),
    after=lambda *_: logger.warning("...retrying ended"),
)
def init() -> None:
    try:
        engine = create_engine(url=config.DATABASE_URL)
        with engine.connect() as conn:
            # Try to create session to check if DB is awake
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(e)
        raise e
    engine.dispose()


def main() -> None:
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
