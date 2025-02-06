import pandas as pd
from io import BytesIO

def exportar_para_excel(dados):
    """Exporta os dados para um arquivo Excel."""
    df = pd.DataFrame(
        dados,
        columns=[
            "Nome",                  # [1]
            "Setor",                 # [2]
            "Unidade",               # [3]
            "Instrumento",           # [4]
            "Objetivo",              # [5]
            "Eixo Temático",         # [6]
            "Ação de Manejo",        # [7]
            "Preenchido em",         # [8]
            "Descrição do Instrumento"  # [9]
        ]
    )
    # Reordena as colunas para exportar na mesma ordem da visualização:
    ordem_export = [
        "Setor",
        "Unidade",
        "Descrição do Instrumento",
        "Instrumento",
        "Objetivo",
        "Eixo Temático",
        "Ação de Manejo",
        "Nome",
        "Preenchido em"
    ]
    df = df[ordem_export]
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Vinculações')
    buffer.seek(0)
    return buffer
