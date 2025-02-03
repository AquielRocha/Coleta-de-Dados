# views/main_view.py
import streamlit as st
from datetime import datetime
from models.database import obter_dados
from controllers.vinculations_controller import salvar_vinculacoes, coletar_dados_para_exportar
from utils.export_utils import exportar_para_excel
from utils.validation import validar_campos

def render():
    # Inicializando estados no Streamlit
    if "objetivos_por_instrumento" not in st.session_state:
        st.session_state["objetivos_por_instrumento"] = {}
    if "objetivos_inputs" not in st.session_state:
        st.session_state["objetivos_inputs"] = {}

    st.title("Gestão de Manejo - ICMBio")
    st.info("Preencha as informações passo a passo para registrar as vinculações de maneira completa.")

    # Identificação do usuário
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

    # Objetivos Específicos
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

            # Exibir lista de objetivos adicionados
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

    # Resumo das Vinculações
    st.subheader("Resumo das Vinculações")
    if setor_escolhido and unidades_selecionadas:
        st.write(f"**Setor Selecionado:** {setor_escolhido}")
        for unidade in unidades_selecionadas:
            st.write(f"### Unidade de Conservação: {unidade}")
            for instrumento in instrumentos_por_unidade.get(unidade, []):
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

    # Exportar para Excel
    dados_para_exportar = coletar_dados_para_exportar(
        usuario,
        setor_escolhido,
        instrumentos_por_unidade,
        st.session_state["objetivos_por_instrumento"],
        eixos_por_objetivo,
        acoes_por_eixo
    )
    if dados_para_exportar:
        excel_buffer = exportar_para_excel(dados_para_exportar)
        st.download_button(
            label="Exportar Vinculações para Excel",
            data=excel_buffer,
            file_name="vinculacoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Botão para Salvar as Vinculações
    if st.button("Salvar Vinculações"):
        if validar_campos(
            usuario,
            setor_escolhido,
            unidades_selecionadas,
            instrumentos_por_unidade,
            st.session_state["objetivos_por_instrumento"],
            eixos_por_objetivo
        ):
            salvar_vinculacoes(
                usuario,
                setor_escolhido,
                instrumentos_por_unidade,
                st.session_state["objetivos_por_instrumento"],
                eixos_por_objetivo,
                acoes_por_eixo
            )
        else:
            st.warning("Por favor, preencha todos os campos obrigatórios antes de salvar.")
