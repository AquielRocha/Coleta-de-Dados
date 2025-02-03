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
    st.info("Preencha as informações passo a passo para registrar de maneira completa.")

    # Identificação do usuário via CPF
    cpf = st.text_input("Digite seu CPF:", max_chars=11, help="Digite apenas os números do CPF (sem pontos ou traços)")
    if not cpf.strip():
        st.warning("Por favor, insira seu CPF antes de continuar.")
        st.stop()

    # Seleção do Setor
    setores = obter_dados("SELECT DISTINCT nome FROM setor")
    setor_escolhido = st.selectbox("Selecione o Setor", setores)

    # Seleção de Unidade de Conservação (única)
    unidades = obter_dados("SELECT DISTINCT nome FROM unidade_conservacao")
    unidade_selecionada = st.selectbox("Selecione a Unidade de Conservação", unidades)

    # Seleção de Instrumentos para a unidade selecionada
    instrumentos = obter_dados("SELECT DISTINCT nome FROM instrumento")
    instrumentos_por_unidade = {}
    if unidade_selecionada:
        instrumentos_escolhidos = st.multiselect(
            f"Selecione os Instrumentos para '{unidade_selecionada}'",
            instrumentos,
            key=f"inst_{unidade_selecionada}"
        )
        instrumentos_por_unidade[unidade_selecionada] = instrumentos_escolhidos

    # Objetivos Específicos
    for unidade, instrumentos_list in instrumentos_por_unidade.items():
        for instrumento in instrumentos_list:
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
                        if st.button("x", key=f"remove_obj_{unidade}_{instrumento}_{idx}"):
                            st.session_state["objetivos_por_instrumento"][chave].pop(idx - 1)
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
    st.subheader("Resumo da Gestão")
    if setor_escolhido and unidade_selecionada:
        st.write(f"**Setor Selecionado:** {setor_escolhido}")
        st.write(f"### Unidade de Conservação: {unidade_selecionada}")
        for instrumento in instrumentos_por_unidade.get(unidade_selecionada, []):
            st.write(f"- **Instrumento:** {instrumento}")
            objetivos = st.session_state["objetivos_por_instrumento"].get((unidade_selecionada, instrumento), [])
            for objetivo in objetivos:
                st.write(f"  - **Objetivo:** {objetivo}")
                eixos = eixos_por_objetivo.get((unidade_selecionada, instrumento, objetivo), [])
                for eixo in eixos:
                    st.write(f"    - **Eixo Temático:** {eixo}")
                    acoes = acoes_por_eixo.get((unidade_selecionada, instrumento, objetivo, eixo), [])
                    st.write(f"      - **Ações de Manejo:** {', '.join(acoes) if acoes else 'Nenhuma'}")
    else:
        st.warning("Nenhum dado preenchido para exibição.")

    # Exportar para Excel
    dados_para_exportar = coletar_dados_para_exportar(
        cpf,
        setor_escolhido,
        instrumentos_por_unidade,
        st.session_state["objetivos_por_instrumento"],
        eixos_por_objetivo,
        acoes_por_eixo
    )
    if dados_para_exportar:
        excel_buffer = exportar_para_excel(dados_para_exportar)
        st.download_button(
            label="Exportar para Excel",
            data=excel_buffer,
            file_name="relacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Botão para Salvar as Vinculações
    if st.button("Salvar dados"):
        if validar_campos(
            cpf,
            setor_escolhido,
            unidade_selecionada,
            instrumentos_por_unidade,
            st.session_state["objetivos_por_instrumento"],
            eixos_por_objetivo
        ):
            salvar_vinculacoes(
                cpf,
                setor_escolhido,
                instrumentos_por_unidade,
                st.session_state["objetivos_por_instrumento"],
                eixos_por_objetivo,
                acoes_por_eixo
            )
        else:
            st.warning("Por favor, preencha todos os campos obrigatórios antes de salvar.")
