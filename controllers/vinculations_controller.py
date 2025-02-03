# controllers/vinculations_controller.py
from datetime import datetime
from models.database import conectar_banco
import streamlit as st

def salvar_vinculacoes(usuario, setor_escolhido, instrumentos_por_unidade, objetivos_por_instrumento, eixos_por_objetivo, acoes_por_eixo):
    """Salva as vinculações no banco de dados."""
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        for unidade, instrumentos in instrumentos_por_unidade.items():
            for instrumento in instrumentos:
                objetivos = objetivos_por_instrumento.get((unidade, instrumento), [])
                for objetivo in objetivos:
                    eixos = eixos_por_objetivo.get((unidade, instrumento, objetivo), [])
                    for eixo in eixos:
                        acoes = acoes_por_eixo.get((unidade, instrumento, objetivo, eixo), [])
                        if acoes:
                            for acao in acoes:
                                cur.execute(
                                    """
                                    INSERT INTO vinculacoes (usuario, setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo, preenchido_em)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    """,
                                    (
                                        usuario,
                                        setor_escolhido,
                                        unidade,
                                        instrumento,
                                        objetivo,
                                        eixo,
                                        acao,
                                        datetime.now(),
                                    ),
                                )
                        else:
                            cur.execute(
                                """
                                INSERT INTO vinculacoes (usuario, setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo, preenchido_em)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    usuario,
                                    setor_escolhido,
                                    unidade,
                                    instrumento,
                                    objetivo,
                                    eixo,
                                    'Nenhuma',
                                    datetime.now(),
                                ),
                            )
        conn.commit()
        cur.close()
        conn.close()
        st.success("Dados salvos com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar os dados: {e}")

def coletar_dados_para_exportar(usuario, setor_escolhido, instrumentos_por_unidade, objetivos_por_instrumento, eixos_por_objetivo, acoes_por_eixo):
    """Coleta os dados que serão exportados para Excel."""
    dados = []
    for unidade, instrumentos in instrumentos_por_unidade.items():
        for instrumento in instrumentos:
            objetivos = objetivos_por_instrumento.get((unidade, instrumento), [])
            for objetivo in objetivos:
                eixos = eixos_por_objetivo.get((unidade, instrumento, objetivo), [])
                for eixo in eixos:
                    acoes = acoes_por_eixo.get((unidade, instrumento, objetivo, eixo), [])
                    if acoes:
                        for acao in acoes:
                            dados.append([
                                setor_escolhido,
                                unidade,
                                instrumento,
                                objetivo,
                                eixo,
                                acao,
                                usuario,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            ])
                    else:
                        dados.append([
                            setor_escolhido,
                            unidade,
                            instrumento,
                            objetivo,
                            eixo,
                            'Nenhuma',
                            usuario,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ])
    return dados
