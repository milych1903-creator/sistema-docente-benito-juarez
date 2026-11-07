import sqlite3
from datetime import date, datetime
import pandas as pd
import streamlit as st

# ------------------------------------------------------------
# CONFIGURACION GENERAL
# ------------------------------------------------------------
st.set_page_config(
    page_title="Sistema Docente | Secundaria Benito Juárez",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_NAME = "benito_juarez_docente.db"
GRUPOS = ["A", "B", "C", "D", "E", "F"]
ESTADOS_ASISTENCIA = ["Asistió", "Falta", "Retardo", "Justificante"]

# ------------------------------------------------------------
# ESTILOS: AZUL CIELO, BLANCO Y AZUL MARINO
# ------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(145deg, #e4f5ff 0%, #f5fbff 55%, #d8efff 100%);
        color: #17324d;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #c8eaff 0%, #eaf7ff 100%);
        border-right: 1px solid #a8d8f5;
    }
    h1, h2, h3 { color: #123c63 !important; }
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,.82);
        border: 1px solid #c6e5f8;
        padding: 14px;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(24, 82, 120, .06);
    }
    div.stButton > button, div.stDownloadButton > button {
        background: #17699e;
        color: white;
        border: 0;
        border-radius: 9px;
        padding: .55rem 1rem;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background: #0d4f7c;
        color: white;
    }
    .school-header {
        background: linear-gradient(100deg, #0e5688, #2695cc);
        color: white;
        padding: 24px 28px;
        border-radius: 18px;
        margin-bottom: 18px;
        box-shadow: 0 5px 18px rgba(12, 75, 116, .15);
    }
    .school-header h1 { color: white !important; margin: 0; }
    .school-header p { color: #e8f7ff; margin: 7px 0 0 0; }
    .hint {
        background: #edf8ff;
        border-left: 4px solid #2695cc;
        padding: 10px 14px;
        border-radius: 7px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# BASE DE DATOS
# ------------------------------------------------------------
def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def inicializar_bd():
    with conectar() as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alumnos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                grupo TEXT NOT NULL,
                fecha_registro TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grupo TEXT NOT NULL,
                materia TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                fecha_asignacion TEXT NOT NULL,
                fecha_entrega TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS asistencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alumno_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                estado TEXT NOT NULL,
                observaciones TEXT,
                UNIQUE(alumno_id, fecha),
                FOREIGN KEY(alumno_id) REFERENCES alumnos(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trabajos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grupo TEXT NOT NULL,
                materia TEXT NOT NULL,
                actividad TEXT NOT NULL,
                descripcion TEXT,
                fecha TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS temas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grupo TEXT NOT NULL,
                materia TEXT NOT NULL,
                tema TEXT NOT NULL,
                notas TEXT,
                fecha TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agenda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                hora TEXT,
                tipo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT
            )
        """)
        con.commit()

def consultar(sql, params=()):
    with conectar() as con:
        return pd.read_sql_query(sql, con, params=params)

def ejecutar(sql, params=()):
    with conectar() as con:
        con.execute(sql, params)
        con.commit()

inicializar_bd()

def alumnos_grupo(grupo):
    return consultar(
        "SELECT id, nombre, grupo FROM alumnos WHERE grupo = ? ORDER BY nombre COLLATE NOCASE",
        (grupo,)
    )

# ------------------------------------------------------------
# ENCABEZADO Y MENU
# ------------------------------------------------------------
st.markdown("""
<div class="school-header">
    <h1>📘 Sistema de Gestión Docente</h1>
    <p>Escuela Secundaria Para Trabajadores Benito Juárez · Uruapan, Michoacán</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🏫 Menú docente")
    seccion = st.radio(
        "Selecciona un módulo",
        [
            "Inicio",
            "Alumnos",
            "Tareas",
            "Asistencia",
            "Trabajos en clase",
            "Temas de clase",
            "Calendario y agenda",
        ],
    )
    st.divider()
    st.caption("Sistema de uso docente")
    st.caption("Los datos se guardan en esta laptop.")

# ------------------------------------------------------------
# INICIO
# ------------------------------------------------------------
if seccion == "Inicio":
    st.subheader("Bienvenida al espacio de trabajo docente")
    st.write("Administra tus grupos, listas, actividades y planeación desde un solo lugar.")
    total_alumnos = consultar("SELECT COUNT(*) AS n FROM alumnos").iloc[0]["n"]
    total_tareas = consultar("SELECT COUNT(*) AS n FROM tareas").iloc[0]["n"]
    total_grupos = consultar("SELECT COUNT(DISTINCT grupo) AS n FROM alumnos").iloc[0]["n"]
    hoy = date.today().isoformat()
    eventos_hoy = consultar("SELECT COUNT(*) AS n FROM agenda WHERE fecha = ?", (hoy,)).iloc[0]["n"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Alumnos registrados", int(total_alumnos))
    c2.metric("Grupos con alumnos", int(total_grupos))
    c3.metric("Tareas registradas", int(total_tareas))
    c4.metric("Agenda de hoy", int(eventos_hoy))

    st.markdown("### Accesos rápidos")
    a, b, c = st.columns(3)
    a.info("👥 **Alumnos**\n\nRegistra y consulta las listas de los grupos A al F.")
    b.info("📝 **Asistencia**\n\nCaptura la asistencia de cada día.")
    c.info("📅 **Agenda**\n\nOrganiza reuniones, evaluaciones y pendientes.")

    st.markdown('<div class="hint">Consejo: comienza registrando a tus alumnos. Después podrás capturar asistencia, tareas y trabajos por grupo.</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# ALUMNOS
# ------------------------------------------------------------
elif seccion == "Alumnos":
    st.subheader("👥 Registro de alumnos")
    tab1, tab2 = st.tabs(["Registrar alumno", "Consultar listas"])

    with tab1:
        with st.form("form_alumno", clear_on_submit=True):
            nombre = st.text_input("Nombre completo", placeholder="Apellidos y nombre(s)")
            grupo = st.selectbox("Grupo", GRUPOS)
            guardar = st.form_submit_button("Guardar alumno")
            if guardar:
                if nombre.strip():
                    ejecutar(
                        "INSERT INTO alumnos (nombre, grupo, fecha_registro) VALUES (?, ?, ?)",
                        (nombre.strip(), grupo, date.today().isoformat())
                    )
                    st.success(f"Alumno registrado en el grupo {grupo}.")
                    st.rerun()
                else:
                    st.error("Escribe el nombre del alumno.")

    with tab2:
        grupo_consulta = st.selectbox("Selecciona el grupo para consultar", GRUPOS, key="lista_grupo")
        lista = alumnos_grupo(grupo_consulta)
        st.write(f"**Grupo {grupo_consulta} · {len(lista)} alumno(s)**")
        if not lista.empty:
            lista.index = range(1, len(lista) + 1)
            st.dataframe(lista[["nombre"]].rename(columns={"nombre": "Nombre del alumno"}), use_container_width=True)
            st.download_button(
                "Descargar lista en CSV",
                data=lista[["nombre"]].to_csv(index=False).encode("utf-8-sig"),
                file_name=f"lista_grupo_{grupo_consulta}.csv",
                mime="text/csv",
            )
            with st.expander("Eliminar un registro"):
                opciones = {f'{r.nombre} (ID {r.id})': int(r.id) for r in lista.itertuples()}
                elegido = st.selectbox("Alumno", list(opciones.keys()), key="borrar_alumno")
                if st.button("Eliminar alumno seleccionado"):
                    ejecutar("DELETE FROM alumnos WHERE id = ?", (opciones[elegido],))
                    st.warning("Registro eliminado.")
                    st.rerun()
        else:
            st.info("Todavía no hay alumnos registrados en este grupo.")

# ------------------------------------------------------------
# TAREAS
# ------------------------------------------------------------
elif seccion == "Tareas":
    st.subheader("📝 Registro de tareas por grupo")
    with st.form("form_tarea", clear_on_submit=True):
        c1, c2 = st.columns(2)
        grupo = c1.selectbox("Grupo", GRUPOS)
        materia = c2.text_input("Materia")
        titulo = st.text_input("Nombre de la tarea")
        descripcion = st.text_area("Instrucciones o descripción")
        c3, c4 = st.columns(2)
        fecha_asignacion = c3.date_input("Fecha de asignación", value=date.today())
        fecha_entrega = c4.date_input("Fecha de entrega", value=date.today())
        if st.form_submit_button("Guardar tarea"):
            if materia.strip() and titulo.strip():
                ejecutar(
                    """INSERT INTO tareas
                    (grupo, materia, titulo, descripcion, fecha_asignacion, fecha_entrega)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (grupo, materia.strip(), titulo.strip(), descripcion.strip(),
                     fecha_asignacion.isoformat(), fecha_entrega.isoformat())
                )
                st.success("Tarea guardada.")
                st.rerun()
            else:
                st.error("Completa la materia y el nombre de la tarea.")

    st.markdown("### Tareas registradas")
    filtro = st.selectbox("Filtrar por grupo", ["Todos"] + GRUPOS, key="filtro_tareas")
    if filtro == "Todos":
        tareas = consultar("SELECT * FROM tareas ORDER BY fecha_entrega")
    else:
        tareas = consultar("SELECT * FROM tareas WHERE grupo = ? ORDER BY fecha_entrega", (filtro,))
    st.dataframe(tareas, use_container_width=True, hide_index=True)
    if not tareas.empty:
        st.download_button("Descargar tareas en CSV", tareas.to_csv(index=False).encode("utf-8-sig"),
                           "tareas_docentes.csv", "text/csv")

# ------------------------------------------------------------
# ASISTENCIA
# ------------------------------------------------------------
elif seccion == "Asistencia":
    st.subheader("📋 Registro diario de asistencia")
    c1, c2 = st.columns(2)
    grupo = c1.selectbox("Grupo", GRUPOS, key="asistencia_grupo")
    fecha = c2.date_input("Fecha de asistencia", value=date.today(), key="fecha_asistencia")
    alumnos = alumnos_grupo(grupo)

    if alumnos.empty:
        st.warning("Primero registra alumnos en este grupo.")
    else:
        existentes = consultar(
            "SELECT alumno_id, estado, observaciones FROM asistencias WHERE fecha = ?",
            (fecha.isoformat(),)
        )
        existentes_dict = {
            int(r.alumno_id): (r.estado, r.observaciones or "")
            for r in existentes.itertuples()
        }
        filas = []
        for r in alumnos.itertuples():
            estado_previo, obs_previa = existentes_dict.get(int(r.id), ("Asistió", ""))
            filas.append({
                "ID": int(r.id),
                "Alumno": r.nombre,
                "Estado": estado_previo,
                "Observaciones": obs_previa,
            })
        df_asistencia = pd.DataFrame(filas)
        editado = st.data_editor(
            df_asistencia,
            hide_index=True,
            use_container_width=True,
            disabled=["ID", "Alumno"],
            column_config={
                "Estado": st.column_config.SelectboxColumn(
                    "Estado", options=ESTADOS_ASISTENCIA, required=True
                ),
                "Observaciones": st.column_config.TextColumn("Observaciones"),
            },
            key="tabla_asistencia",
        )
        if st.button("Guardar asistencia del grupo"):
            with conectar() as con:
                for fila in editado.itertuples(index=False):
                    con.execute("""
                        INSERT INTO asistencias (alumno_id, fecha, estado, observaciones)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(alumno_id, fecha) DO UPDATE SET
                        estado = excluded.estado,
                        observaciones = excluded.observaciones
                    """, (int(fila.ID), fecha.isoformat(), fila.Estado, fila.Observaciones or ""))
                con.commit()
            st.success("Asistencia guardada correctamente.")
            st.rerun()

        resumen = editado["Estado"].value_counts()
        st.markdown("### Resumen de captura")
        cols = st.columns(4)
        for col, estado in zip(cols, ESTADOS_ASISTENCIA):
            col.metric(estado, int(resumen.get(estado, 0)))

    st.markdown("### Consultar asistencias guardadas")
    filtro_fecha = st.date_input("Fecha para consultar", value=date.today(), key="consulta_fecha")
    registros = consultar("""
        SELECT al.nombre AS Alumno, al.grupo AS Grupo, a.fecha AS Fecha,
               a.estado AS Estado, a.observaciones AS Observaciones
        FROM asistencias a
        JOIN alumnos al ON al.id = a.alumno_id
        WHERE a.fecha = ?
        ORDER BY al.grupo, al.nombre COLLATE NOCASE
    """, (filtro_fecha.isoformat(),))
    st.dataframe(registros, use_container_width=True, hide_index=True)
    if not registros.empty:
        st.download_button("Descargar asistencia CSV", registros.to_csv(index=False).encode("utf-8-sig"),
                           "asistencia.csv", "text/csv")

# ------------------------------------------------------------
# TRABAJOS EN CLASE
# ------------------------------------------------------------
elif seccion == "Trabajos en clase":
    st.subheader("✏️ Registro de trabajos en clase")
    with st.form("form_trabajo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        grupo = c1.selectbox("Grupo", GRUPOS)
        materia = c2.text_input("Materia", key="materia_trabajo")
        actividad = st.text_input("Nombre del trabajo o actividad")
        descripcion = st.text_area("Indicaciones y observaciones")
        fecha = st.date_input("Fecha de realización", value=date.today(), key="fecha_trabajo")
        if st.form_submit_button("Guardar trabajo"):
            if materia.strip() and actividad.strip():
                ejecutar(
                    """INSERT INTO trabajos (grupo, materia, actividad, descripcion, fecha)
                    VALUES (?, ?, ?, ?, ?)""",
                    (grupo, materia.strip(), actividad.strip(), descripcion.strip(), fecha.isoformat())
                )
                st.success("Trabajo registrado.")
                st.rerun()
            else:
                st.error("Completa la materia y el nombre de la actividad.")

    trabajos = consultar("SELECT * FROM trabajos ORDER BY fecha DESC")
    st.markdown("### Historial de trabajos")
    st.dataframe(trabajos, use_container_width=True, hide_index=True)
    if not trabajos.empty:
        st.download_button("Descargar trabajos CSV", trabajos.to_csv(index=False).encode("utf-8-sig"),
                           "trabajos_en_clase.csv", "text/csv")

# ------------------------------------------------------------
# TEMAS DE CLASE
# ------------------------------------------------------------
elif seccion == "Temas de clase":
    st.subheader("📚 Registro de temas y avance")
    with st.form("form_tema", clear_on_submit=True):
        c1, c2 = st.columns(2)
        grupo = c1.selectbox("Grupo", GRUPOS)
        materia = c2.text_input("Materia", key="materia_tema")
        tema = st.text_input("Tema abordado")
        notas = st.text_area("Contenido, aprendizajes o notas del docente")
        fecha = st.date_input("Fecha de la clase", value=date.today(), key="fecha_tema")
        if st.form_submit_button("Guardar tema"):
            if materia.strip() and tema.strip():
                ejecutar(
                    "INSERT INTO temas (grupo, materia, tema, notas, fecha) VALUES (?, ?, ?, ?, ?)",
                    (grupo, materia.strip(), tema.strip(), notas.strip(), fecha.isoformat())
                )
                st.success("Tema guardado.")
                st.rerun()
            else:
                st.error("Completa la materia y el tema.")

    st.markdown("### Temas registrados")
    f1, f2 = st.columns(2)
    grupo_filtro = f1.selectbox("Grupo", ["Todos"] + GRUPOS, key="filtro_temas")
    materia_filtro = f2.text_input("Filtrar por materia (opcional)")
    temas = consultar("SELECT * FROM temas ORDER BY fecha DESC")
    if grupo_filtro != "Todos":
        temas = temas[temas["grupo"] == grupo_filtro]
    if materia_filtro.strip():
        temas = temas[temas["materia"].str.contains(materia_filtro, case=False, na=False)]
    st.dataframe(temas, use_container_width=True, hide_index=True)
    if not temas.empty:
        st.download_button("Descargar temas CSV", temas.to_csv(index=False).encode("utf-8-sig"),
                           "temas_de_clase.csv", "text/csv")

# ------------------------------------------------------------
# CALENDARIO Y AGENDA DOCENTE
# ------------------------------------------------------------
elif seccion == "Calendario y agenda":
    st.subheader("📅 Calendario y agenda docente")
    tab1, tab2 = st.tabs(["Agregar evento", "Consultar agenda"])

    with tab1:
        with st.form("form_agenda", clear_on_submit=True):
            fecha = st.date_input("Fecha del evento", value=date.today())
            hora = st.time_input("Hora", value=datetime.now().replace(second=0, microsecond=0).time())
            tipo = st.selectbox("Tipo de evento", [
                "Planeación", "Reunión", "Evaluación", "Entrega", "Pendiente", "Otro"
            ])
            titulo = st.text_input("Nombre del evento")
            descripcion = st.text_area("Detalles")
            if st.form_submit_button("Guardar evento"):
                if titulo.strip():
                    ejecutar(
                        "INSERT INTO agenda (fecha, hora, tipo, titulo, descripcion) VALUES (?, ?, ?, ?, ?)",
                        (fecha.isoformat(), hora.strftime("%H:%M"), tipo, titulo.strip(), descripcion.strip())
                    )
                    st.success("Evento agregado a la agenda.")
                    st.rerun()
                else:
                    st.error("Escribe el nombre del evento.")

    with tab2:
        fecha_consulta = st.date_input("Selecciona una fecha", value=date.today(), key="agenda_fecha")
        eventos_dia = consultar(
            "SELECT * FROM agenda WHERE fecha = ? ORDER BY hora",
            (fecha_consulta.isoformat(),)
        )
        st.markdown(f"### Agenda del {fecha_consulta.strftime('%d/%m/%Y')}")
        if eventos_dia.empty:
            st.info("No hay eventos registrados para esta fecha.")
        else:
            for evento in eventos_dia.itertuples():
                with st.container(border=True):
                    st.markdown(f"**{evento.hora or 'Sin hora'} · {evento.titulo}**")
                    st.caption(evento.tipo)
                    if evento.descripcion:
                        st.write(evento.descripcion)
                    if st.button("Eliminar evento", key=f"eliminar_evento_{evento.id}"):
                        ejecutar("DELETE FROM agenda WHERE id = ?", (int(evento.id),))
                        st.rerun()

        st.markdown("### Próximos eventos")
        proximos = consultar(
            "SELECT * FROM agenda WHERE fecha >= ? ORDER BY fecha, hora LIMIT 30",
            (date.today().isoformat(),)
        )
        st.dataframe(proximos, use_container_width=True, hide_index=True)
        if not proximos.empty:
            st.download_button("Descargar agenda CSV", proximos.to_csv(index=False).encode("utf-8-sig"),
                               "agenda_docente.csv", "text/csv")

# ------------------------------------------------------------
# PIE DE PAGINA
# ------------------------------------------------------------
st.divider()
st.caption("Sistema de Gestión Docente · Escuela Secundaria Para Trabajadores Benito Juárez · Uruapan, Michoacán")
st.caption("Versión inicial local. Realiza respaldos periódicos del archivo benito_juarez_docente.db.")
