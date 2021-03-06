from __future__ import division

from datetime import datetime
from cachecontrol.cache import BaseCache


def total_seconds(td):
    """Python 2.6 compatability"""
    if hasattr(td, 'total_seconds'):
        return int(td.total_seconds())

    ms = td.microseconds
    secs = (td.seconds + td.days * 24 * 3600)
    return int((ms + secs * 10**6) / 10**6)


class RedisCache(BaseCache):

    def __init__(self, conn):
        self.conn = conn

    def get(self, key):
        return self.conn.get(key)

    def set(self, key, value, expires=None):
        if not expires:
            self.conn.set(key, value)
        else:
            # the keyword arguments are to account for a Redis v StrictRedis issue
            # with pyredis being a mess. this is compatible with both.

            redis_class = self.conn.__class__
            if redis_class == 'redis.client.StrictRedis':
                # StrictRedis
                self.conn.setex(key, expires, value)
            elif redis_class == 'redis.client.Redis':
                # Redis
                self.conn.setex(key, value, expires)
            else:
                # unknown redis client type. give it a shot.

                try:
                    self.conn.setex(key, expires, value)
                except Exception as e:
                    # complete failure. give up and don't set a date.
                    self.conn.set(key, value)
    def delete(self, key):
        self.conn.delete(key)

    def clear(self):
        """Helper for clearing all the keys in a database. Use with
        caution!"""
        for key in self.conn.keys():
            self.conn.delete(key)

    def close(self):
        """Redis uses connection pooling, no need to close the connection."""
        pass
