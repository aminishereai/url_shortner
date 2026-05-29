# URL Shortener API

> A production-ready REST API that maps long URLs to short, shareable codes — built with FastAPI, Redis, and Docker Compose.

-----

## The Problem

Long URLs are ugly, break in emails, and blow past character limits on social platforms.
This API solves that by accepting any URL and returning a short code (e.g. `go.io/xK3pQz`) that permanently redirects to the original. It’s the same core problem Bitly, TinyURL, and every link-in-bio tool solves — rebuilt from scratch to understand what actually happens under the hood.

-----

## Tech Stack

|Technology             |Why                                                                                                             |
|-----------------------|----------------------------------------------------------------------------------------------------------------|
|**FastAPI**            |Async-native Python web framework; generates OpenAPI docs automatically; type-safe request/response via Pydantic|
|**Redis**              |Sub-millisecond key-value lookups; a short code → URL mapping is a perfect fit; TTL support built in            |
|**aioredis / redis-py**|Async Redis client so the event loop never blocks on I/O                                                        |
|**Docker Compose**     |One command to spin up the full stack; Redis and the API run in isolated containers with a shared network       |
|**python-json-logger** |Structured JSON logs — parseable by Datadog, Loki, CloudWatch out of the box                                    |

-----

## Architecture

```
Client
  │
  ▼
FastAPI (uvicorn)          ← validates input, encodes/decodes short codes
  │                          returns RFC 7807 errors on bad input
  │   connection pool
  ▼
Redis                      ← stores short_code → original_url mappings
  │                          optional TTL per key
  ▼
Docker network (bridge)    ← api + redis containers; Redis never exposed publicly
```

Short code generation uses **base62 encoding** of an MD5/SHA hash of the original URL. This is deterministic — submitting the same URL twice returns the same code (idempotent).

-----

## API Endpoints

|Method|Endpoint               |Description                         |Request Body                    |Response                                                       |
|------|-----------------------|------------------------------------|--------------------------------|---------------------------------------------------------------|
|`POST`|`/shorten`             |Shorten a URL                       |`{"url": "https://example.com"}`|`{"short_code": "xK3pQz", "short_url": "https://go.io/xK3pQz"}`|
|`GET` |`/{short_code}`        |Redirect to original URL            |—                               |`HTTP 307` to original URL                                     |
|`GET` |`/resolve/{short_code}`|Get original URL without redirecting|—                               |`{"original_url": "https://example.com"}`                      |
|`GET` |`/health`              |Service health check                |—                               |`{"status": "ok", "redis": "connected"}`                       |

**Error format (RFC 7807):**

```json
{
  "type": "https://example.com/errors/invalid-url",
  "title": "Invalid URL",
  "status": 422,
  "detail": "URL must begin with http:// or https://",
  "instance": "/shorten"
}
```

-----

## Getting Started

**Prerequisites:** Docker and Docker Compose installed.

```bash
# 1. Clone the repo
git clone https://github.com/aminishereai/url_shortner.git
cd url_shortner

# 2. Start the full stack
docker compose up --build

# 3. The API is now running at:
#    http://localhost:8000
#    Swagger UI: http://localhost:8000/docs

# 4. Shorten your first URL
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/aminishereai/url_shortner"}'

# 5. Follow the redirect
curl -L http://localhost:8000/{short_code}
```

**Run without Docker (local dev):**

```bash
pip install uv
uv sync
uvicorn app.main:app --reload
```

-----

## Design Decisions

**1. Base62 encoding over random IDs**
Short codes are derived by taking the first 7 characters of a base62-encoded MD5 hash of the original URL. This gives 62⁷ ≈ 3.5 trillion possible codes — enough for any real-world use — and makes the operation idempotent. Submitting `https://google.com` twice returns the same code, which avoids bloating Redis with duplicates.

**2. Redis connection pooling**
A single `ConnectionPool` is created at startup (via FastAPI’s `lifespan` context) and shared across all requests. Without pooling, each request would open and close its own TCP connection to Redis, which is expensive under load. With a pool of 10 connections, the application handles concurrent requests efficiently without connection exhaustion.

**3. RFC 7807 error responses**
All errors — invalid URL, missing short code, Redis timeout — return a structured JSON body following the RFC 7807 “Problem Details” spec. This means clients (mobile apps, frontend, third-party integrations) always get machine-readable errors with a consistent shape, not inconsistent HTML 500 pages or ad-hoc JSON.

**4. URL validation before storage**
Input is validated with Pydantic’s `HttpUrl` type, which enforces a valid scheme (`http://` or `https://`), a parseable host, and rejects empty strings. This prevents garbage data from entering Redis and closes off a class of redirect-to-localhost / SSRF-adjacent abuse where attackers submit `http://169.254.169.254/` (AWS metadata endpoint) or `file:///etc/passwd` as the target URL.

-----

## What I Learned

*(Written by Amin Giri)*

Building this felt like peeling an onion — every layer revealed another thing I hadn’t thought about.

I thought a URL shortener was a weekend project. It technically is, but making it *not embarrassing in production* took a lot longer. The first version had Redis initialized inside the route handler. Every request opened a new connection. Under any real load, that would exhaust file descriptors and crash. Learning about connection pools — and why they exist — was probably the most practically useful thing from this project.

The RFC 7807 error format was new to me. I was just returning `{"error": "invalid url"}` before. Reading the spec made me realize that error handling isn’t just about the happy path — it’s an API contract that downstream consumers depend on. A machine can’t meaningfully parse `"something went wrong"`.

I also learned that `aioredis` as a standalone package is deprecated since `redis-py` 4.2 absorbed async support. I had both in my dependencies — a redundancy I only caught while reading the changelog. Details like that matter when you’re maintaining a production service.

The hardest part wasn’t the code. It was resisting the urge to add features (custom codes, analytics, expiry UI) before the foundation was solid. Scope creep is real even on personal projects.

-----

## Project Status

This is **Project 1 of 7** in a backend mastery roadmap. The goal is to build progressively more complex systems — each one using real infrastructure (Redis, Postgres, queues, etc.) rather than toy in-memory stores.

-----

*Built by [Amin Giri](https://github.com/aminishereai) · Nepal · 2026*