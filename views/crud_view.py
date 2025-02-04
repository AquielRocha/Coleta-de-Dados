# views/crud_view.py
import streamlit as st
import pandas as pd
from controllers.vinculations_controller import listar_vinculacoes, editar_vinculacao, deletar_vinculacao
from models.database import obter_dados

def render_crud_view():
    st.markdown("<h1 style='color:#E5EFE3;'>Visualização e Gerenciamento</h1>", unsafe_allow_html=True)
    st.info("Informe seu CPF para visualizar e gerenciar as informações de manejo. Por favor, verifique cuidadosamente os dados antes de confirmar qualquer alteração ou exclusão.")

    # Entrada do CPF
    cpf_input = st.text_input(
        "Digite seu CPF:", 
        max_chars=11, 
        help="Somente números, sem pontos ou traços."
    )

    # Se os dados ainda não foram carregados, exibe o botão para carregamento
    if "records" not in st.session_state:
        if st.button("Carregar dados do Usuário"):
            if cpf_input.strip() == "":
                st.error("Por favor, insira um CPF válido.")
                return

            # Lista os registros filtrados pelo CPF
            records = listar_vinculacoes(cpf=cpf_input)
            if not records:
                st.warning("Nenhum dado encontrado para este CPF.")
                return

            st.session_state["records"] = records
            st.session_state["cpf"] = cpf_input
        else:
            # Se o botão ainda não foi clicado, encerra a função
            return

    # Se os dados já foram carregados, utiliza-os
    records = st.session_state["records"]
    cpf_input = st.session_state["cpf"]

    # Converter os registros para DataFrame para visualização (escondendo a coluna de ID)
    df = pd.DataFrame(records, columns=[
        "ID", "CPF", "Setor", "Unidade", "Instrumento", "Objetivo", "Eixo Temático", "Ação de Manejo", "Preenchido em"
    ])
    if "ID" in df.columns:
        df = df.drop(columns=["ID"])
    st.subheader("Seus Registros de Manejo")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Editar / Deletar Registros")

    # Cria um dicionário para associar uma label descritiva a cada registro (não exibe o ID para o usuário)
    options = {
        f"{r[3]} | {r[4]} | {r[5]}": r   # r[3]: Unidade, r[4]: Instrumento, r[5]: Objetivo
        for r in records
    }
    selected_label = st.selectbox("Selecione o registro que deseja editar:", list(options.keys()), 
                                  help="Selecione o registro correspondente à informação que você deseja alterar.")
    selected_record = options[selected_label]

    st.markdown("### Dados Selecionados para Edição")
    st.write("Confira os dados abaixo. O campo CPF é somente leitura. Você pode alterar os demais campos se necessário.")
    st.text_input("CPF (somente leitura)", value=selected_record[1], disabled=True)

    # Carrega as opções para cada campo a partir do banco de dados
    setores_options      = obter_dados("SELECT DISTINCT nome FROM setor")
    unidades_options     = obter_dados("SELECT DISTINCT nome FROM unidade_conservacao")
    instrumentos_options = obter_dados("SELECT DISTINCT nome FROM instrumento")
    eixos_options        = obter_dados("SELECT DISTINCT nome FROM eixo_tematico")
    acoes_options        = obter_dados("SELECT DISTINCT nome FROM acao_manejo")

    # Campo "Setor" com selectbox
    try:
        setor = st.selectbox(
            "Selecione o Setor",
            options=setores_options,
            index=setores_options.index(selected_record[2]) if selected_record[2] in setores_options else 0,
            help="Selecione o setor correspondente à sua área de atuação."
        )
    except Exception as e:
        st.error(f"Erro ao carregar o setor: {e}")
        setor = selected_record[2]

    # Campo "Unidade de Conservação" com selectbox
    try:
        unidade = st.selectbox(
            "Selecione a Unidade de Conservação",
            options=unidades_options,
            index=unidades_options.index(selected_record[3]) if selected_record[3] in unidades_options else 0,
            help="Selecione a unidade de conservação correta."
        )
    except Exception as e:
        st.error(f"Erro ao carregar a unidade: {e}")
        unidade = selected_record[3]

    # Campo "Instrumento" com selectbox
    try:
        instrumento = st.selectbox(
            "Selecione o Instrumento",
            options=instrumentos_options,
            index=instrumentos_options.index(selected_record[4]) if selected_record[4] in instrumentos_options else 0,
            help="Selecione o instrumento utilizado."
        )
    except Exception as e:
        st.error(f"Erro ao carregar o instrumento: {e}")
        instrumento = selected_record[4]

    # Campo "Objetivo" como text_input para permitir edição livre
    objetivo = st.text_input(
        "Digite o Objetivo", 
        value=selected_record[5],
        help="Edite o objetivo conforme necessário. Este campo permite entrada livre de texto."
    )

    # Campo "Eixo Temático" com selectbox
    try:
        eixo_tematico = st.selectbox(
            "Selecione o Eixo Temático",
            options=eixos_options,
            index=eixos_options.index(selected_record[6]) if selected_record[6] in eixos_options else 0,
            help="Selecione o eixo temático correspondente."
        )
    except Exception as e:
        st.error(f"Erro ao carregar o eixo temático: {e}")
        eixo_tematico = selected_record[6]

    # Campo "Ação de Manejo" com selectbox
    try:
        acao_manejo = st.selectbox(
            "Selecione a Ação de Manejo",
            options=acoes_options,
            index=acoes_options.index(selected_record[7]) if selected_record[7] in acoes_options else 0,
            help="Selecione a ação de manejo adequada."
        )
    except Exception as e:
        st.error(f"Erro ao carregar a ação de manejo: {e}")
        acao_manejo = selected_record[7]

    st.markdown("### Confirmação")
    st.info("Revise os dados alterados e confirme a operação desejada abaixo.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar Alterações"):
            if st.checkbox("Confirmo que desejo salvar as alterações", key="confirm_save", help="Marque esta opção para confirmar que deseja salvar as alterações feitas."):
                editar_vinculacao(
                    selected_record[0],
                    setor,
                    unidade,
                    instrumento,
                    objetivo,
                    eixo_tematico,
                    acao_manejo
                )
                st.success("Alterações salvas com sucesso!")
                # Limpa os registros para recarregar os dados na próxima ação
                if "records" in st.session_state:
                    del st.session_state["records"]
                st.experimental_rerun()
            else:
                st.warning("Por favor, confirme que deseja salvar as alterações.")

    with col2:
        if st.button("Deletar Registro"):
            if st.checkbox("Confirmo que desejo deletar este registro", key="confirm_delete", help="Marque esta opção para confirmar a exclusão do registro selecionado."):
                deletar_vinculacao(selected_record[0])
                st.success("Registro deletado com sucesso!")
                if "records" in st.session_state:
                    del st.session_state["records"]
                st.experimental_rerun()
            else:
                st.warning("Por favor, confirme que deseja deletar este registro.")
