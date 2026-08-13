import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

st.set_page_config(page_title='Combustibles Chile', page_icon='', layout='wide')

# Diccionario de nombres legibles para los tipos de combustible
nombres_combustible = {
    '93': 'Gasolina 93 octanos',
    'A93': 'Gasolina 93 octanos (aditivada)',
    '95': 'Gasolina 95 octanos',
    'A95': 'Gasolina 95 octanos (aditivada)',
    '97': 'Gasolina 97 octanos',
    'A97': 'Gasolina 97 octanos (aditivada)',
    'DI': 'Petróleo Diésel',
    'ADI': 'Petróleo Diésel (aditivado)',
    'KE': 'Kerosene Doméstico',
    'AKE': 'Kerosene Doméstico (aditivado)',
    'GLP': 'Gas Licuado de Petróleo (GLP)',
    'GNC': 'Gas Natural Comprimido (GNC)',
}

# Conexión a Supabase
@st.cache_resource
def get_engine():
    connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?sslmode=require"
    return create_engine(connection_string)

engine = get_engine()

# Cargar datos en tiempo real desde Supabase
@st.cache_data(ttl=600)
def cargar_datos_actuales():
    query = """
    SELECT p.*, e.region, e.comuna, e.marca, e.razon_social, e.direccion, e.latitud, e.longitud
    FROM precios p
    JOIN estaciones e ON p.estacion_codigo = e.codigo
    WHERE p.fecha_captura >= NOW() - INTERVAL '30 days'
    """
    return pd.read_sql(query, engine)

df_actual = cargar_datos_actuales()

# Cargar histórico regional desde el CSV procesado
@st.cache_data
def cargar_historico():
    return pd.read_csv('data/processed/historico_precios_regional.csv', parse_dates=['Fecha'])

df_historico = cargar_historico()

orden_preferido = ['93', '95', '97', 'DI', 'A93', 'A95', 'A97', 'ADI', 'GLP', 'GNC', 'KE', 'AKE']
opciones_disponibles = [c for c in orden_preferido if c in df_actual['tipo_combustible'].unique()]

# ---------- Header: panel de precios estilo cartel de bencinera ----------
labels_cortos = {'93': 'G-93', '95': 'G-95', '97': 'G-97', 'DI': 'DIÉSEL', 'GLP': 'GLP'}
board_tipos = [t for t in ['93', '95', '97', 'DI', 'GLP'] if t in df_actual['tipo_combustible'].unique()]

precios_board = []
for t in board_tipos:
    df_t = df_actual[df_actual['tipo_combustible'] == t]
    df_t = df_t.sort_values('fecha_captura').drop_duplicates(subset='estacion_codigo', keep='last')
    precios_board.append((t, df_t['precio'].mean()))

boxes_html = ''.join(
    f'<div class="fh-box"><div class="fh-box-label">{labels_cortos.get(t, t)}</div>'
    f'<div class="fh-box-price">${p:,.0f}</div>'
    f'<div class="fh-box-unit">$/litro prom.</div></div>'
    for t, p in precios_board
)

n_estaciones = df_actual['estacion_codigo'].nunique()
n_regiones = df_actual['region'].nunique()
fecha_str = df_actual['fecha_captura'].max().strftime('%d-%m-%Y %H:%M')

header_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

.fh-wrap {{
    font-family: 'Space Grotesk', sans-serif;
    padding: 1.75rem 2rem 1.5rem 2rem;
    background: linear-gradient(180deg, #14181c 0%, #1a1e23 100%);
    border: 1px solid #262b31;
    border-top: 3px solid #ffb020;
    border-radius: 6px;
    margin-bottom: 1.75rem;
}}
.fh-eyebrow {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #ffb020;
    margin-bottom: 0.5rem;
}}
.fh-title {{
    font-size: 2.1rem;
    font-weight: 700;
    color: #ece9e4;
    margin: 0 0 0.4rem 0;
    line-height: 1.15;
}}
.fh-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #8b929a;
    margin-bottom: 1.4rem;
}}
.fh-board {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
}}
.fh-box {{
    font-family: 'JetBrains Mono', monospace;
    background: #0f1215;
    border: 1px solid #262b31;
    border-radius: 4px;
    padding: 0.55rem 1.1rem;
    min-width: 108px;
}}
.fh-box-label {{
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    color: #8b929a;
    text-transform: uppercase;
}}
.fh-box-price {{
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffb020;
}}
.fh-box-unit {{
    font-size: 0.62rem;
    color: #5c636b;
}}
.fh-rows-wrap {{
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 0.75rem;
}}
.fh-row {{
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #0f1215;
    border: 1px solid #262b31;
    border-radius: 4px;
    padding: 0.7rem 1.1rem;
    font-family: 'Space Grotesk', sans-serif;
}}
.fh-row-cheapest {{
    border-color: #ffb020;
    box-shadow: 0 0 0 1px #ffb02033 inset;
}}
.fh-rank {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #5c636b;
    width: 1.6rem;
    text-align: center;
    flex-shrink: 0;
}}
.fh-row-cheapest .fh-rank {{
    color: #ffb020;
    font-weight: 700;
}}
.fh-row-info {{
    flex: 1;
    min-width: 0;
}}
.fh-row-name {{
    font-size: 0.95rem;
    color: #ece9e4;
    font-weight: 500;
}}
.fh-row-address {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #8b929a;
    margin-top: 0.15rem;
}}
.fh-row-price {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffb020;
    white-space: nowrap;
}}
.fh-row-unit {{
    font-size: 0.65rem;
    color: #5c636b;
    font-weight: 400;
}}
.fh-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.08em;
    background: #ffb020;
    color: #14181c;
    padding: 0.1rem 0.4rem;
    border-radius: 2px;
    margin-left: 0.5rem;
    vertical-align: middle;
}}
</style>
<div class="fh-wrap">
    <div class="fh-eyebrow">Panel en vivo · Datos abiertos CNE</div>
    <div class="fh-title">Precios de combustibles en Chile</div>
    <div class="fh-sub">{n_estaciones:,} estaciones · {n_regiones} regiones · actualizado {fecha_str}</div>
    <div class="fh-board">
        {boxes_html}
    </div>
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)

