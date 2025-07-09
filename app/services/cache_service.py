"""
Caching service for the AI Cover Letter Generator.
Provides in-memory caching with TTL support.
"""

import time
import json
import hashlib
import logging
from typing import Any, Optional, Dict
from threading import Lock

logger = logging.getLogger(__name__)

class CacheEntry:
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = time.time() + ttl
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    def age_seconds(self) -> float:
        return time.time() - self.created_at

class CacheService:
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize cache service.
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = Lock()
        self.hits = 0
        self.misses = 0
        
        logger.info(f"Cache service initialized with max_size={max_size}, default_ttl={default_ttl}")
    
    def _create_key(self, key_data: Any) -> str:
        """Create a cache key from data."""
        if isinstance(key_data, (dict, list)):
            key_str = json.dumps(key_data, sort_keys=True)
        else:
            key_str = str(key_data)
        
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _evict_expired(self):
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items() 
            if entry.expires_at <= current_time
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Evicted {len(expired_keys)} expired cache entries")
    
    def _evict_oldest(self, count: int = 1):
        """Evict the oldest entries."""
        if not self.cache:
            return
        
        # Sort by creation time and remove oldest
        sorted_entries = sorted(
            self.cache.items(), 
            key=lambda x: x[1].created_at
        )
        
        for i in range(min(count, len(sorted_entries))):
            key = sorted_entries[i][0]
            del self.cache[key]
        
        logger.debug(f"Evicted {count} oldest cache entries")
    
    def get(self, key_data: Any) -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._create_key(key_data)
        
        with self.lock:
            entry = self.cache.get(cache_key)
            
            if entry is None:
                self.misses += 1
                return None
            
            if entry.is_expired():
                del self.cache[cache_key]
                self.misses += 1
                return None
            
            self.hits += 1
            return entry.value
    
    def set(self, key_data: Any, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        if ttl is None:
            ttl = self.default_ttl
        
        cache_key = self._create_key(key_data)
        
        with self.lock:
            # Clean up expired entries periodically
            if len(self.cache) % 100 == 0:
                self._evict_expired()
            
            # Ensure we don't exceed max size
            if len(self.cache) >= self.max_size:
                self._evict_oldest(max(1, self.max_size // 10))  # Remove 10% of entries
            
            self.cache[cache_key] = CacheEntry(value, ttl)
    
    def delete(self, key_data: Any) -> bool:
        """Delete entry from cache."""
        cache_key = self._create_key(key_data)
        
        with self.lock:
            if cache_key in self.cache:
                del self.cache[cache_key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
        
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate_percent": round(hit_rate, 2),
                "total_requests": total_requests
            }
    
    def cleanup(self) -> int:
        """Remove all expired entries and return count removed."""
        with self.lock:
            initial_size = len(self.cache)
            self._evict_expired()
            removed_count = initial_size - len(self.cache)
            
        logger.info(f"Cache cleanup removed {removed_count} expired entries")
        return removed_count

# Global cache instances
company_research_cache = CacheService(max_size=500, default_ttl=7200)  # 2 hours
llm_response_cache = CacheService(max_size=200, default_ttl=3600)      # 1 hour
embedding_cache = CacheService(max_size=1000, default_ttl=86400)       # 24 hours