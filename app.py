import streamlit as st
import sqlite3
from datetime import datetime
import urllib.parse

# Configuração da página
st.set_page_config(page_title="Leitor de Cupom Fiscal", layout="centered")

# Função para salvar no banco de dados
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

# Título e instruções
st.title("📷 Leitor de Cupom Fiscal")
st.markdown("Escaneie o QR Code do seu cupom fiscal usando a câmera do celular.")

# Componente HTML + JS para abrir a câmera e ler QR Code
st.markdown("""
<script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
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
""", unsafe_allow_html=True)

# Recebe conteúdo via query string
query_params = st.query_params
if "conteudo" in query_params:
    conteudo = query_params["conteudo"]
    salvar_qrcode(conteudo)
    st.success("✅ QR Code lido com sucesso!")
    st.code(conteudo, language="text")

    # Se for um cupom fiscal da SEFAZ, tenta extrair dados
    if "chNFe=" in conteudo or "nfe.sefaz" in conteudo:
        st.markdown("🔍 Parece ser um cupom fiscal eletrônico.")
        try:
            decoded = urllib.parse.unquote(conteudo)
            st.text_area("Conteúdo decodificado:", decoded, height=200)
        except:
            st.warning("Não foi possível decodificar o conteúdo.")
else:
    st.info("Aguardando leitura do QR Code...")import streamlit as st
import sqlite3
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Leitor de Cupom Fiscal", layout="centered")

# Inicializa o banco
def inicializar_banco():
    conn = sqlite3.connect("cupons.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            chave TEXT,
            emitente TEXT,
            data_emissao TEXT,
            produtos TEXT,
            total TEXT,
            data_hora TEXT
        )
    """)
    conn.commit()
    conn.close()

inicializar_banco()

# Função para salvar dados
def salvar_nota(url, chave, emitente, data_emissao, produtos, total):
    conn = sqlite3.connect("cupons.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cupons (url, chave, emitente, data_emissao, produtos, total, data_hora) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (url, chave, emitente, data_emissao, produtos, total, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Simulação de extração manual
def extrair_dados_nota_manual(url):
    chave = "35250847508411278863651050000834821774113240"
    emitente = "CIA BRASILEIRA DE DISTRIBUICAO"
    data_emissao = "03/08/2025 17:05:36"
    total = "20,82"
    produtos = [
        "BISC PIR COCO 132G — Qtde: 1 UN — Vl. Unit: 2,59 — Vl. Total: 2,59",
        "PAO QUEIJO EDIVIN — Qtde: 1 UN — Vl. Unit: 10,74 — Vl. Total: 10,74",
        "LEITE COND MOCO 395G — Qtde: 2 UN — Vl. Unit: 3,74 — Vl. Total: 7,48"
    ]
    salvar_nota(url, chave, emitente, data_emissao, "\n".join(produtos), total)
    return chave, emitente, data_emissao, produtos, total

# Interface principal
st.title("📷 Leitor de Cupom Fiscal")
st.markdown("Escaneie o QR Code usando a câmera ou envie uma imagem.")

# Leitura via câmera
st.components.v1.html("""
<script src="https://unpkg.com/html5-qrcode"></script>
<div id="reader" style="width:100%"></div>
<div id="status" style="margin-top:10px; font-weight:bold;"></div>
<script>
function onScanSuccess(decodedText, decodedResult) {
  document.getElementById("status").innerText = "✅ QR Code lido!";
  window.location.href = window.location.pathname + "?conteudo=" + encodeURIComponent(decodedText);
}
new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 }).render(onScanSuccess);
</script>
""", height=550)

# Recebe conteúdo via query string
query_params = st.query_params
if "conteudo" in query_params:
    url = query_params["conteudo"]
    st.success("✅ QR Code recebido!")
    st.code(url, language="text")
    chave, emitente, data_emissao, produtos, total = extrair_dados_nota_real(url)
    st.markdown(f"**Chave de Acesso:** {chave}")
    st.markdown(f"**Emitente:** {emitente}")
    st.markdown(f"**Data de Emissão:** {data_emissao}")
    st.markdown(f"**Valor Total:** R$ {total}")
    st.markdown("**Produtos:**")
    for p in produtos:
        st.write(f"• {p}")

# Histórico de notas salvas
st.markdown("### 📚 Histórico de notas salvas")
conn = sqlite3.connect("cupons.db")
cursor = conn.cursor()
cursor.execute("SELECT chave, emitente, data_emissao, total, produtos, data_hora FROM cupons ORDER BY data_hora DESC")
registros = cursor.fetchall()
conn.close()

if registros:
    for chave, emitente, data_emissao, total, produtos, data_hora in registros:
        st.write(f"📌 {data_hora}")
        st.markdown(f"**Chave:** {chave}")
        st.markdown(f"**Emitente:** {emitente}")
        st.markdown(f"**Data:** {data_emissao}")
        st.markdown(f"**Total:** R$ {total}")
        st.text_area("Produtos:", produtos, height=100)
else:
    st.info("Nenhuma nota fiscal salva ainda.")