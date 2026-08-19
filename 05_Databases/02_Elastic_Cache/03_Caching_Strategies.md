# Caching Strategies: Lazy Loading vs. Write-Through

Before implementing a cache, you must evaluate if caching is appropriate for your specific data set. Ask yourself:

* **Is it safe to cache?** Can your application tolerate eventually consistent (slightly out-of-date) data?
* **Is it effective?** Caching works best for data that changes slowly but is read frequently. It is an *anti-pattern* to cache data that changes constantly and rapidly.
* **Is the data structured correctly?** You must structure the data in a way that makes it easy to retrieve from a key-value store (like storing the results of heavy database aggregations).

Once you decide to cache, you must choose a design pattern.

---

## 1. Lazy Loading (Cache-Aside / Lazy Population)

Lazy Loading is the most common and foundational caching strategy. The basic principle is: **only load data into the cache when it is actually requested.**

**How it works:**

1. **The Read Request:** The application asks ElastiCache for data.
2. **Cache Hit:** If ElastiCache has the data, it returns it immediately.
3. **Cache Miss:** If ElastiCache does *not* have the data, the application fetches the data from the primary database (e.g., RDS).
4. **Populate Cache:** The application writes the newly fetched data into ElastiCache so the next request results in a cache hit.

**Pros & Cons:**

| Pros | Cons |
| --- | --- |
| **Efficient storage:** Only data that is actually requested is cached. | **Read Penalty:** A cache miss requires three network calls (App ➡️ Cache, App ➡️ DB, App ➡️ Cache), which users may perceive as latency. |
| **Node failure is not fatal:** If a cache node fails, you just get cache misses until the cache is "warmed up" again. | **Stale Data:** If data is updated in RDS, the cache is completely unaware. It will serve outdated data until the cache expires. |

### Lazy Loading Pseudocode

```python
def get_user(user_id):
    # 1. Check the cache first
    record = cache.get(user_id)
    
    # 2. Cache Miss: Fetch from DB and populate cache
    if record is None:
        record = db.query("SELECT * FROM users WHERE id = ?", user_id)
        cache.set(user_id, record)
        
    # 3. Return the data (Cache Hit or fresh from DB)
    return record

```

---

## 2. Write-Through

Write-Through is a proactive strategy. You add or update data in the cache *at the exact same time* you update the primary database.

**How it works:**

1. The application modifies a record in Amazon RDS.
2. The application immediately writes that same updated record into ElastiCache.

**Pros & Cons:**

| Pros | Cons |
| --- | --- |
| **Data is never stale:** The cache is always perfectly synchronized with the database. | **Write Penalty:** Every database write now requires two network calls. (Users generally tolerate slower writes better than slower reads, however). |
| **Faster reads:** Users never experience the "cache miss" read penalty for recently updated data. | **Cache Churn:** If you write a lot of data that is never actually read, you are wasting valuable cache memory. |
|  | **Missing Data:** If a cache node fails, newly spun-up nodes will be empty until a new write occurs. |

*Note: Because of the "Missing Data" con, Write-Through is almost always combined with Lazy Loading to handle cache misses.*

### Write-Through Pseudocode

```python
def save_user(user_id, values):
    # 1. Write the update to the primary database
    record = db.query("UPDATE users SET ... WHERE id = ?", user_id, values)
    
    # 2. Immediately write the update to the cache
    cache.set(user_id, record)
    
    return record

```

---

## 3. Cache Evictions and Time-to-Live (TTL)

Caches have limited memory. You must have a strategy to remove old data to make room for new data. This is called **Cache Eviction**.

Data is evicted in three ways:

1. **Explicit Deletion:** Your application explicitly tells the cache to delete a specific item.
2. **Memory Full (LRU):** When the cache memory is full, the engine automatically deletes the **Least Recently Used (LRU)** items.
3. **Time-to-Live (TTL):** You assign a lifespan to a cache key (e.g., 5 minutes, 1 hour, or 3 days). Once the time expires, the item is automatically deleted.

**TTL Best Practices:**

* TTL is an excellent strategy for data like leaderboards, comments, or activity streams.
* Even a short TTL of a few seconds can prevent a database from crashing under heavy traffic.
* If your cache is constantly full and evicting items via LRU, you need to scale up (larger node) or scale out (more nodes).

---

## 4. Final Words of Wisdom

> *"There are only two hard things in Computer Science: cache invalidation and naming things."* — Phil Karlton

Caching is difficult. Here is your cheat sheet for caching strategies:

1. **Start with Lazy Loading:** It is easy to implement and immediately improves read performance.
2. **Add Write-Through later:** Only use Write-Through as a secondary optimization if your application strictly requires avoiding stale data.
3. **Use TTLs generously:** Always set a sensible TTL on your cached data (unless using a strict Write-Through model) to ensure eventual consistency.
4. **Only cache what matters:** Cache user profiles and blogs. Do not cache rapidly changing or hyper-sensitive data like a live bank account balance.