import streamlit as st
import sqlite3
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Leitor de QR Code", layout="centered")

# Função para salvar QR Code no banco de dados
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

# Interface do usuário
st.title("📷 Leitor de QR Code via Câmera")
st.markdown("Abra no celular e escaneie o QR Code com a câmera.")

# Iframe com leitor de QR Code externo
st.markdown("""
<iframe src="https://bassoli-html5qrcode.streamlit.app" width="100%" height="500" frameborder="0"></iframe>
""", unsafe_allow_html=True)

# Verifica se há conteúdo recebido via query string
query_params = st.query_params
if "conteudo" in query_params:
    conteudo = query_params["conteudo"]
    salvar_qrcode(conteudo)
    st.success(f"✅ QR Code recebido: {conteudo}")