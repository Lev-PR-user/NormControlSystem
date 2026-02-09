import functools
from typing import Any, Callable, Optional
import hashlib

from cache.redis_client import cache

def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    unless: Optional[Callable] = None
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if unless and unless():
                return func(*args, **kwargs)
            
            cache_key = _generate_cache_key(func, key_prefix, args, kwargs)
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    
    return decorator


def _generate_cache_key(
    func: Callable, 
    prefix: str, 
    args: tuple, 
    kwargs: dict
) -> str:
    func_name = func.__module__ + "." + func.__qualname__
    
    args_repr = repr(args)
    kwargs_repr = repr(sorted(kwargs.items()))
    
    key_string = f"{func_name}:{args_repr}:{kwargs_repr}"
    
    hash_obj = hashlib.md5(key_string.encode())
    key_hash = hash_obj.hexdigest()
    
    return f"{prefix}{key_hash}" if prefix else key_hash