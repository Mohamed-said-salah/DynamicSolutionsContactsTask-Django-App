### Here we will implement the distributed lock technic


from django.core.cache import cache # To transfer data to & from redis

class DistributedLock:
    def __init__(self, lock_key, lock_token, expire_time=250):
        self.lock_key : str = lock_key # key with object id to be  set in the locked items
        self.lock_token : str = lock_token # verifies person has the permission to release locked item
        self.expire_time : int = expire_time # time object should be locked

    # To lock some object
    def acquire(self) -> bool: 
        """
            This method takes a lock_key as an id for some functionality to be blocked 
            for a period  of time and takes lock_token as a verify as a permission
            for commit specific operations.
        """
        # if it's already locked it will not re lock it as the first lock session ends
        if cache.get(self.lock_key) is not None:
            return False
        # will be locked if it wasn't
        return cache.set(self.lock_key, self.lock_token, self.expire_time)

    # verify if item is locked and it's [locker]
    # locker is the person that has the lock_token
    def verify(self) -> bool :
        "This function verifies if the current user owns the permissions for committing specific operations."
        if not cache.get(self.lock_key, False): return False # if not in locked items then won't be verified
        elif cache.get(self.lock_key, "") != self.lock_token:  return False # if user lock_token not equal the lock_token on cache then won't be verified
        return True # verified as it's saved with the lock_token user have

    # releasing the locked object from cache
    # This mean it's available for some locker to lock it and not private to any one
    def release(self) -> None:
        return cache.delete(self.lock_key)