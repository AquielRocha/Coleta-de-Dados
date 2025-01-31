import streamlit as st
import psycopg2
import pandas as pd
from io import BytesIO
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

# Função para buscar dados de uma tabela com caching
@st.cache_data(ttl=600)  # Cache por 10 minutos
def obter_dados(query, params=None):
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute(query, params if params else ())
        dados = cur.fetchall()
        cur.close()
        conn.close()
        return [d[0] for d in dados]
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return []

# Inicializando estados do Streamlit
if "objetivos_por_instrumento" not in st.session_state:
    st.session_state["objetivos_por_instrumento"] = {}

if "objetivos_inputs" not in st.session_state:
    st.session_state["objetivos_inputs"] = {}

# Interface no Streamlit
st.title("Gestão de Manejo - ICMBio")
st.info("Preencha as informações passo a passo para registrar as vinculações de maneira completa.")

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

# Seleção de Objetivos Específicos (Substituído por Input de Texto)
objetivos_disponiveis = []  # Não estamos mais usando objetivos pré-definidos

for unidade, instrumentos in instrumentos_por_unidade.items():
    for instrumento in instrumentos:
        chave = (unidade, instrumento)
        if chave not in st.session_state["objetivos_por_instrumento"]:
            st.session_state["objetivos_por_instrumento"][chave] = []
        if chave not in st.session_state["objetivos_inputs"]:
            st.session_state["objetivos_inputs"][chave] = ""

        st.write(f"### Objetivos para '{instrumento}' na unidade '{unidade}':")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            novo_objetivo = st.text_input(
                f"Adicione um Objetivo Específico para '{instrumento}' na unidade '{unidade}':",
                key=f"novo_obj_{unidade}_{instrumento}"
            )
        with col2:
            if st.button("Adicionar", key=f"add_obj_{unidade}_{instrumento}"):
                if novo_objetivo.strip():
                    if novo_objetivo.strip() not in st.session_state["objetivos_por_instrumento"][chave]:
                        st.session_state["objetivos_por_instrumento"][chave].append(novo_objetivo.strip())
                        st.session_state["objetivos_inputs"][chave] = ""
                    else:
                        st.warning("Este objetivo já foi adicionado.")
                else:
                    st.warning("Por favor, insira um objetivo válido antes de adicionar.")

        # Exibir Lista de Objetivos Adicionados
        objetivos_atualizados = st.session_state["objetivos_por_instrumento"][chave]
        if objetivos_atualizados:
            st.write("**Objetivos Adicionados:**")
            for idx, obj in enumerate(objetivos_atualizados, 1):
                col3, col4 = st.columns([10, 1])
                with col3:
                    st.write(f"{idx}. {obj}")
                with col4:
                    if st.button("Remover", key=f"remove_obj_{unidade}_{instrumento}_{idx}"):
                        st.session_state["objetivos_por_instrumento"][chave].pop(idx-1)
                        st.experimental_rerun()

# Seleção de Eixos Temáticos
eixos_por_objetivo = {}
eixos = obter_dados("SELECT nome FROM eixo_tematico")
if st.session_state["objetivos_por_instrumento"]:
    for (unidade, instrumento), objetivos in st.session_state["objetivos_por_instrumento"].items():
        for objetivo in objetivos:
            eixos_selecionados = st.multiselect(
                f"Eixos Temáticos para o Objetivo '{objetivo}' no Instrumento '{instrumento}' na Unidade '{unidade}'",
                eixos,
                key=f"eixo_{unidade}_{instrumento}_{objetivo}"
            )
            eixos_por_objetivo[(unidade, instrumento, objetivo)] = eixos_selecionados

# Seleção de Ações de Manejo
acoes_por_eixo = {}
acoes = obter_dados("SELECT nome FROM acao_manejo")
if eixos_por_objetivo:
    for (unidade, instrumento, objetivo), eixos in eixos_por_objetivo.items():
        for eixo in eixos:
            acoes_selecionadas = st.multiselect(
                f"Ações de Manejo para o Eixo '{eixo}' (Objetivo: {objetivo})",
                acoes,
                key=f"acao_{unidade}_{instrumento}_{objetivo}_{eixo}"
            )
            acoes_por_eixo[(unidade, instrumento, objetivo, eixo)] = acoes_selecionadas

