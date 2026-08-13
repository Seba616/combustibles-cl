# Precios de Combustibles en Chile — Pipeline Automatizado

Dashboard interactivo que combina un pipeline de datos en tiempo real (vía
n8n) con una serie histórica de referencia, para analizar el precio de los
combustibles vehiculares en Chile — a nivel de estación de servicio,
región, comuna y marca.

**🔗 Ver el dashboard en vivo:** [PENDIENTE — actualizar tras el deploy]

---

## Sobre el proyecto

Proyecto de portafolio enfocado en **ingeniería de datos y automatización**,
complementando el enfoque de análisis/BI del proyecto hermano
[`gasto-publico-cl`](https://github.com/Seba616/gasto-publico-cl). Cubre el
flujo completo: consumo de una API con autenticación, orquestación con n8n,
almacenamiento histórico en PostgreSQL, y un dashboard que combina esa fuente
en vivo con un dataset histórico oficial de largo plazo.

Para el detalle completo de objetivo, alcance, decisiones técnicas y
arquitectura, ver [PROJECT.md](PROJECT.md).

## Preguntas de negocio respondidas

1. ¿Dónde está el combustible más barato ahora mismo, en mi región/comuna?
2. ¿Cómo ha evolucionado el precio a nivel nacional en el largo plazo (1994-2026)?
3. ¿Cómo varían los precios entre regiones?
4. ¿Qué marcas/distribuidores tienden a tener precios más altos o más bajos?
5. ¿Dónde están geográficamente las estaciones, y cómo se distribuye el precio en el mapa?

## Arquitectura

```
[API CNE] → [n8n: login + fetch programado] → [PostgreSQL (Supabase)] → [Dashboard Streamlit]
                                                        ↑
                              [Histórico regional CNE, 1994-2026] → [ETL en pandas] → [CSV procesado]
```

El pipeline de n8n corre de forma recurrente (cada 2 horas, más una
ejecución al iniciar la instancia), construyendo un dataset histórico
propio a partir de las ~1.800 estaciones de servicio del país. El dashboard
combina esta fuente en tiempo real con un dataset histórico oficial de la
CNE (precio promedio regional mensual desde 1994), procesado una única vez
mediante un ETL en pandas.

## Tecnologías

- **n8n** (self-hosted vía Docker) — orquestación del pipeline: login,
  consumo de API, transformación, escritura en base de datos
- **PostgreSQL (Supabase)** — almacenamiento histórico de precios por
  estación
- **Python + pandas** — ETL del dataset histórico regional (Excel → CSV limpio)
- **Streamlit + Plotly** — dashboard interactivo
- **SQLAlchemy / psycopg2** — conexión del dashboard a la base de datos
- **Fuente de datos:** [API CNE](https://api.cne.cl) (precios en línea por
  estación) y [Estadísticas de Hidrocarburos CNE](https://www.cne.cl/estadisticas/hidrocarburo/)
  (histórico regional)

## Estructura del repositorio

```
combustibles-cl/
├── data/
│   ├── raw/                          # Excel histórico original (CNE)
│   └── processed/                    # histórico regional ya limpio (CSV)
├── docs/                             # export del workflow de n8n (ignorado por git)
├── notebooks/
│   ├── 01_exploracion.ipynb          # exploración del Excel histórico
│   └── 02_etl_historico.ipynb        # ETL documentado paso a paso
├── sql/
│   └── schema.sql                    # esquema de las tablas estaciones/precios
├── app.py                            # dashboard de Streamlit
├── requirements.txt
├── PROJECT.md                        # definición completa del proyecto
└── README.md
```

## Cómo correrlo localmente

```bash
git clone https://github.com/Seba616/combustibles-cl.git
cd combustibles-cl
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Creá un archivo `.env` en la raíz con las credenciales de tu propia base de
datos PostgreSQL:

```
DB_HOST=...
DB_PORT=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
```

Luego:

```bash
streamlit run app.py
```

**Nota:** el pipeline de n8n (que alimenta la tabla `precios`) no está
incluido para correr automáticamente al clonar el repo — el workflow se
administra por separado en una instancia de n8n (self-hosted vía Docker).
El esquema de base de datos necesario está en [`sql/schema.sql`](sql/schema.sql).

## Principales hallazgos

- El precio de los combustibles muestra variaciones notables entre
  regiones, con diferencias de varios cientos de pesos por litro entre la
  región más cara y la más barata para un mismo tipo de combustible.
- El histórico de largo plazo (1994-2026) muestra la evolución del precio
  de referencia nacional, disponible para explorar por tipo de combustible
  y rango de años en el dashboard.
- Existen variantes "aditivadas" de cada tipo de gasolina/diésel, vendidas
  a un precio distinto de la versión base — un detalle no siempre evidente
  para el usuario final.

Detalle completo, con gráficos y filtros interactivos, disponible en el
dashboard en vivo.
