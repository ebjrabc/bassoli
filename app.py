import streamlit as st
import sqlite3
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Leitor de Cupom Fiscal", layout="centered")

# Função para salvar no banco
def salvar_qrcode(conteudo):
    conn = sqlite3.connect("cupons.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conteudo TEXT NOT NULL,
            data_hora TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT INTO cupons (conteudo, data_hora) VALUES (?, ?)",
                   (conteudo, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Interface
st.title("📷 Leitor de Cupom Fiscal")
st.markdown("Escaneie o QR Code do seu cupom fiscal usando a câmera do celular.")

# Componente HTML que ativa a câmera
st.components.v1.html("""
<script src="https://unpkg.com/html5-qrcode"></script>
<div id="reader" style="width:100%"></div>
<script>
function onScanSuccess(decodedText, decodedResult) {
  const params = new URLSearchParams(window.location.search);
  if (!params.has("conteudo")) {
    window.location.search = "?conteudo=" + encodeURIComponent(decodedText);
  }
}
new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 }).render(onScanSuccess);
</script>
""", height=500)

# Recebe conteúdo via query string
query_params = st.query_params
if "conteudo" in query_params:
    conteudo = query_params["conteudo"]
    salvar_qrcode(conteudo)
    st.success("✅ QR Code lido com sucesso!")
    st.code(conteudo, language="text")

    # Decodifica se for cupom fiscal
    if "chNFe=" in conteudo or "nfe.sefaz" in conteudo:
        st.markdown("🔍 Parece ser um cupom fiscal eletrônico.")
        try:
            decoded = urllib.parse.unquote(conteudo)
            st.text_area("Conteúdo decodificado:", decoded, height=200)
        except:
            st.warning("Não foi possível decodificar o conteúdo.")
else:
    st.info("Aguardando leitura do QR Code...")