# ---------- Navegación por tabs ----------
tab_buscar, tab_historico, tab_region, tab_marca, tab_mapa = st.tabs([
    ' Buscar más barata', ' Tendencia histórica', ' Por región', ' Por marca', ' Mapa'
])

# ---------- Tab: Buscar la más barata (filtro anidado región > comuna > octanaje) ----------
with tab_buscar:
    st.header('¿Dónde está más barata?')
    st.caption('Elegí región, comuna y tipo de combustible para ver las estaciones ordenadas de menor a mayor precio.')

    col_region, col_comuna, col_tipo = st.columns(3)

    with col_region:
        regiones_disp = sorted(df_actual['region'].dropna().unique())
        region_sel = st.selectbox('Región', regiones_disp, key='region_buscar')

    with col_comuna:
        comunas_disp = sorted(df_actual[df_actual['region'] == region_sel]['comuna'].dropna().unique())
        comuna_sel = st.selectbox('Comuna', comunas_disp)  # sin key fijo: se recalcula si cambia la región

    with col_tipo:
        tipo_sel = st.selectbox(
            'Tipo de combustible',
            opciones_disponibles,
            format_func=lambda codigo: nombres_combustible.get(codigo, codigo),
            key='tipo_buscar'
        )

    df_busqueda = df_actual[
        (df_actual['region'] == region_sel) &
        (df_actual['comuna'] == comuna_sel) &
        (df_actual['tipo_combustible'] == tipo_sel)
    ]
    df_busqueda = df_busqueda.sort_values('fecha_captura').drop_duplicates(subset='estacion_codigo', keep='last')
    df_busqueda = df_busqueda.sort_values('precio', ascending=True).reset_index(drop=True)

    if df_busqueda.empty:
        st.warning(f"No hay datos de {nombres_combustible.get(tipo_sel, tipo_sel)} en {comuna_sel} en los últimos 30 días.")
    else:
        filas_html = ''
        for idx, fila in df_busqueda.iterrows():
            es_mas_barata = idx == 0
            row_class = 'fh-row fh-row-cheapest' if es_mas_barata else 'fh-row'
            badge = '<span class="fh-badge">MÁS BARATA</span>' if es_mas_barata else ''
            marca = fila['marca'] if pd.notna(fila['marca']) else 'Sin marca registrada'
            direccion = fila['direccion'] if pd.notna(fila['direccion']) else 'Dirección no disponible'
            razon_social = fila['razon_social'] if pd.notna(fila['razon_social']) else ''
            filas_html += (
                f'<div class="{row_class}"><div class="fh-rank">{idx + 1}</div>'
                f'<div class="fh-row-info"><div class="fh-row-name">{marca}{badge}</div>'
                f'<div class="fh-row-address">{direccion} · {razon_social}</div></div>'
                f'<div class="fh-row-price">${fila["precio"]:,.0f}<span class="fh-row-unit"> /L</span></div></div>'
            )

        st.markdown(f'<div class="fh-rows-wrap">{filas_html}</div>', unsafe_allow_html=True)
        st.caption(f'{len(df_busqueda)} estación(es) encontradas en {comuna_sel}, {region_sel}.')

# ---------- Tab: Tendencia histórica nacional ----------
with tab_historico:
    st.header('Tendencia histórica nacional (1994-2026)')

    tipo_seleccionado = st.selectbox(
        'Tipo de combustible',
        df_historico['tipo_combustible'].unique(),
        format_func=lambda codigo: nombres_combustible.get(codigo, codigo),
        key='tipo_historico'
    )

    año_min = int(df_historico['Fecha'].dt.year.min())
    año_max = int(df_historico['Fecha'].dt.year.max())

    rango_años = st.slider(
        'Rango de años',
        min_value=año_min,
        max_value=año_max,
        value=(año_min, año_max)
    )

    df_hist_filtrado = df_historico[
        (df_historico['tipo_combustible'] == tipo_seleccionado) &
        (df_historico['Fecha'].dt.year >= rango_años[0]) &
        (df_historico['Fecha'].dt.year <= rango_años[1])
    ]

    promedio_nacional = df_hist_filtrado.groupby('Fecha')['precio'].mean().reset_index()

    fig_historico = px.line(
        promedio_nacional,
        x='Fecha',
        y='precio',
        labels={'precio': 'Precio promedio ($/litro)', 'Fecha': ''},
    )
    fig_historico.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig_historico, use_container_width=True)

