# Build static frontend files
FROM node:26-alpine AS builder

WORKDIR /app

ENV NODE_ENV=production

# The frontend is served by the backend under `API_PREFIX` (e.g. `/api`), so
# the API base URL must match that prefix when no build arg is provided.
ARG VITE_API_BASE_URL=http://localhost:8400/api

COPY frontend .

RUN apk add pnpm && \
    CI=true pnpm install && \
    VITE_API_BASE_URL=${VITE_API_BASE_URL} pnpm build

# Build backend image that also serves frontend (stored in `/app/frontend-dist`)
FROM python:3.14-alpine3.22
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN rm -rf /var/cache/apk/*

COPY backend /app
WORKDIR /app

# -- Install dependencies:
RUN addgroup --system bracket && \
    adduser --system bracket --ingroup bracket && \
    chown -R bracket:bracket /app
USER bracket

RUN uv sync --no-dev --locked

COPY --from=builder --chown=bracket:bracket /app/dist /app/frontend-dist

EXPOSE 8400

HEALTHCHECK --interval=30s --timeout=5s --retries=5 --start-period=30s \
    CMD wget -O - http://0.0.0.0:8400/api/ping | grep -q '"ping"'

CMD [ \
    "uv", \
    "run", \
    "--no-dev", \
    "--locked", \
    "--", \
    "gunicorn", \
    "-k", \
    "uvicorn.workers.UvicornWorker", \
    "bracket.app:app", \
    "--bind", \
    "0.0.0.0:8400", \
    "--workers", \
    "1" \
]
