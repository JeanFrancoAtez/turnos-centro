import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Turnos Rehabilitación", page_icon="🤝", layout="centered")
ARCHIVO_DATOS = "registro_turnos.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        return df
    else:
        return pd.DataFrame(columns=["Nombre", "Especialidad/Rol", "Fecha", "Turno", "Notas"])

def guardar_datos(df):
    df.to_csv(ARCHIVO_DATOS, index=False)

df_turnos = cargar_datos()

# --- DISEÑO ---
st.title("🤝 Centro de Rehabilitación")
st.write("Registra los días en los que vendrás a colaborar al centro.")

tab_registro, tab_calendario, tab_registro_interno = st.tabs(["📝 Anotar Turno", "📅 Ver Calendario", "📋 Registro Interno"])

with tab_registro:
    st.header("Ingresa tus datos")
    with st.form("form_turno", clear_on_submit=True):
        nombre = st.text_input("Tu Nombre Completo *")
        rol = st.selectbox("Especialidad o Rol", ["Kinesiólogo(a)", "Terapeuta Ocupacional", "Psicólogo(a)", "Fonoaudiólogo(a)", "Médico", "Voluntario(a) General", "Otro"])
        fecha_elegida = st.date_input("¿Qué día vendrás?", min_value=date.today(), format="DD/MM/YYYY")
        turno = st.radio("¿En qué horario?", ["Mañana (09:00 - 13:00)", "Tarde (14:00 - 18:00)", "Día Completo"])
        notas = st.text_area("Notas adicionales (opcional)", placeholder="Ej: Llego un poco más tarde, llevo materiales, etc.")
        
        if st.form_submit_button("✅ Registrar mi turno"):
            if nombre.strip() == "":
                st.error("Por favor, ingresa tu nombre.")
            else:
                nuevo_registro = pd.DataFrame([{"Nombre": nombre, "Especialidad/Rol": rol, "Fecha": fecha_elegida, "Turno": turno, "Notas": notas}])
                df_turnos = pd.concat([df_turnos, nuevo_registro], ignore_index=True)
                guardar_datos(df_turnos)
                st.success(f"¡Gracias {nombre}! Tu turno ha sido guardado.")

with tab_calendario:
    st.header("¿Quiénes van esta semana?")
    if df_turnos.empty:
        st.info("Aún no hay turnos registrados.")
    else:
        df_futuro = df_turnos[df_turnos['Fecha'] >= date.today()].sort_values(by="Fecha")
        if df_futuro.empty:
             st.info("No hay turnos registrados para los próximos días.")
        else:
            dias_con_turnos = df_futuro['Fecha'].unique()
            dia_seleccionado = st.selectbox("Selecciona un día para ver quién asiste:", dias_con_turnos, format_func=lambda x: x.strftime('%d/%m/%Y'))
            for index, row in df_futuro[df_futuro['Fecha'] == dia_seleccionado].iterrows():
                with st.container(border=True):
                    st.write(f"**👤 {row['Nombre']}** - {row['Especialidad/Rol']}")
                    st.write(f"🕒 {row['Turno']}")
                    if pd.notna(row['Notas']) and str(row['Notas']).strip() != "":
                        st.caption(f"📝 Nota: {row['Notas']}")

with tab_registro_interno:
    st.header("Registro Completo")
    if not df_turnos.empty:
        st.dataframe(df_turnos, use_container_width=True, hide_index=True)
        csv = df_turnos.to_csv(index=False).encode('utf-8')
        st.download_button(label="⬇️ Descargar Excel (CSV)", data=csv, file_name=f'registro_{date.today()}.csv', mime='text/csv')
    else:
        st.info("La base de datos está vacía.")
