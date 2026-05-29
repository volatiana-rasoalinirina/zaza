# Zaza.io — Childcare Management Platform

> **"Zaza"** means *child* in Malagasy.

Zaza.io is a multi-tenant childcare SaaS platform built for French-speaking Africa and Madagascar. It enables daycare schools to manage children, daily activities, parent communication, and attendance — all in one place.

---

## Features

- **Multi-tenant architecture** — shared schema with `school_id` FK isolation on every model; no schema-per-tenant complexity
- **Role-based access control** — three roles: `Director`, `Teacher`, `Parent`, each with scoped permissions
- **Activity feed** — log CHECKIN, CHECKOUT, MEAL, NAP, NOTE, PHOTO events per child
- **Child management** — children grouped by pedagogical level (Garderie / TPS / PS / MS / GS), with allergy tracking
- **Contacts & authorized pickups** — per-child contacts with relation types, emergency flag, and pickup authorization
- **Parent access** — a parent account can span multiple schools via `ChildParent` pivot
- **Messaging** — per-child `Thread` with typed `Message` (text, image, file)
- **i18n** — French, English, and Malagasy (gettext + django-modeltranslation)
- **JWT authentication** — email-based login, no username

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6, Django REST Framework |
| Auth | `djangorestframework-simplejwt` |
| Database | PostgreSQL 16 |
| Cache / Queue | Redis 7, Celery |
| Storage | AWS S3 (planned) |
| Notifications | In-app (Celery async dispatch); WhatsApp + Resend email (planned) |
| Infrastructure | Docker, Docker Compose |
| Deploy | AWS EC2 + RDS + ElastiCache + ECR (planned) |
| CI/CD | GitHub Actions (planned) |
| Observability | Sentry + Prometheus + Grafana Cloud (planned) |
| API docs | drf-spectacular / Swagger + ReDoc |
| Rate limiting | DRF throttling (20/h anon, 1000/h user) |
| i18n | django-modeltranslation, gettext (FR / EN / MG) |

---

## Data Model

```
School           ── the tenant (slug, name)
User             ── AbstractUser with role: Director / Teacher / Parent
Group            ── pedagogical level (Garderie / TPS / PS / MS / GS)
Child            ── belongs to one School + one Group, has allergies[]
ChildParent      ── pivot: Child ↔ Parent (multi-school parent account)
ChildContact     ── authorized pickup / emergency contact (not a User)
Activity         ── CHECKIN | CHECKOUT | MEAL | NAP | NOTE | PHOTO
Thread           ── one per child, messaging entry point
Message          ── TEXT | IMAGE | FILE inside a Thread
```

### Permissions matrix

| Action | Director | Teacher | Parent |
|---|---|---|---|
| CRUD children | ✅ | ❌ | ❌ |
| Log activity | ✅ | ✅ | ❌ |
| View child feed | ✅ | ✅ (own group) | ✅ (own children) |
| Messaging | ✅ | ✅ | ✅ |
| Reports | ✅ | ❌ | ❌ |
| Manage school | ✅ | ❌ | ❌ |

---

## Notification Flow

Messages trigger async notifications routed by sender role:

```
Message saved
  └── post_save signal (notifications/signals.py)
        ├── sender is Parent          → dispatch_notification.delay(director)
        └── sender is Director/Teacher → dispatch_notification.delay(each parent of child)
              └── Celery task (notifications/tasks.py)
                    └── Notification created via dispatcher
```

This keeps the request/response cycle fast — the DB write and notification dispatch are fully decoupled.

---

## Project Structure

```
zaza/
├── apps/
│   ├── accounts/       # School, User, JWT auth, TenantMiddleware
│   ├── children/       # Child, Group, ChildParent, ChildContact
│   ├── activities/     # Activity feed (CHECKIN, CHECKOUT, MEAL…)
│   ├── messaging/      # Thread, Message
│   └── notifications/  # Notification model, signals, Celery async dispatch
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── celery.py
│   └── urls.py
├── requirements/
│   ├── base.txt
│   └── dev.txt
├── docker-compose.yml
└── Dockerfile
```

---

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Run locally

```bash
git clone https://github.com/volatiana-rasoalinirina/zaza.git
cd zaza

# Start PostgreSQL, Redis, and the Django dev server
docker compose up --build

# In a second terminal — run migrations and create a superuser
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

The API is available at `http://localhost:8000/`.

### Environment variables

Copy `.env.example` to `.env` and fill in the values (DB credentials, secret key, etc.). The `dev.py` settings read from environment variables or fall back to the Docker Compose defaults.

---

## Running Tests

```bash
docker compose exec web python manage.py test
```

---

## Roadmap

- [x] Celery async tasks for notifications
- [x] Swagger / ReDoc API documentation
- [ ] WhatsApp Business Cloud API integration
- [ ] Resend email notifications
- [ ] AWS deploy (EC2 + RDS + ElastiCache + S3)
- [ ] GitHub Actions CI/CD pipeline
- [ ] Sentry + Prometheus + Grafana observability
- [ ] DirectorSchool pivot (multi-site director accounts)

---

## Author

**Volatiana Rasoalinirina** — Senior Backend Engineer (Django / Python)
