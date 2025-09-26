import streamlit as st
import sqlite3
from datetime import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup

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

# Extração real via scraping da SEFAZ-SP
def extrair_dados_nota_real(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Chave de acesso
        chave_tag = soup.find('span', id='lblChaveAcesso')
        chave = chave_tag.text.strip() if chave_tag else "N/A"

        # Emitente
        emitente_tag = soup.find('span', id='lblEmitente')
        emitente = emitente_tag.text.strip() if emitente_tag else "N/A"

        # Data de emissão
        data_tag = soup.find('span', id='lblDataEmissao')
        data_emissao = data_tag.text.strip() if data_tag else "N/A"

        # Valor total
        total_tag = soup.find('span', id='lblValorTotalNota')
        total = total_tag.text.strip().replace("R$", "").strip() if total_tag else "N/A"

        # Produtos
        produtos = []
        itens = soup.select('table#tabResult tbody tr')
        for item in itens:
            cols = item.find_all('td')
            if len(cols) >= 4:
                nome = cols[0].text.strip()
                qtde = cols[1].text.strip()
                valor_unit = cols[2].text.strip()
                valor_total = cols[3].text.strip()
                produtos.append(f"{nome} — Qtde: {qtde} — Vl. Unit: {valor_unit} — Vl. Total: {valor_total}")

        salvar_nota(url, chave, emitente, data_emissao, "\n".join(produtos), total)
        return chave, emitente, data_emissao, produtos, total

    except Exception as e:
        st.error(f"Erro ao extrair dados reais: {e}")
        return "N/A", "N/A", "N/A", [], "N/A"

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
else:
    st.info("Aguardando leitura do QR Code...")

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