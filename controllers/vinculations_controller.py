# controllers/vinculations_controller.py

from datetime import datetime
from models.database import conectar_banco
import streamlit as st

def salvar_vinculacoes(usuario, setor_escolhido, instrumentos_por_unidade, 
                         objetivos_por_instrumento, eixos_por_objetivo, acoes_por_eixo):
    """
    Insere novos registros de vinculações no banco.
    Para cada combinação de unidade, instrumento, objetivo, eixo e ação (ou 'Nenhuma'),
    insere um registro com a data de preenchimento.
    """
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
                                    INSERT INTO vinculacoes 
                                    (usuario, setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo, preenchido_em)
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
                                INSERT INTO vinculacoes 
                                (usuario, setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo, preenchido_em)
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

def coletar_dados_para_exportar(usuario, setor_escolhido, instrumentos_por_unidade, 
                                objetivos_por_instrumento, eixos_por_objetivo, acoes_por_eixo):
    """
    Coleta os dados que serão exportados para Excel.
    Retorna uma lista de registros com os campos necessários.
    """
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

def listar_vinculacoes(cpf=None):
    """
    Retorna todas as vinculações cadastradas.
    Se o parâmetro cpf (armazenado no campo "usuario") for informado, filtra somente os registros desse CPF.
    """
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        if cpf:
            cur.execute("""
                SELECT id, usuario, setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo, preenchido_em
                FROM vinculacoes
                WHERE usuario = %s
                ORDER BY id
            """, (cpf,))
        else:
            cur.execute("""
                SELECT id, usuario, setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo, preenchido_em
                FROM vinculacoes
                ORDER BY id
            """)
        records = cur.fetchall()
        cur.close()
        conn.close()
        return records
    except Exception as e:
        st.error(f"Erro ao listar as vinculações: {e}")
        return []

def obter_vinculacao_por_id(vinc_id):
    """
    Retorna os dados completos de uma vinculação específica, dado o ID.
    Esses dados serão utilizados para pré-preencher o formulário de edição.
    """
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, usuario, setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo, preenchido_em
            FROM vinculacoes
            WHERE id = %s
        """, (vinc_id,))
        record = cur.fetchone()
        cur.close()
        conn.close()
        return record
    except Exception as e:
        st.error(f"Erro ao obter a vinculação: {e}")
        return None

def editar_vinculacao(vinc_id, setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo):
    """
    Atualiza a vinculação com o ID especificado.
    O CPF (armazenado no campo "usuario") não é alterado.
    Todos os demais campos (setor, unidade, instrumento, objetivo, eixo temático e ação de manejo)
    são atualizados e a data de atualização é gravada.
    """
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute("""
            UPDATE vinculacoes
            SET setor = %s, unidade = %s, instrumento = %s, objetivo = %s, eixo_tematico = %s, 
                acao_manejo = %s, preenchido_em = %s
            WHERE id = %s
        """, (setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo, datetime.now(), vinc_id))
        conn.commit()
        cur.close()
        conn.close()
        st.success("dados atualizados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao atualizar a vinculação: {e}")

def deletar_vinculacao(vinc_id):
    """
    Deleta a vinculação com o ID especificado.
    """
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute("DELETE FROM vinculacoes WHERE id = %s", (vinc_id,))
        conn.commit()
        cur.close()
        conn.close()
        st.success("Vinculação deletada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao deletar a vinculação: {e}")
