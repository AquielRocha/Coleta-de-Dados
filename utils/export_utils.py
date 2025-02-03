# utils/export_utils.py
import pandas as pd
from io import BytesIO
from datetime import datetime

def exportar_para_excel(dados):
    """Exporta os dados para um arquivo Excel."""
    df = pd.DataFrame(
        dados,
        columns=["Setor", "Unidade", "Instrumento", "Objetivo", "Eixo Temático", "Ação de Manejo", "Usuário", "Preenchido em"]
    )
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Vinculações')
    buffer.seek(0)
    return buffer
