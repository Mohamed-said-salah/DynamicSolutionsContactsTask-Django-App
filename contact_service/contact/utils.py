import redis
from django.core.cache import cache

class DistributedLock:
    def __init__(self, key, expire_time=60):
        self.key : str = key
        self.expire_time : int = expire_time
        self.locked : bool = False

    def acquire(self) -> bool:
        self.locked = cache.add(self.key, True, self.expire_time)
        return self.locked

    def release(self) -> None:
        if self.locked:
            cache.delete(self.key)
            self.locked = False