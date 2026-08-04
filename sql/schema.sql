-- Esquema de base de datos: combustibles-cl
-- Fuente: API CNE (api.cne.cl) - GET /api/v4/estaciones

-- Tabla de estaciones: datos que cambian poco (identidad y ubicación).
-- Se actualiza vía "upsert" (insertar si es nueva, actualizar si cambió algo).
CREATE TABLE estaciones (
    codigo VARCHAR(20) PRIMARY KEY,
    razon_social TEXT,
    marca VARCHAR(50),
    region VARCHAR(50),
    codigo_region VARCHAR(5),
    comuna VARCHAR(50),
    codigo_comuna VARCHAR(10),
    direccion TEXT,
    latitud NUMERIC(10,7),
    longitud NUMERIC(10,7)
);

-- Tabla de precios: histórico. Cada ejecución del pipeline de n8n agrega
-- filas nuevas (una por cada combustible de cada estación), sin modificar
-- las filas anteriores. Así se construye el dataset histórico con el tiempo.
CREATE TABLE precios (
    id SERIAL PRIMARY KEY,
    estacion_codigo VARCHAR(20) REFERENCES estaciones(codigo),
    tipo_combustible VARCHAR(10),
    precio NUMERIC(10,2),
    unidad_cobro VARCHAR(10),
    fecha_actualizacion_api DATE,   -- cuándo la estación reportó el precio a la CNE
    hora_actualizacion_api TIME,
    fecha_captura TIMESTAMP DEFAULT NOW()  -- cuándo nuestro pipeline capturó el dato
);

-- Índices para consultas frecuentes (filtrar por estación o por fecha de captura)
CREATE INDEX idx_precios_estacion ON precios(estacion_codigo);
CREATE INDEX idx_precios_fecha_captura ON precios(fecha_captura);