# Exibir Resumo Antes de Salvar
st.subheader("Resumo das Vinculações")
if setor_escolhido and unidades_selecionadas:
    st.write(f"**Setor Selecionado:** {setor_escolhido}")
    for unidade in unidades_selecionadas:
        st.write(f"### Unidade de Conservação: {unidade}")
        instrumentos = instrumentos_por_unidade.get(unidade, [])
        for instrumento in instrumentos:
            st.write(f"- **Instrumento:** {instrumento}")
            objetivos = st.session_state["objetivos_por_instrumento"].get((unidade, instrumento), [])
            for objetivo in objetivos:
                st.write(f"  - **Objetivo:** {objetivo}")
                eixos = eixos_por_objetivo.get((unidade, instrumento, objetivo), [])
                for eixo in eixos:
                    st.write(f"    - **Eixo Temático:** {eixo}")
                    acoes = acoes_por_eixo.get((unidade, instrumento, objetivo, eixo), [])
                    st.write(f"      - **Ações de Manejo:** {', '.join(acoes) if acoes else 'Nenhuma'}")
else:
    st.warning("Nenhum dado preenchido para exibição.")

# Função para exportar dados para Excel
def exportar_para_excel(dados):
    df = pd.DataFrame(dados, columns=["Setor", "Unidade", "Instrumento", "Objetivo", "Eixo Temático", "Ação de Manejo", "Usuário", "Preenchido em"])
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:  # Use 'openpyxl' aqui
        df.to_excel(writer, index=False, sheet_name='Vinculações')
    buffer.seek(0)
    return buffer

# Função para coletar os dados para exportação
def coletar_dados_para_exportar():
    dados = []
    for unidade, instrumentos in instrumentos_por_unidade.items():
        for instrumento in instrumentos:
            objetivos = st.session_state["objetivos_por_instrumento"].get((unidade, instrumento), [])
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

# Função para salvar os dados no banco
def salvar_vinculacoes():
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        for unidade, instrumentos in instrumentos_por_unidade.items():
            for instrumento in instrumentos:
                objetivos = st.session_state["objetivos_por_instrumento"].get((unidade, instrumento), [])
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
                            # Caso não haja ações de manejo selecionadas, insere 'Nenhuma'
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

# Função para validar se todos os campos obrigatórios estão preenchidos
def validar_campos():
    if not usuario.strip():
        st.error("O campo de usuário está vazio.")
        return False
    if not setor_escolhido:
        st.error("Nenhum setor selecionado.")
        return False
    if not unidades_selecionadas:
        st.error("Nenhuma unidade de conservação selecionada.")
        return False
    for unidade, instrumentos in instrumentos_por_unidade.items():
        if not instrumentos:
            st.error(f"Não há instrumentos selecionados para a unidade '{unidade}'.")
            return False
        for instrumento in instrumentos:
            objetivos = st.session_state["objetivos_por_instrumento"].get((unidade, instrumento), [])
            if not objetivos:
                st.error(f"Não há objetivos adicionados para o instrumento '{instrumento}' na unidade '{unidade}'.")
                return False
            for objetivo in objetivos:
                eixos = eixos_por_objetivo.get((unidade, instrumento, objetivo), [])
                if not eixos:
                    st.error(f"Não há eixos temáticos selecionados para o objetivo '{objetivo}' no instrumento '{instrumento}' na unidade '{unidade}'.")
                    return False
    return True

# Botão de exportação para Excel
dados_para_exportar = coletar_dados_para_exportar()
if dados_para_exportar:
    excel_buffer = exportar_para_excel(dados_para_exportar)
    st.download_button(
        label="Exportar Vinculações para Excel",
        data=excel_buffer,
        file_name="vinculacoes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Botão de salvamento com validação
if st.button("Salvar Vinculações"):
    if validar_campos():
        salvar_vinculacoes()
    else:
        st.warning("Por favor, preencha todos os campos obrigatórios antes de salvar.")
