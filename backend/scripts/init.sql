-- GanitMitra — Database Initialization
-- Run on first PostgreSQL container start

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create Langfuse database (if using self-hosted)
-- Uncomment if running Langfuse on same Postgres:
-- CREATE DATABASE langfuse OWNER ganitmitra;
