import streamlit as st
import psycopg2
from datetime import datetime

# Função para conectar ao banco de dados PostgreSQL
def conectar_banco():
    return psycopg2.connect(
        dbname="db_samge_hmg",
        user="samge_read",
        password="samge_read",
        host="162.243.243.165",
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

# Seleção do Setor
setores = obter_dados("SELECT DISTINCT nome FROM setor")
setor_escolhido = st.selectbox("Selecione o Setor", setores)

# Seleção de Unidades
unidades = obter_dados("SELECT DISTINCT nome FROM unidade_conservacao")
unidades_selecionadas = st.multiselect("Selecione as Unidades de Conservação", unidades)

# Seleção de Instrumentos
instrumentos = obter_dados("SELECT DISTINCT nome FROM instrumento")
instrumentos_por_unidade = {}
if unidades_selecionadas:
    for unidade in unidades_selecionadas:
        instrumentos_escolhidos = st.multiselect(f"Selecione os Instrumentos para '{unidade}'", instrumentos, key=f"inst_{unidade}")
        instrumentos_por_unidade[unidade] = instrumentos_escolhidos

# Gerenciar múltiplos objetivos por instrumento
if "objetivos_por_instrumento" not in st.session_state:
    st.session_state.objetivos_por_instrumento = {}

for unidade, instrumentos in instrumentos_por_unidade.items():
    for instrumento in instrumentos:
        chave = (unidade, instrumento)
        if chave not in st.session_state.objetivos_por_instrumento:
            st.session_state.objetivos_por_instrumento[chave] = [""]

        st.write(f"### Objetivos para '{instrumento}' na unidade '{unidade}':")
        
        # Exibir campos para os objetivos adicionados
        for i, obj in enumerate(st.session_state.objetivos_por_instrumento[chave]):
            cols = st.columns([4, 1])  # Campo + botão de remoção
            with cols[0]:
                st.session_state.objetivos_por_instrumento[chave][i] = st.text_input(
                    f"Objetivo {i + 1}:", value=obj, key=f"obj_{unidade}_{instrumento}_{i}")
            with cols[1]:
                if st.button("❌", key=f"remove_{unidade}_{instrumento}_{i}"):
                    st.session_state.objetivos_por_instrumento[chave].pop(i)
                    st.rerun()

        # Exibir opção para adicionar mais objetivos
        adicionar_mais = st.radio(
            f"Deseja adicionar mais objetivos para '{instrumento}'?",
            ["Não", "Sim"],
            key=f"add_more_{unidade}_{instrumento}",
            index=0
        )
        if adicionar_mais == "Sim":
            st.session_state.objetivos_por_instrumento[chave].append("")

# Seleção de Eixos Temáticos para Cada Objetivo
eixos_por_objetivo = {}
if st.session_state.objetivos_por_instrumento:
    eixos = obter_dados("SELECT nome FROM eixo_tematico")
    for (unidade, instrumento), objetivos in st.session_state.objetivos_por_instrumento.items():
        for objetivo in objetivos:
            if objetivo.strip():
                eixos_selecionados = st.multiselect(
                    f"Eixos Temáticos para o Objetivo '{objetivo}'",
                    eixos,
                    key=f"eixo_{unidade}_{instrumento}_{objetivo}"
                )
                eixos_por_objetivo[(unidade, instrumento, objetivo)] = list(set(eixos_selecionados))

# Seleção de Ações de Manejo para Cada Eixo Temático
acoes_por_eixo = {}
if eixos_por_objetivo:
    acoes = obter_dados("SELECT nome FROM acao_manejo")
    for (unidade, instrumento, objetivo), eixos in eixos_por_objetivo.items():
        for eixo in eixos:
            acoes_selecionadas = st.multiselect(
                f"Ações de Manejo para o Eixo '{eixo}' (Objetivo: {objetivo})",
                acoes,
                key=f"acao_{unidade}_{instrumento}_{objetivo}_{eixo}"
            )
            acoes_por_eixo[(unidade, instrumento, objetivo, eixo)] = list(set(acoes_selecionadas))

# Exibir Resumo Antes de Salvar
st.subheader("Resumo das Vinculações")
if setor_escolhido and unidades_selecionadas:
    st.write(f"**Setor Selecionado:** {setor_escolhido}")
    for unidade in unidades_selecionadas:
        st.write(f"### Unidade de Conservação: {unidade}")
        instrumentos = instrumentos_por_unidade.get(unidade, [])
        if instrumentos:
            st.write(f"- **Instrumentos:** {', '.join(instrumentos)}")
            for instrumento in instrumentos:
                chave = (unidade, instrumento)
                objetivos = st.session_state.objetivos_por_instrumento.get(chave, [])
                for i, objetivo in enumerate(objetivos):
                    st.write(f"  - Objetivo {i + 1}: {objetivo}")
                    eixos = eixos_por_objetivo.get((unidade, instrumento, objetivo), [])
                    for eixo in eixos:
                        st.write(f"    - Eixo: {eixo}")
                        acoes = acoes_por_eixo.get((unidade, instrumento, objetivo, eixo), [])
                        for acao in acoes:
                            st.write(f"      - Ação de Manejo: {acao}")
else:
    st.warning("Nenhum dado preenchido para exibição.")

# Função para salvar os dados no banco
def salvar_vinculacoes():
    with st.spinner("Salvando dados..."):
        try:
            conn = conectar_banco()
            cur = conn.cursor()
            for (unidade, instrumento), objetivos in st.session_state.objetivos_por_instrumento.items():
                for objetivo in objetivos:
                    if objetivo.strip():
                        cur.execute(
                            """
                            INSERT INTO vinculacoes (usuario, setor, unidade, instrumento, objetivo, preenchido_em)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (usuario, setor_escolhido, unidade, instrumento, objetivo, datetime.now())
                        )
            conn.commit()
            conn.close()
            st.success("Dados salvos com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar os dados: {e}")

# Botão de salvamento
if setor_escolhido and unidades_selecionadas:
    if st.button("Salvar Vinculações"):
        salvar_vinculacoes()
else:
    st.warning("Complete as informações antes de salvar.")