# ---------- Tab: Precio actual por región ----------
with tab_region:
    st.header('Precio actual por región')

    tipo_actual = st.selectbox(
        'Tipo de combustible',
        opciones_disponibles,
        format_func=lambda codigo: nombres_combustible.get(codigo, codigo),
        key='tipo_actual'
    )

    df_ultimo = df_actual[df_actual['tipo_combustible'] == tipo_actual]
    df_ultimo = df_ultimo.sort_values('fecha_captura').drop_duplicates(subset='estacion_codigo', keep='last')

    precio_por_region = df_ultimo.groupby('region')['precio'].mean().sort_values(ascending=False)

    fig_region = px.bar(
        x=precio_por_region.values,
        y=precio_por_region.index,
        orientation='h',
        labels={'x': 'Precio promedio ($/litro)', 'y': ''},
        color_discrete_sequence=['#4C78A8']
    )
    fig_region.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=600,
    )
    st.plotly_chart(fig_region, use_container_width=True)

    region_mas_cara = precio_por_region.index[0]
    region_mas_barata = precio_por_region.index[-1]
    diferencia = precio_por_region.iloc[0] - precio_por_region.iloc[-1]

    st.info(f"""
    **Hallazgo:** Para {nombres_combustible.get(tipo_actual, tipo_actual)}, {region_mas_cara}
    tiene el precio promedio más alto (\${precio_por_region.iloc[0]:,.0f}/litro),
    mientras que {region_mas_barata} tiene el más bajo
    (\${precio_por_region.iloc[-1]:,.0f}/litro) — una diferencia de
    \${diferencia:,.0f} por litro entre ambas regiones.
    """)

# ---------- Tab: Precio actual por marca ----------
with tab_marca:
    st.header('Precio actual por marca')

    tipo_marca = st.selectbox(
        'Tipo de combustible',
        opciones_disponibles,
        format_func=lambda codigo: nombres_combustible.get(codigo, codigo),
        key='tipo_marca'
    )

    df_marca_filtrado = df_actual[df_actual['tipo_combustible'] == tipo_marca]
    df_marca_filtrado = df_marca_filtrado.sort_values('fecha_captura').drop_duplicates(subset='estacion_codigo', keep='last')

    precio_por_marca = df_marca_filtrado.groupby('marca')['precio'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    precio_por_marca.columns = ['precio_promedio', 'n_estaciones']

    top10_caras = precio_por_marca.head(10)

    fig_marca = px.bar(
        x=top10_caras['precio_promedio'],
        y=top10_caras.index,
        orientation='h',
        labels={'x': 'Precio promedio ($/litro)', 'y': ''},
        color_discrete_sequence=['#59A14F']
    )
    fig_marca.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450,
    )
    st.plotly_chart(fig_marca, use_container_width=True)

    marca_mas_cara = precio_por_marca.index[0]
    marca_mas_barata = precio_por_marca.index[-1]


    with st.expander('Ver tabla completa de todas las marcas'):
        st.dataframe(
            precio_por_marca.rename(columns={'precio_promedio': 'Precio promedio ($/litro)', 'n_estaciones': 'N° estaciones'}),
            use_container_width=True
        )
    st.info(f"""
            **Hallazgo:** Entre las {len(precio_por_marca)} marcas con estaciones registradas,
            {marca_mas_cara} tiene el precio promedio más alto para
            {nombres_combustible.get(tipo_marca, tipo_marca)}, mientras que {marca_mas_barata}
            tiene el más bajo.
            """)

# ---------- Tab: Mapa de estaciones ----------
with tab_mapa:
    st.header('Mapa de estaciones')

    tipo_mapa = st.selectbox(
        'Tipo de combustible',
        opciones_disponibles,
        format_func=lambda codigo: nombres_combustible.get(codigo, codigo),
        key='tipo_mapa'
    )

    df_mapa = df_actual[df_actual['tipo_combustible'] == tipo_mapa]
    df_mapa = df_mapa.sort_values('fecha_captura').drop_duplicates(subset='estacion_codigo', keep='last')
    df_mapa = df_mapa.dropna(subset=['latitud', 'longitud'])

    fig_mapa = px.scatter_mapbox(
        df_mapa,
        lat='latitud',
        lon='longitud',
        color='precio',
        hover_name='razon_social',
        hover_data={'comuna': True, 'marca': True, 'precio': ':.0f', 'latitud': False, 'longitud': False},
        color_continuous_scale='RdYlGn_r',
        zoom=3,
        height=600,
    )
    fig_mapa.update_layout(
        mapbox_style='carto-darkmatter',
        margin=dict(l=0, r=0, t=0, b=0),
    )
    st.plotly_chart(fig_mapa, use_container_width=True)