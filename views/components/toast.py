import streamlit as st
import time

def show_toast(message, alert_type="warning"):
    """
    Exibe um toast estilizado no canto superior direito do Streamlit.

    Parâmetros:
    - message (str): Mensagem do toast.
    - alert_type (str): Tipo do alerta ('warning', 'info', 'error', 'success').
    """

    # Cores de fundo para cada tipo de alerta
    alert_colors = {
        "warning": "#FFC107",  # Amarelo
        "info": "#17A2B8",     # Azul
        "error": "#DC3545",    # Vermelho
        "success": "#28A745"   # Verde
    }

    # Emojis para cada tipo de alerta
    alert_emojis = {
        "warning": "⚠️",
        "info": "ℹ️",
        "error": "❌",
        "success": "✅"
    }

    # Obtém cor e emoji correspondente
    bg_color = alert_colors.get(alert_type, "#FFC107")  # Padrão: Amarelo
    emoji = alert_emojis.get(alert_type, "⚠️")

    # Exibe o toast padrão (caso o usuário queira manter a funcionalidade nativa)
    st.toast(f"{emoji} {message}")

    
    # Mantém o toast visível por 3 segundos
    time.sleep(3)

# # 📌 **Testando diferentes tipos de toast**
# show_toast("Usuário não encontrado ou não associado a um setor.", "warning")
# show_toast("Operação realizada com sucesso!", "success")
# show_toast("Erro ao processar a requisição.", "error")
# show_toast("Atualize sua página para ver as mudanças.", "info")
