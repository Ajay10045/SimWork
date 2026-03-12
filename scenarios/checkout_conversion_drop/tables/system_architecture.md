# FoodDash System Architecture

## Overview

FoodDash is a food delivery platform built on a microservice architecture running on AWS. The system consists of 6 core microservices, a PostgreSQL database cluster, Redis caching layer, and integrations with external payment and notification providers.

**Infrastructure:** AWS (ECS for container orchestration, RDS for PostgreSQL, ElastiCache for Redis, CloudFront CDN for static assets and images)

---

## Services

### 1. Catalog Service
- **Purpose:** Manages restaurant listings, menus, categories, and item availability
- **Stack:** Python (FastAPI), PostgreSQL
- **Port:** 8001
- **Dependencies:** PostgreSQL (RDS), Redis (ElastiCache), CloudFront CDN (images)
- **Owner:** Sarah Chen

### 2. Search Service
- **Purpose:** Restaurant and menu item search, ranking, and recommendations
- **Stack:** Python (FastAPI), Elasticsearch
- **Port:** 8002
- **Dependencies:** Elasticsearch cluster, Catalog Service (for index updates)
- **Owner:** Emily Wong

### 3. User Service
- **Purpose:** User authentication, profiles, preferences, and session management
- **Stack:** Node.js (Express), PostgreSQL
- **Port:** 8003
- **Dependencies:** PostgreSQL (RDS), Redis (session cache)
- **Owner:** Alex Kumar

### 4. Checkout Service
- **Purpose:** Shopping cart management, order creation, checkout flow orchestration
- **Stack:** Python (FastAPI), PostgreSQL
- **Port:** 8004
- **Dependencies:** Payment Service, Catalog Service, User Service, PostgreSQL (RDS)
- **Owner:** Lisa Taylor

### 5. Payment Service
- **Purpose:** Payment processing, refunds, transaction management
- **Stack:** Java (Spring Boot), PostgreSQL
- **Port:** 8005
- **Dependencies:** External PayStream API (payment gateway), PostgreSQL (RDS)
- **Owner:** David Park
- **Note:** Recently migrated from PayStream v2 to PayStream v3 API (January 10, 2025)

### 6. Notification Service
- **Purpose:** Push notifications, email, and SMS delivery
- **Stack:** Node.js (Express), Redis (queue)
- **Port:** 8006
- **Dependencies:** AWS SES (email), Firebase Cloud Messaging (push), Twilio (SMS)
- **Owner:** Mike Johnson

---

## Service Dependency Diagram

```
                    ┌─────────────┐
                    │   Client    │
                    │ (iOS/Android│
                    │    /Web)    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  API Gateway │
                    │  (AWS ALB)   │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────────┐
          │                │                    │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────────▼────────┐
    │  Catalog   │   │  Search   │   │   User Service   │
    │  Service   │   │  Service  │   │                  │
    └─────┬─────┘   └─────┬─────┘   └─────────┬────────┘
          │               │                    │
          │         ┌─────┘                    │
          │         │                          │
    ┌─────▼─────────▼──────────────────────────▼───┐
    │              Checkout Service                  │
    │      (cart management, order creation)         │
    └─────────────────────┬────────────────────────┘
                          │
                    ┌─────▼──────┐
                    │  Payment   │
                    │  Service   │
                    └─────┬──────┘
                          │
                    ┌─────▼──────────┐
                    │  PayStream API  │
                    │  (External)     │
                    │  v2 → v3        │
                    └─────┬──────────┘
                          │
                    ┌─────▼──────┐
                    │    Bank /   │
                    │  Card Issuer│
                    └────────────┘

    ┌──────────────────┐
    │  Notification     │  (triggered by Checkout Service
    │  Service          │   after order events)
    └──────────────────┘
```

---

## Payment Flow (Detailed)

The payment flow is the critical path for order completion:

```
1. User taps "Pay Now" in the app
      │
2. Client → Checkout Service: POST /api/v1/orders/{id}/pay
      │
3. Checkout Service → Payment Service: POST /api/v1/payments/process
      │
4. Payment Service → PayStream Gateway: POST /v3/transactions
   (Previously: POST /v2/transactions — migrated Jan 10, 2025)
      │
5. PayStream → Bank/Card Issuer: Authorization request
      │
6. Bank → PayStream → Payment Service → Checkout Service → Client
   (Response propagates back through the chain)
```

**Timeout Configuration:**
- Client → Checkout Service: 30s timeout
- Checkout Service → Payment Service: 15s timeout
- Payment Service → PayStream: 10s timeout (was 5s, increased Jan 14 hotfix)

**Payment Methods Supported:**
- Credit Card (all platforms)
- Apple Pay (iOS only — routes through iOS PayStream SDK)
- Google Pay (Android only — routes through Android PayStream SDK)
- PayPal (all platforms — routes through PayPal API, not PayStream)

---

## Database

- **PostgreSQL 15** on AWS RDS (Multi-AZ deployment)
- **Primary instance:** db.r6g.xlarge
- **Read replicas:** 2 (us-east-1b, us-east-1c)
- **Key tables:** users, restaurants, menu_items, orders, order_items, payments, sessions

---

## Caching

- **Redis 7** on AWS ElastiCache
- **Cluster mode:** Enabled (3 shards)
- **Use cases:**
  - User session data (TTL: 24h)
  - Restaurant menu cache (TTL: 15min)
  - Search results cache (TTL: 5min)
  - Rate limiting

---

## CDN

- **AWS CloudFront** for static asset delivery
- Restaurant images, menu item photos
- Recently migrated image storage to CloudFront (Jan 25, 2025)

---

## Monitoring & Observability

- **Metrics:** Datadog (service latency, error rates, throughput)
- **Logging:** AWS CloudWatch Logs → Elasticsearch
- **Tracing:** Datadog APM (distributed tracing across services)
- **Alerting:** PagerDuty integration for critical alerts

---

## Recent Changes

| Date | Service | Change |
|------|---------|--------|
| Dec 18 | Catalog | Added restaurant category filters |
| Dec 28 | Catalog | Image CDN optimization |
| Jan 5 | Search | New ranking algorithm |
| Jan 8 | Search | Index rebuild with new schema |
| **Jan 10** | **Payment** | **Migrated to PayStream v3 payment gateway** |
| Jan 14 | Payment | Hotfix: increased PayStream timeout 5s → 10s |
| Jan 20 | Payment | Added retry logic for timeout errors |
| Jan 25 | Catalog | CloudFront CDN migration |
