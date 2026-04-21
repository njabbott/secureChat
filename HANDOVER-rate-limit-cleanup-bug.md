# Handover: Rate Limit Cleanup Job Bug

**Date:** 2026-03-13
**Severity:** Low
**Status:** Open — not yet fixed

---

## Summary

The scheduled job that cleans up stale rate limit buckets silently fails every 5 minutes with a `RuntimeError: no running event loop`. Rate limiting itself still works correctly, but the in-memory store accumulates entries indefinitely (memory leak).

---

## Background

The backend uses a sliding-window rate limiter (`RateLimitService`) that tracks request counts per client IP in an in-memory `defaultdict` called `_store`. Each unique IP that hits a rate-limited endpoint gets an entry in `_store`. A scheduled cleanup job is supposed to prune entries for IPs that have been inactive for more than 1 hour, preventing unbounded memory growth.

**Rate-limited endpoints:**

| Endpoint | Limit | Window |
|---|---|---|
| `/api/chat/message` | 30 requests | 60 seconds |
| `/api/indexing/start` | 5 requests | 1 hour |

---

## The Bug

**File:** `backend/app/main.py`, line 112

```python
scheduler.add_job(
    lambda: asyncio.create_task(rate_limit_svc.cleanup_stale_buckets()),
    "interval",
    seconds=settings.rate_limit_cleanup_interval,  # 300s / 5 minutes
    id="rate_limit_cleanup",
    replace_existing=True,
)
```

The scheduler used is `AsyncIOScheduler` (from APScheduler). Despite its name, APScheduler executes jobs on a **background thread**, not directly on the asyncio event loop. Calling `asyncio.create_task()` from a non-async context requires a running event loop to be present in the calling thread — which there isn't. This causes the job to raise:

```
RuntimeError: no running event loop
```

every time it fires. The error is logged but otherwise swallowed by APScheduler, so the application continues running normally.

**Observed in logs** (`/ecs/chat-magic-backend`):
```
ERROR - Job "lifespan.<locals>.<lambda> (trigger: interval[0:05:00], ...)" raised an exception
RuntimeError: no running event loop
```

---

## Impact

**Rate limiting: unaffected.** The `check_rate_limit` method already trims expired timestamps inline on every request (sliding window logic), so limits are correctly enforced regardless of this bug.

**Memory leak:** `_store` entries for inactive IPs are never removed. At current traffic levels this is negligible — each bucket is a small dict and ECS task recycling (e.g. on each deployment) resets memory to zero. It would only become a real concern at very high traffic with many unique IPs over a sustained period without any redeployment.

---

## The Fix

`AsyncIOScheduler` supports async job functions natively — there is no need for `asyncio.create_task()`. Replace the lambda with a direct reference to the coroutine function:

**Before (`backend/app/main.py` line 111–117):**
```python
scheduler.add_job(
    lambda: asyncio.create_task(rate_limit_svc.cleanup_stale_buckets()),
    "interval",
    seconds=settings.rate_limit_cleanup_interval,
    id="rate_limit_cleanup",
    replace_existing=True,
)
```

**After:**
```python
scheduler.add_job(
    rate_limit_svc.cleanup_stale_buckets,
    "interval",
    seconds=settings.rate_limit_cleanup_interval,
    id="rate_limit_cleanup",
    replace_existing=True,
)
```

This passes the coroutine function directly to `AsyncIOScheduler`, which schedules it on the event loop correctly.

Note: the `import asyncio` at the top of `main.py` can be removed after this change if it has no other usages.

---

## Testing

After applying the fix, verify in the logs that the job runs without error every 5 minutes:

```
INFO - Running job "cleanup_stale_buckets ..."
DEBUG - Rate limit cleanup: no stale buckets found   ← or INFO if buckets were pruned
```

The error lines should no longer appear.

---

## Deployment

Only the backend needs rebuilding:

```bash
cd /Users/angelaabbott/PycharmProjects/PythonProject
./deploy-backend.sh
```
