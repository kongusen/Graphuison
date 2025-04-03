import redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Redis 客户端配置
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True  # 自动解码响应
)

def init_redis():
    """初始化 Redis 连接"""
    try:
        redis_client.ping()
        logger.info("Redis 连接成功")
    except redis.ConnectionError as e:
        logger.error(f"Redis 连接失败: {e}")
        raise 