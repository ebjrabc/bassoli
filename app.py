import streamlit as st
from PIL import Image
from pyzbar.pyzbar import decode
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Leitor de QR Code", layout="centered")

# Banco de dados
def salvar_qrcode(conteudo):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qrcodes (import streamlit as st
import sqlite3
from datetime import datetime
import json

st.set_page_config(page_title="Leitor de QR Code", layout="centered")

# Banco de dados
def salvar_qrcode(conteudo):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qrcodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conteudo TEXT NOT NULL,
            data_hora TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT INTO qrcodes (conteudo, data_hora) VALUES (?, ?)",
                   (conteudo, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Interface
st.title("📷 Leitor de QR Code via Câmera")
st.markdown("Abra no celular e escaneie o QR Code com a câmera.")

# Recebe dados via JavaScript
st.markdown("""
<iframe src="https://bassoli-html5qrcode.streamlit.app" width="100%" height="500" frameborder="0"></iframe>
""", unsafe_allow_html=True)

# Recebe conteúdo via query string
query_params = st.experimental_get_query_params()
if "conteudo" in query_params:
    conteudo = query_params["conteudo"][0]
    salvar_qrcode(conteudo)
    st.success(f"✅ QR Code recebido: {conteudo}")