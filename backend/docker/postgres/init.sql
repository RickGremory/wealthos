-- WealthOS local bootstrap (runs once on first Postgres volume init).
-- Keep idempotent and free of application schema (Alembic owns migrations).

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
