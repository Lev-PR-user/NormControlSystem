import redis
from typing import Any, Optional
import pickle

from cache.redis import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
    CACHE_TTL,
    CACHE_PREFIX
)

print(f"🔧 Redis Configuration:")
print(f"   Host: {REDIS_HOST}")
print(f"   Port: {REDIS_PORT}")
print(f"   DB: {REDIS_DB}")
print(f"   Password: {'Set' if REDIS_PASSWORD else 'Not set'}")


class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=False, 
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        self.ttl = CACHE_TTL
        self.prefix = CACHE_PREFIX
    
    def _make_key(self, key: str) -> str:
        """Добавляет префикс к ключу"""
        return f"{self.prefix}{key}"
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохраняет значение в кэш"""
        try:
            key = self._make_key(key)
            serialized_value = pickle.dumps(value)
            expire_time = ttl if ttl is not None else self.ttl
            return self.redis_client.setex(key, expire_time, serialized_value)
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False
    
    def get(self, key: str) -> Any:
        """Получает значение из кэша"""
        try:
            key = self._make_key(key)
            data = self.redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Удаляет ключ из кэша"""
        try:
            key = self._make_key(key)
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Error deleting cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Проверяет существование ключа"""
        try:
            key = self._make_key(key)
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Error checking cache: {e}")
            return False
    
    def clear(self, pattern: str = "*") -> int:
        """Очищает кэш по паттерну"""
        try:
            pattern = self._make_key(pattern)
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return 0
    
    def get_or_set(self, key: str, func: callable, ttl: Optional[int] = None) -> Any:
        """Получает значение из кэша или вычисляет и сохраняет, если нет"""
        cached = self.get(key)
        if cached is not None:
            return cached
        
        value = func()
        self.set(key, value, ttl)
        return value
    
    def ping(self) -> bool:
        """Проверяет подключение к Redis"""
        try:
            return self.redis_client.ping()
        except:
            return False


cache = RedisCache()