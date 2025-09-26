import streamlit as st
import sqlite3
from datetime import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Leitor de Cupom Fiscal", layout="centered")

# Função para salvar dados estruturados
def salvar_nota(url, chave, emitente, data_emissao, produtos, total):
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
    cursor.execute("INSERT INTO cupons (url, chave, emitente, data_emissao, produtos, total, data_hora) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (url, chave, emitente, data_emissao, produtos, total, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Função para extrair dados da nota fiscal
def extrair_dados_nota(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        texto = soup.get_text(separator="\n", strip=True)

        chave = ""
        emitente = ""
        data_emissao = ""
        produtos = []
        total = ""

        for linha in texto.split("\n"):
            if "Chave de Acesso" in linha:
                chave = linha.split(":")[-1].strip()
            elif "Emitente:" in linha:
                emitente = linha.split(":")[-1].strip()
            elif "Data de Emissão" in linha:
                data_emissao = linha.split(":")[-1].strip()
            elif "Valor Total R$" in linha:
                total = linha.split("R$")[-1].strip()
            elif "Qtde:" in linha and "Vl. Unit" in linha:
                produtos.append(linha.strip())

        salvar_nota(url, chave, emitente, data_emissao, "\n".join(produtos), total)
        return chave, emitente, data_emissao, produtos, total
    except Exception as e:
        st.error(f"Erro ao acessar o site da SEFAZ: {e}")
        return "", "", "", [], ""

# Interface principal
st.title("📷 Leitor de Cupom Fiscal")
modo = st.radio("Escolha o modo de leitura:", ["📸 Câmera", "🖼️ Imagem do QR Code"])

if modo == "📸 Câmera":
    st.markdown("Escaneie o QR Code do seu cupom fiscal usando a câmera do celular.")
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

elif modo == "🖼️ Imagem do QR Code":
    imagem = st.file_uploader("Envie uma imagem com o QR Code do cupom fiscal", type=["png", "jpg", "jpeg"])
    if imagem:
        st.image(imagem, caption="Imagem enviada", use_column_width=True)
        st.info("🔄 Enviando imagem para API externa...")
        api_url = "https://api.qrserver.com/v1/read-qr-code/"
        response = requests.post(api_url, files={"file": imagem})
        try:
            conteudo = response.json()[0]["symbol"][0]["data"]
            if conteudo:
                st.success("✅ QR Code lido com sucesso!")
                st.code(conteudo, language="text")
                chave, emitente, data_emissao, produtos, total = extrair_dados_nota(conteudo)
                st.markdown(f"**Chave de Acesso:** {chave}")
                st.markdown(f"**Emitente:** {emitente}")
                st.markdown(f"**Data de Emissão:** {data_emissao}")
                st.markdown(f"**Valor Total:** R$ {total}")
                st.markdown("**Produtos:**")
                for p in produtos:
                    st.write(f"• {p}")
            else:
                st.error("❌ QR Code não reconhecido na imagem.")
        except:
            st.error("❌ Erro ao processar a imagem. Verifique se é um QR Code válido.")

# Recebe conteúdo via query string (modo câmera)
query_params = st.query_params
if "conteudo" in query_params:
    conteudo = query_params["conteudo"]
    st.success("✅ QR Code recebido!")
    st.code(conteudo, language="text")
    chave, emitente, data_emissao, produtos, total = extrair_dados_nota(conteudo)
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