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

# Leitura do QR Code
def ler_qrcode(imagem):
    resultado = decode(imagem)
    if resultado:
        return resultado[0].data.decode("utf-8")
    return None

# Interface
st.title("📷 Leitor de QR Code via Imagem")
st.write("Envie uma foto do QR Code ou use a câmera do celular.")

arquivo = st.file_uploader("Escolha uma imagem", type=["jpg", "jpeg", "png"])

if arquivo:
    imagem = Image.open(arquivo)
    st.image(imagem, caption="Imagem enviada", use_column_width=True)

    resultado = ler_qrcode(imagem)
    if resultado:
        st.success(f"✅ QR Code detectado:\n\n{resultado}")
        salvar_qrcode(resultado)
        st.info("📦 QR Code salvo no banco de dados.")
    else:
        st.error("❌ Nenhum QR Code detectado na imagem.")