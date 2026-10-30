import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from io import StringIO


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

st.set_page_config(
    page_title="Sales Analytics | Control Anual",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# DISEÑO CORPORATIVO
# ==========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
    }

    [data-testid="stSidebar"] {
        background-color: #10243A;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #10243A;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 15px;
        color: #65758B;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 700;
        color: #10243A;
        margin-top: 15px;
        margin-bottom: 12px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E0E7F0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 7px rgba(16, 36, 58, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #65758B;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #10243A;
        font-weight: 800;
    }

    .info-box {
        background-color: white;
        border-left: 5px solid #2878D0;
        padding: 15px;
        border-radius: 7px;
        color: #34465A;
        margin-bottom: 15px;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================================
# CONFIGURACIÓN DE MESES Y DATOS INICIALES
# ==========================================================

MESES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre"
]

DATOS_INICIALES = pd.DataFrame({
    "Mes": MESES,
    "Ventas": [0.0] * 12,
    "Meta": [10000.0] * 12
})


# ==========================================================
# FUNCIONES AUXILIARES
# ==========================================================

def formato_dinero(valor, simbolo):
    """Devuelve un importe con formato monetario."""
    return f"{simbolo} {valor:,.2f}"


def preparar_datos(df):
    """Limpia y valida los datos numéricos de ventas."""

    resultado = df.copy()

    resultado["Ventas"] = pd.to_numeric(
        resultado["Ventas"], errors="coerce"
    ).fillna(0).clip(lower=0)

    resultado["Meta"] = pd.to_numeric(
        resultado["Meta"], errors="coerce"
    ).fillna(0).clip(lower=0)

    return resultado


def calcular_cumplimiento(ventas, meta):
    """Calcula el cumplimiento de la meta sin dividir entre cero."""

    if meta <= 0:
        return 0.0

    return ventas / meta * 100


# ==========================================================
# ENCABEZADO
# ==========================================================

st.markdown(
    '<div class="main-title">SALES ANALYTICS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Sistema de control, seguimiento y análisis de ventas anuales'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="info-box">
    <b>Panel de control comercial</b><br>
    Edita las ventas y las metas mensuales directamente en la tabla.
    Los indicadores y gráficos se recalcularán automáticamente.
</div>
""", unsafe_allow_html=True)


# ==========================================================
# BARRA LATERAL
# ==========================================================

with st.sidebar:

    st.markdown("# SALES ANALYTICS")
    st.markdown("### Configuración")

    anio = st.selectbox(
        "Año de análisis",
        options=list(range(2024, 2036)),
        index=list(range(2024, 2036)).index(2026)
    )

    moneda = st.selectbox(
        "Moneda",
        options={
            "Soles peruanos (PEN)": "S/",
            "Dólares estadounidenses (USD)": "$",
            "Euros (EUR)": "€"
        }.keys()
    )

    simbolo = {
        "Soles peruanos (PEN)": "S/",
        "Dólares estadounidenses (USD)": "$",
        "Euros (EUR)": "€"
    }[moneda]

    st.markdown("---")

    st.markdown("### Visualización")

    tipo_grafico = st.selectbox(
        "Tipo de gráfico",
        [
            "Barras",
            "Líneas",
            "Área",
            "Barras y metas"
        ]
    )

    mostrar_meta = st.checkbox(
        "Mostrar línea de meta",
        value=True
    )

    mostrar_etiquetas = st.checkbox(
        "Mostrar valores en el gráfico",
        value=True
    )

    st.markdown("---")

    st.caption(
        "Los cambios se mantienen durante la sesión actual. "
        "Descarga tus datos para conservar una copia."
    )


# ==========================================================
# INICIALIZAR DATOS EN LA SESIÓN
# ==========================================================

if "ventas_anuales" not in st.session_state:

    st.session_state.ventas_anuales = DATOS_INICIALES.copy()


# ==========================================================
# RESTABLECER DATOS
# ==========================================================

col_info, col_reset = st.columns([5, 1])

with col_info:
    st.markdown(
        '<div class="section-title">Registro mensual de ventas</div>',
        unsafe_allow_html=True
    )

with col_reset:
    if st.button(
        "Restablecer",
        help="Restablece las ventas a cero y las metas a 10 000."
    ):
        st.session_state.ventas_anuales = DATOS_INICIALES.copy()

        if "tabla_ventas" in st.session_state:
            del st.session_state["tabla_ventas"]

        st.rerun()


# ==========================================================
# TABLA EDITABLE
# ==========================================================

st.caption(
    "Haz clic en cualquier celda de Ventas o Meta para editar su valor."
)

datos_editados = st.data_editor(
    st.session_state.ventas_anuales,
    key="tabla_ventas",
    hide_index=True,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "Mes": st.column_config.TextColumn(
            "Mes",
            disabled=True,
            width="medium"
        ),
        "Ventas": st.column_config.NumberColumn(
            "Ventas reales",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            help="Importe vendido durante el mes."
        ),
        "Meta": st.column_config.NumberColumn(
            "Meta mensual",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            help="Objetivo de ventas establecido para el mes."
        )
    }
)

datos = preparar_datos(datos_editados)

st.session_state.ventas_anuales = datos.copy()


# ==========================================================
# INDICADORES KPI
# ==========================================================

total_ventas = datos["Ventas"].sum()
total_metas = datos["Meta"].sum()

promedio_mensual = total_ventas / 12

cumplimiento_anual = calcular_cumplimiento(
    total_ventas,
    total_metas
)

if total_ventas > 0:
    mejor_indice = datos["Ventas"].idxmax()
    mejor_mes = datos.loc[mejor_indice, "Mes"]
    mejor_venta = datos.loc[mejor_indice, "Ventas"]
else:
    mejor_mes = "Sin ventas"
    mejor_venta = 0.0

diferencia_meta = total_ventas - total_metas


# ==========================================================
# TARJETAS DE INDICADORES
# ==========================================================

st.markdown(
    '<div class="section-title">Indicadores principales</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Ventas acumuladas",
    formato_dinero(total_ventas, simbolo)
)

k2.metric(
    "Promedio mensual",
    formato_dinero(promedio_mensual, simbolo)
)

k3.metric(
    "Mejor mes",
    mejor_mes,
    delta=formato_dinero(mejor_venta, simbolo)
)

k4.metric(
    "Cumplimiento anual",
    f"{cumplimiento_anual:.2f}%",
    delta=f"{diferencia_meta:,.2f} respecto a la meta"
)

st.markdown("")


# ==========================================================
# ANÁLISIS DE CUMPLIMIENTO
# ==========================================================

st.markdown(
    '<div class="section-title">Cumplimiento de objetivos</div>',
    unsafe_allow_html=True
)

if total_metas > 0:

    st.progress(
        min(max(cumplimiento_anual / 100, 0.0), 1.0)
    )

    if cumplimiento_anual >= 100:
        st.success(
            f"Meta anual alcanzada: {cumplimiento_anual:.2f}%."
        )
    else:
        pendiente = total_metas - total_ventas

        st.warning(
            f"Cumplimiento actual: {cumplimiento_anual:.2f}%. "
            f"Faltan {formato_dinero(max(pendiente, 0), simbolo)} "
            "para alcanzar la meta anual."
        )

else:
    st.info(
        "Introduce metas mensuales mayores que cero "
        "para calcular el cumplimiento."
    )


# ==========================================================
# GRÁFICOS
# ==========================================================

st.markdown(
    '<div class="section-title">Visualización de ventas</div>',
    unsafe_allow_html=True
)

col_grafico, col_resumen = st.columns([3, 1])

with col_grafico:

    if tipo_grafico == "Barras":

        fig = px.bar(
            datos,
            x="Mes",
            y="Ventas",
            title=f"Ventas mensuales de {anio}",
            text="Ventas",
            color="Ventas",
            color_continuous_scale=["#B9D8F5", "#1255A0"]
        )

        fig.update_coloraxes(showscale=False)

        if mostrar_meta:
            fig.add_scatter(
                x=datos["Mes"],
                y=datos["Meta"],
                mode="lines+markers",
                name="Meta mensual",
                line=dict(color="#E59A28", width=3)
            )

        if mostrar_etiquetas:
            fig.update_traces(
                selector=dict(type="bar"),
                texttemplate="%{y:,.0f}",
                textposition="outside"
            )
        else:
            fig.update_traces(
                selector=dict(type="bar"),
                text=None
            )

    elif tipo_grafico == "Líneas":

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=datos["Mes"],
                y=datos["Ventas"],
                mode="lines+markers+text" if mostrar_etiquetas
                else "lines+markers",
                text=[
                    f"{v:,.0f}" for v in datos["Ventas"]
                ] if mostrar_etiquetas else None,
                textposition="top center",
                name="Ventas reales",
                line=dict(color="#1769AA", width=3),
                marker=dict(size=8)
            )
        )

        if mostrar_meta:
            fig.add_trace(
                go.Scatter(
                    x=datos["Mes"],
                    y=datos["Meta"],
                    mode="lines+markers",
                    name="Meta mensual",
                    line=dict(
                        color="#E59A28",
                        width=2,
                        dash="dash"
                    )
                )
            )

        fig.update_layout(
            title=f"Evolución de ventas de {anio}"
        )

    elif tipo_grafico == "Área":

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=datos["Mes"],
                y=datos["Ventas"],
                mode="lines",
                name="Ventas",
                fill="tozeroy",
                line=dict(color="#1769AA", width=3)
            )
        )

        if mostrar_meta:
            fig.add_trace(
                go.Scatter(
                    x=datos["Mes"],
                    y=datos["Meta"],
                    mode="lines",
                    name="Meta mensual",
                    line=dict(
                        color="#E59A28",
                        width=2,
                        dash="dash"
                    )
                )
            )

        fig.update_layout(
            title=f"Área de ventas de {anio}"
        )

    else:

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=datos["Mes"],
                y=datos["Ventas"],
                name="Ventas reales",
                marker_color="#1769AA"
            )
        )

        fig.add_trace(
            go.Bar(
                x=datos["Mes"],
                y=datos["Meta"],
                name="Meta mensual",
                marker_color="#E6A23C"
            )
        )

        fig.update_layout(
            title=f"Ventas reales frente a metas de {anio}",
            barmode="group"
        )

    fig.update_layout(
        template="plotly_white",
        height=480,
        xaxis_title="Mes",
        yaxis_title=f"Importe ({simbolo})",
        font=dict(
            family="Arial",
            size=12,
            color="#34465A"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        margin=dict(l=20, r=20, t=75, b=20)
    )

    fig.update_xaxes(
        tickangle=-35,
        categoryorder="array",
        categoryarray=MESES
    )

    fig.update_yaxes(
        rangemode="tozero",
        tickformat=",.0f"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "responsive": True,
            "scrollZoom": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": f"ventas_{anio}",
                "height": 800,
                "width": 1400,
                "scale": 2
            }
        }
    )

with col_resumen:

    st.markdown("#### Resumen anual")

    st.write("**Año de análisis**")
    st.write(anio)

    st.write("**Total de meses**")
    st.write("12")

    st.write("**Meses con ventas**")
    st.write(int((datos["Ventas"] > 0).sum()))

    st.write("**Meses que alcanzaron su meta**")
    meses_cumplidos = (
        (datos["Meta"] > 0) &
        (datos["Ventas"] >= datos["Meta"])
    ).sum()

    st.write(f"{meses_cumplidos} de 12")

    st.write("**Variación frente a la meta**")
    st.write(
        formato_dinero(diferencia_meta, simbolo)
    )


# ==========================================================
# TABLA DE ANÁLISIS DETALLADO
# ==========================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">Análisis mensual detallado</div>',
    unsafe_allow_html=True
)

analisis = datos.copy()

analisis["Diferencia"] = (
    analisis["Ventas"] - analisis["Meta"]
)

analisis["Cumplimiento (%)"] = [
    calcular_cumplimiento(v, m)
    for v, m in zip(analisis["Ventas"], analisis["Meta"])
]

analisis["Estado"] = [
    "Sin meta" if meta <= 0
    else "Cumplida" if venta >= meta
    else "Pendiente"
    for venta, meta in zip(
        analisis["Ventas"],
        analisis["Meta"]
    )
]

tabla_final = analisis.copy()

for columna in ["Ventas", "Meta", "Diferencia"]:
    tabla_final[columna] = tabla_final[columna].map(
        lambda x: f"{simbolo} {x:,.2f}"
    )

tabla_final["Cumplimiento (%)"] = (
    analisis["Cumplimiento (%)"].map(
        lambda x: f"{x:.2f}%"
    )
)

st.dataframe(
    tabla_final,
    hide_index=True,
    use_container_width=True
)


# ==========================================================
# DESCARGA DE INFORMACIÓN
# ==========================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">Exportar información</div>',
    unsafe_allow_html=True
)

col_csv, col_html, col_nota = st.columns([1, 1, 2])

with col_csv:

    csv = datos.to_csv(
        index=False,
        sep=";",
        decimal=","
    )

    st.download_button(
        label="Descargar datos CSV",
        data=csv.encode("utf-8-sig"),
        file_name=f"ventas_{anio}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_html:

    html = fig.to_html(
        full_html=True,
        include_plotlyjs=True
    )

    st.download_button(
        label="Descargar gráfico HTML",
        data=html.encode("utf-8"),
        file_name=f"grafico_ventas_{anio}.html",
        mime="text/html",
        use_container_width=True
    )

with col_nota:

    st.caption(
        "El CSV permite analizar los datos en Excel. "
        "El HTML conserva el gráfico interactivo y permite "
        "abrirlo en un navegador sin ejecutar Streamlit."
    )


# ==========================================================
# PIE DE PÁGINA
# ==========================================================

st.markdown("---")

st.caption(
    f"SALES ANALYTICS | Informe comercial {anio} | "
    "Desarrollado con Python, Streamlit, Pandas y Plotly."
)
