import streamlit as st

st.set_page_config(page_title="Leitor de QR Code", layout="centered")

st.markdown("## 📷 Escaneie o QR Code do Cupom Fiscal")

st.components.v1.html("""
<!DOCTYPE html>
<html>
<head>
  <title>Leitor de QR Code</title>
  <script src="https://unpkg.com/html5-qrcode"></script>
</head>
<body>
  <div id="reader" style="width:100%"></div>
  <script>
    function onScanSuccess(decodedText, decodedResult) {
      window.location.href = "https://controlefinanceiro2025qrcode.streamlit.app1/?conteudo=" + encodeURIComponent(decodedText);
    }
    new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 }).render(onScanSuccess);
  </script>
</body>
</html>
""", height=500)