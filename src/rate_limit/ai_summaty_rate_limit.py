from src.settings.redis_config import redis_client
from aiogram.types import Message




RATE_LIMIT_KEY_TEMPLATE = "ai_job_summary_rate_limit:{tg_user_id}"
RATE_LIMIT_TTL = 60


async def check_job_item_limit(tg_user_id: int) -> bool:
    key = RATE_LIMIT_KEY_TEMPLATE.format(tg_user_id=tg_user_id)
    if redis_client.exists(key):
        ttl = redis_client.ttl(key)
        if ttl > 0:
            return False
        if ttl <= 0:
            redis_client.delete(key)
            redis_client.setex(key, RATE_LIMIT_TTL, "1")
            return True
    else:
        redis_client.setex(key, RATE_LIMIT_TTL, "1")
        return True


