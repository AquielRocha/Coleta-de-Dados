import streamlit as st
import psycopg2
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Função para conectar ao banco de dados PostgreSQL
def conectar_banco():
    return psycopg2.connect(
        dbname="fcpp2",
        user="postgres",
        password="asd",
        host="10.197.42.64",
        port="5432"
    )

# Função para buscar dados de uma tabela
def obter_dados(query, params=None):
    conn = conectar_banco()
    cur = conn.cursor()
    cur.execute(query, params if params else ())
    dados = cur.fetchall()
    conn.close()
    return [d[0] for d in dados]

# Interface no Streamlit
st.title("Gestão de Manejo - ICMBio")

# Campo para Identificação do Usuário
usuario = st.text_input("Digite seu nome ou ID para identificar o preenchimento:")
if not usuario.strip():
    st.warning("Por favor, insira seu nome ou ID antes de continuar.")
    st.stop()

# 1️⃣ Seleção do Setor
setores = obter_dados("SELECT DISTINCT nome FROM setor")
setor_escolhido = st.selectbox("Selecione o Setor", setores)

# 2️⃣ Seleção de Unidades
unidades = obter_dados("SELECT DISTINCT nome FROM unidade_conservacao")
unidades_selecionadas = st.multiselect("Selecione as Unidades de Conservação", unidades)

# 3️⃣ Seleção de Instrumentos
instrumentos = obter_dados("SELECT DISTINCT nome FROM instrumento")
instrumentos_por_unidade = {}
if unidades_selecionadas:
    for unidade in unidades_selecionadas:
        instrumentos_escolhidos = st.multiselect(f"Selecione os Instrumentos para a unidade '{unidade}'", instrumentos, key=f"inst_{unidade}")
        instrumentos_por_unidade[unidade] = instrumentos_escolhidos

# 4️⃣ Gerenciar múltiplos objetivos por instrumento usando `st.session_state`
if "objetivos_por_instrumento" not in st.session_state:
    st.session_state.objetivos_por_instrumento = {}

for unidade, instrumentos in instrumentos_por_unidade.items():
    for instrumento in instrumentos:
        chave = (unidade, instrumento)
        if chave not in st.session_state.objetivos_por_instrumento:
            st.session_state.objetivos_por_instrumento[chave] = []

        st.write(f"Objetivos para '{instrumento}' na unidade '{unidade}':")
        
        # Exibir os objetivos já adicionados
        for i, obj in enumerate(st.session_state.objetivos_por_instrumento[chave]):
            novo_obj = st.text_input(f"Objetivo {i + 1}:", value=obj, key=f"obj_{unidade}_{instrumento}_{i}")
            st.session_state.objetivos_por_instrumento[chave][i] = novo_obj

        # Adicionar novo objetivo
        if st.button(f"Adicionar Objetivo para '{instrumento}' (Unidade '{unidade}')", key=f"add_{unidade}_{instrumento}"):
            st.session_state.objetivos_por_instrumento[chave].append("")

# 5️⃣ Seleção de Eixos Temáticos para Cada Objetivo
eixos_por_objetivo = {}
if st.session_state.objetivos_por_instrumento:
    eixos = obter_dados("SELECT nome FROM eixo_tematico")
    for (unidade, instrumento), objetivos in st.session_state.objetivos_por_instrumento.items():
        for objetivo in objetivos:
            eixos_selecionados = st.multiselect(f"Eixos Temáticos para o Objetivo '{objetivo}'", eixos, key=f"eixo_{unidade}_{instrumento}_{objetivo}")
            eixos_por_objetivo[(unidade, instrumento, objetivo)] = eixos_selecionados

# 6️⃣ Seleção de Ações de Manejo para Cada Eixo Temático
acoes_por_eixo = {}
if eixos_por_objetivo:
    acoes = obter_dados("SELECT nome FROM acao_manejo")
    for (unidade, instrumento, objetivo), eixos in eixos_por_objetivo.items():
        for eixo in eixos:
            acoes_selecionadas = st.multiselect(f"Ações de Manejo para o Eixo '{eixo}' (Objetivo: {objetivo})", acoes, key=f"acao_{unidade}_{instrumento}_{objetivo}_{eixo}")
            acoes_por_eixo[(unidade, instrumento, objetivo, eixo)] = acoes_selecionadas

# 7️⃣ Salvar ou Atualizar Dados no Banco com Loading
def salvar_vinculacoes():
    with st.spinner("Salvando dados..."):
        try:
            conn = conectar_banco()
            cur = conn.cursor()

            for (unidade, instrumento), objetivos in st.session_state.objetivos_por_instrumento.items():
                for objetivo in objetivos:
                    if objetivo.strip():
                        # Verifica se o registro já existe
                        cur.execute(
                            """
                            SELECT COUNT(*) FROM vinculacoes
                            WHERE usuario = %s AND setor = %s AND unidade = %s AND instrumento = %s AND objetivo = %s
                            """,
                            (usuario, setor_escolhido, unidade, instrumento, objetivo)
                        )
                        existe = cur.fetchone()[0]

                        if existe:
                            # Atualiza o registro
                            cur.execute(
                                """
                                UPDATE vinculacoes
                                SET preenchido_em = %s
                                WHERE usuario = %s AND setor = %s AND unidade = %s AND instrumento = %s AND objetivo = %s
                                """,
                                (datetime.now(), usuario, setor_escolhido, unidade, instrumento, objetivo)
                            )
                        else:
                            # Insere novo registro
                            cur.execute(
                                """
                                INSERT INTO vinculacoes (usuario, setor, unidade, instrumento, objetivo, preenchido_em)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """,
                                (usuario, setor_escolhido, unidade, instrumento, objetivo, datetime.now())
                            )

                        for eixo in eixos_por_objetivo.get((unidade, instrumento, objetivo), []):
                            for acao in acoes_por_eixo.get((unidade, instrumento, objetivo, eixo), []):
                                cur.execute(
                                    """
                                    INSERT INTO vinculacoes (usuario, setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo, preenchido_em)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    """,
                                    (usuario, setor_escolhido, unidade, instrumento, objetivo, eixo, acao, datetime.now())
                                )

            conn.commit()
            conn.close()
            st.success("Dados salvos com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar os dados: {e}")

if st.button("Salvar Vinculações"):
    salvar_vinculacoes()
