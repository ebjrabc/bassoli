import streamlit as st
import sqlite3
import numpy as np
import cv2
from datetime import datetime

st.set_page_config(page_title="Leitor de QR Code", layout="centered")

# Função para salvar no banco
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

# Função para ler QR Code com OpenCV
def ler_qrcode(imagem):
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(imagem)
    return data

# Interface Streamlit
st.title("📷 Leitor de QR Code")
st.write("Envie uma imagem do QR Code ou use a câmera do celular.")

arquivo = st.file_uploader("Escolha uma imagem", type=["jpg", "jpeg", "png"])

if arquivo:
    file_bytes = np.asarray(bytearray(arquivo.read()), dtype=np.uint8)
    imagem = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    st.image(imagem, caption="Imagem enviada", use_column_width=True)

    resultado = ler_qrcode(imagem)
    if resultado:
        st.success(f"✅ QR Code detectado:\n\n{resultado}")
        salvar_qrcode(resultado)
        st.info("📦 QR Code salvo no banco de dados.")
    else:
        st.error("❌ Nenhum QR Code detectado na imagem.")