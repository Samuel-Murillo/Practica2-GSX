-- ============================================================================
-- init.sql — Script de inicialización de PostgreSQL
-- Práctica 2 GSX | Semana 9
--
-- Se ejecuta AUTOMÁTICAMENTE en el primer arranque del contenedor de PostgreSQL.
-- Crea el esquema inicial de la base de datos de GreenDevCorp.
-- ============================================================================

-- Extensión para UUIDs como primary keys (más seguro que IDs secuenciales)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Tabla de servicios de la empresa ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS services (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    status      VARCHAR(20) NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'inactive', 'maintenance')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Tabla de infraestructura ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS infrastructure (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component   VARCHAR(100) NOT NULL,
    version     VARCHAR(20),
    environment VARCHAR(20) NOT NULL DEFAULT 'production'
                CHECK (environment IN ('development', 'staging', 'production')),
    deployed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Datos iniciales de demostración ──────────────────────────────────────
INSERT INTO services (name, description, status) VALUES
    ('Backend API',       'FastAPI REST API — Servicio principal',      'active'),
    ('Frontend Dashboard','Panel de control web de GreenDevCorp',       'active'),
    ('Nginx Proxy',       'Reverse proxy y punto de entrada del sistema','active')
ON CONFLICT DO NOTHING;

INSERT INTO infrastructure (component, version, environment) VALUES
    ('Docker',      '26.x',  'production'),
    ('PostgreSQL',  '15.x',  'production'),
    ('FastAPI',     '0.111', 'production'),
    ('Nginx',       '1.27',  'production')
ON CONFLICT DO NOTHING;

-- Comentario de auditoría
COMMENT ON TABLE services IS 'Registro de servicios activos de GreenDevCorp';
COMMENT ON TABLE infrastructure IS 'Inventario de componentes de infraestructura';
