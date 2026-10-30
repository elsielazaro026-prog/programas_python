import ast
import io
import numpy as np
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =========================================================

st.set_page_config(
    page_title="CURVE 3D | Graficador Matemático",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Colores corporativos
NAVY = "#17365D"
BLUE = "#2878B5"
TEAL = "#159A91"

# Estilos de la interfaz
st.markdown("""
<style>
    .stApp {
        background-color: #F3F6FA;
    }

    .main-title {
        font-size: 35px;
        font-weight: 800;
        color: #17365D;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 16px;
        color: #66758A;
        margin-top: 4px;
        margin-bottom: 25px;
    }

    .section-title {
        color: #17365D;
        font-size: 21px;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #DCE3EC;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# FUNCIONES MATEMÁTICAS PERMITIDAS
# =========================================================

FUNCTIONS = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "sqrt": np.sqrt,
    "exp": np.exp,
    "log": np.log,
    "log10": np.log10,
    "abs": np.abs,
    "floor": np.floor,
    "ceil": np.ceil
}

CONSTANTS = {
    "pi": np.pi,
    "e": np.e
}


class ExpressionEvaluator:
    """Evalúa expresiones matemáticas con operaciones permitidas."""

    ALLOWED_NODES = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.UAdd
    )

    def __init__(self, expression):
        self.expression = expression.strip()

        if not self.expression:
            raise ValueError("La expresión matemática está vacía.")

        self.tree = ast.parse(self.expression, mode="eval")

        for node in ast.walk(self.tree):

            if not isinstance(node, self.ALLOWED_NODES):
                raise ValueError(
                    "La expresión contiene una operación no permitida."
                )

            if isinstance(node, ast.Name):
                if node.id not in (
                    {"t", "u", "v"}
                    | set(FUNCTIONS)
                    | set(CONSTANTS)
                ):
                    raise ValueError(
                        f"Nombre matemático no reconocido: {node.id}"
                    )

            if isinstance(node, ast.Call):

                if (
                    not isinstance(node.func, ast.Name)
                    or node.func.id not in FUNCTIONS
                    or node.keywords
                ):
                    raise ValueError(
                        "La función utilizada no está permitida."
                    )

    def evaluate(self, **variables):

        namespace = {
            **FUNCTIONS,
            **CONSTANTS,
            **variables
        }

        result = eval(
            compile(self.tree, "<expresion>", "eval"),
            {"__builtins__": {}},
            namespace
        )

        return np.asarray(result, dtype=float)


# =========================================================
# ENCABEZADO
# =========================================================

st.markdown(
    '<div class="main-title">CURVE 3D</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Graficador interactivo de curvas y superficies matemáticas '
    'en tres dimensiones'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")


# =========================================================
# BARRA LATERAL
# =========================================================

st.sidebar.markdown("## CONFIGURACIÓN")

tipo = st.sidebar.selectbox(
    "Selecciona la figura",
    [
        "Circunferencia",
        "Elipse",
        "Hélice",
        "Espiral 3D",
        "Curva personalizada",
        "Esfera",
        "Elipsoide",
        "Toro"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Parámetros geométricos")

a = st.sidebar.number_input(
    "Radio o semieje A",
    min_value=0.1,
    max_value=100.0,
    value=5.0,
    step=0.5
)

b = st.sidebar.number_input(
    "Radio o semieje B",
    min_value=0.1,
    max_value=100.0,
    value=3.0,
    step=0.5
)

c = st.sidebar.number_input(
    "Radio o semieje C",
    min_value=0.1,
    max_value=100.0,
    value=2.0,
    step=0.5
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Resolución y presentación")

puntos = st.sidebar.slider(
    "Resolución de la gráfica",
    min_value=50,
    max_value=500,
    value=200,
    step=50
)

color = st.sidebar.color_picker(
    "Color de la figura",
    BLUE
)

grosor = st.sidebar.slider(
    "Grosor de línea",
    min_value=1.0,
    max_value=8.0,
    value=3.0,
    step=0.5
)

mostrar_ejes = st.sidebar.checkbox(
    "Mostrar ejes y cuadrícula",
    value=True
)

st.sidebar.markdown("---")


# =========================================================
# PARÁMETROS DE LAS ECUACIONES
# =========================================================

if tipo in [
    "Circunferencia",
    "Elipse",
    "Hélice",
    "Espiral 3D",
    "Curva personalizada"
]:

    st.markdown(
        '<div class="section-title">Parámetros de la curva</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        t_min = st.number_input(
            "Parámetro mínimo t",
            value=0.0,
            step=0.5
        )

    with col2:
        t_max = st.number_input(
            "Parámetro máximo t",
            value=6.283185,
            step=0.5
        )

    if tipo == "Curva personalizada":

        st.markdown("### Introduce tus propias ecuaciones")

        colx, coly, colz = st.columns(3)

        with colx:
            x_expr = st.text_input(
                "Ecuación X(t)",
                value="cos(t)"
            )

        with coly:
            y_expr = st.text_input(
                "Ecuación Y(t)",
                value="sin(t)"
            )

        with colz:
            z_expr = st.text_input(
                "Ecuación Z(t)",
                value="t"
            )

        st.caption(
            "Funciones admitidas: sin, cos, tan, sqrt, exp, log, "
            "log10, abs. También puedes utilizar pi y e. "
            "Para potencias usa **, por ejemplo t**2."
        )

else:

    st.markdown(
        '<div class="section-title">Parámetros de la superficie</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Modifica los radios o semiejes desde el panel lateral. "
        "La superficie se actualizará automáticamente."
    )

    t_min = 0.0
    t_max = 2 * np.pi


# =========================================================
# GENERACIÓN DEL GRÁFICO
# =========================================================

def generar_grafico():

    fig = go.Figure()

    # -----------------------------------------------------
    # CIRCUNFERENCIA
    # -----------------------------------------------------

    if tipo == "Circunferencia":

        t = np.linspace(t_min, t_max, puntos)

        x = a * np.cos(t)
        y = a * np.sin(t)
        z = np.zeros_like(t)

        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                line=dict(color=color, width=grosor * 2),
                name="Circunferencia"
            )
        )

    # -----------------------------------------------------
    # ELIPSE
    # -----------------------------------------------------

    elif tipo == "Elipse":

        t = np.linspace(t_min, t_max, puntos)

        x = a * np.cos(t)
        y = b * np.sin(t)
        z = np.zeros_like(t)

        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                line=dict(color=color, width=grosor * 2),
                name="Elipse"
            )
        )

    # -----------------------------------------------------
    # HÉLICE
    # -----------------------------------------------------

    elif tipo == "Hélice":

        t = np.linspace(t_min, t_max, puntos)

        x = a * np.cos(t)
        y = b * np.sin(t)
        z = c * t

        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                line=dict(color=color, width=grosor * 2),
                name="Hélice"
            )
        )

    # -----------------------------------------------------
    # ESPIRAL 3D
    # -----------------------------------------------------

    elif tipo == "Espiral 3D":

        t = np.linspace(t_min, t_max, puntos)

        x = a * t * np.cos(t)
        y = b * t * np.sin(t)
        z = c * t

        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                line=dict(color=color, width=grosor * 2),
                name="Espiral 3D"
            )
        )

    # -----------------------------------------------------
    # CURVA PERSONALIZADA
    # -----------------------------------------------------

    elif tipo == "Curva personalizada":

        t = np.linspace(t_min, t_max, puntos)

        try:

            x = ExpressionEvaluator(
                x_expr
            ).evaluate(t=t)

            y = ExpressionEvaluator(
                y_expr
            ).evaluate(t=t)

            z = ExpressionEvaluator(
                z_expr
            ).evaluate(t=t)

            x, y, z = np.broadcast_arrays(x, y, z, subok=False)

            if x.ndim == 0:
                x = np.full_like(t, float(x))

            if y.ndim == 0:
                y = np.full_like(t, float(y))

            if z.ndim == 0:
                z = np.full_like(t, float(z))

            x = np.broadcast_to(x, t.shape)
            y = np.broadcast_to(y, t.shape)
            z = np.broadcast_to(z, t.shape)

            valido = (
                np.isfinite(x)
                & np.isfinite(y)
                & np.isfinite(z)
            )

            x = np.where(valido, x, np.nan)
            y = np.where(valido, y, np.nan)
            z = np.where(valido, z, np.nan)

            if np.count_nonzero(valido) < 2:
                raise ValueError(
                    "Las ecuaciones no generan suficientes puntos válidos."
                )

            fig.add_trace(
                go.Scatter3d(
                    x=x,
                    y=y,
                    z=z,
                    mode="lines",
                    line=dict(color=color, width=grosor * 2),
                    name="Curva personalizada"
                )
            )

        except Exception as error:

            raise ValueError(
                f"No se pudieron evaluar las ecuaciones: {error}"
            ) from error

    # -----------------------------------------------------
    # ESFERA
    # -----------------------------------------------------

    elif tipo == "Esfera":

        u = np.linspace(0, 2 * np.pi, puntos)
        v = np.linspace(-np.pi / 2, np.pi / 2, puntos // 2)

        U, V = np.meshgrid(u, v)

        X = a * np.cos(V) * np.cos(U)
        Y = a * np.cos(V) * np.sin(U)
        Z = a * np.sin(V)

        fig.add_trace(
            go.Surface(
                x=X,
                y=Y,
                z=Z,
                colorscale=[
                    [0, color],
                    [1, color]
                ],
                showscale=False,
                opacity=0.9,
                name="Esfera"
            )
        )

    # -----------------------------------------------------
    # ELIPSOIDE
    # -----------------------------------------------------

    elif tipo == "Elipsoide":

        u = np.linspace(0, 2 * np.pi, puntos)
        v = np.linspace(-np.pi / 2, np.pi / 2, puntos // 2)

        U, V = np.meshgrid(u, v)

        X = a * np.cos(V) * np.cos(U)
        Y = b * np.cos(V) * np.sin(U)
        Z = c * np.sin(V)

        fig.add_trace(
            go.Surface(
                x=X,
                y=Y,
                z=Z,
                colorscale=[
                    [0, color],
                    [1, color]
                ],
                showscale=False,
                opacity=0.9,
                name="Elipsoide"
            )
        )

    # -----------------------------------------------------
    # TORO
    # -----------------------------------------------------

    elif tipo == "Toro":

        # Radio mayor y radio menor
        R = a
        r = min(b, R * 0.95)

        u = np.linspace(0, 2 * np.pi, puntos)
        v = np.linspace(0, 2 * np.pi, puntos // 2)

        U, V = np.meshgrid(u, v)

        X = (R + r * np.cos(V)) * np.cos(U)
        Y = (R + r * np.cos(V)) * np.sin(U)
        Z = c * np.sin(V)

        fig.add_trace(
            go.Surface(
                x=X,
                y=Y,
                z=Z,
                colorscale=[
                    [0, color],
                    [1, color]
                ],
                showscale=False,
                opacity=0.9,
                name="Toro"
            )
        )

    # -----------------------------------------------------
    # DISEÑO DEL GRÁFICO
    # -----------------------------------------------------

    fig.update_layout(
        title=dict(
            text=f"<b>{tipo.upper()}</b>",
            x=0.5,
            font=dict(size=23, color=NAVY)
        ),

        paper_bgcolor="white",
        plot_bgcolor="white",

        margin=dict(
            l=0,
            r=0,
            t=65,
            b=0
        ),

        height=650,

        font=dict(
            family="Arial",
            color=NAVY
        ),

        scene=dict(
            xaxis_title="Eje X",
            yaxis_title="Eje Y",
            zaxis_title="Eje Z",
            aspectmode="data"
        ),

        showlegend=True
    )

    if not mostrar_ejes:

        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False)
            )
        )

    return fig


# =========================================================
# VISUALIZACIÓN
# =========================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">Visualización tridimensional</div>',
    unsafe_allow_html=True
)

try:

    figura = generar_grafico()

    st.plotly_chart(
        figura,
        use_container_width=True,
        config={
            "displaylogo": False,
            "responsive": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": "grafico_3d",
                "scale": 2
            }
        }
    )

    # Información complementaria

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Figura seleccionada",
            tipo
        )

    with col2:
        st.metric(
            "Parámetro A",
            f"{a:.2f}"
        )

    with col3:
        st.metric(
            "Resolución",
            f"{puntos} puntos"
        )

    # Descargar el gráfico como HTML interactivo

    html = figura.to_html(
        include_plotlyjs=True,
        full_html=True
    )

    st.download_button(
        label="Descargar gráfico interactivo HTML",
        data=html,
        file_name="grafico_3d.html",
        mime="text/html",
        use_container_width=True
    )

    st.success(
        "Gráfico generado correctamente. "
        "Puedes girarlo, acercarlo y explorar sus coordenadas."
    )

except Exception as error:

    st.error(
        f"No se pudo generar el gráfico: {error}"
    )


# =========================================================
# INFORMACIÓN MATEMÁTICA
# =========================================================

with st.expander("Consultar información matemática"):

    if tipo == "Circunferencia":

        st.latex(
            r"x(t)=a\cos(t),\quad "
            r"y(t)=a\sin(t),\quad z(t)=0"
        )

    elif tipo == "Elipse":

        st.latex(
            r"x(t)=a\cos(t),\quad "
            r"y(t)=b\sin(t),\quad z(t)=0"
        )

    elif tipo == "Hélice":

        st.latex(
            r"x(t)=a\cos(t),\quad "
            r"y(t)=b\sin(t),\quad z(t)=ct"
        )

    elif tipo == "Espiral 3D":

        st.latex(
            r"x(t)=at\cos(t),\quad "
            r"y(t)=bt\sin(t),\quad z(t)=ct"
        )

    elif tipo == "Esfera":

        st.latex(
            r"x^2+y^2+z^2=a^2"
        )

    elif tipo == "Elipsoide":

        st.latex(
            r"\frac{x^2}{a^2}+"
            r"\frac{y^2}{b^2}+"
            r"\frac{z^2}{c^2}=1"
        )

    elif tipo == "Toro":

        st.latex(
            r"x=(R+r\cos(v))\cos(u)"
        )

        st.latex(
            r"y=(R+r\cos(v))\sin(u)"
        )

        st.latex(
            r"z=c\sin(v)"
        )

    else:

        st.info(
            "La curva personalizada se define mediante "
            "las expresiones X(t), Y(t) y Z(t) introducidas arriba."
        )

st.markdown("---")

st.caption(
    "CURVE 3D | Graficador matemático interactivo | "
    "Desarrollado con Python, Streamlit, NumPy y Plotly"
)