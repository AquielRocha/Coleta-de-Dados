# views/crud_view.py

import streamlit as st
import pandas as pd
from controllers.vinculations_controller import listar_vinculacoes, editar_vinculacao, deletar_vinculacao
from models.database import obter_dados


def carregar_registros(cpf_input):
    """
    Carrega os registros do usuário a partir do CPF informado.
    """
    if not cpf_input.strip():
        st.error("Por favor, insira um CPF válido.")
        return None
    
    records = listar_vinculacoes(cpf=cpf_input)
    if not records:
        st.warning("Nenhum dado encontrado para este CPF ou o usuário não tem setor vinculado.")
        return None
    
    return records


def exibir_registros(records):
    """
    Exibe os registros em formato de tabela, ocultando o ID para visualização.
    Cada 'record' é uma tupla com 9 colunas:
    [0]=ID, [1]=CPF, [2]=Setor, [3]=Unidade, [4]=Instrumento,
    [5]=Objetivo, [6]=Eixo, [7]=Ação, [8]=Preenchido em.
    """
    df = pd.DataFrame(
        records,
        columns=[
            "ID",
            "CPF",
            "Setor",
            "Unidade",
            "Instrumento",
            "Objetivo",
            "Eixo Temático",
            "Ação de Manejo",
            "Preenchido em",
        ],
    )
    # Cria uma cópia sem a coluna "ID" para exibição
    df_exibicao = df.drop(columns=["ID"])
    
    st.subheader("Registros de Manejo do seu setor")
    st.dataframe(df_exibicao, use_container_width=True)


def obter_opcoes_cadastro():
    """
    Obtém as opções para cada campo a partir do banco de dados.
    Aqui passamos single_column=True para retornar lista de strings, não tuplas.
    """
    setores_options = obter_dados(
        "SELECT DISTINCT nome FROM setor",
        single_column=True
    )
    unidades_options = obter_dados(
        "SELECT DISTINCT nome FROM unidade_conservacao",
        single_column=True
    )
    instrumentos_options = obter_dados(
        "SELECT DISTINCT nome FROM instrumento",
        single_column=True
    )
    eixos_options = obter_dados(
        "SELECT DISTINCT nome FROM eixo_tematico",
        single_column=True
    )
    acoes_options = obter_dados(
        "SELECT DISTINCT nome FROM acao_manejo",
        single_column=True
    )
    return (
        setores_options,
        unidades_options,
        instrumentos_options,
        eixos_options,
        acoes_options,
    )


def render_edit_delete_form(records):
    """
    Renderiza o formulário para edição e deleção dos registros.
    Cada registro em 'records' deve ter a estrutura:
      (id, cpf, setor, unidade, instrumento, objetivo, eixo, acao, preenchido_em)
    """
    # Cria um dicionário de opções para seleção do registro
    # Ex.: "Unidade: Parque X | Instrumento: Plano de Manejo | Objetivo: Preservar..." -> tupla dos dados
    options = {
        f"Unidade: {r[3]} | Instrumento: {r[4]} | Objetivo: {r[5]}": r
        for r in records
    }
    
    selected_label = st.selectbox(
        "Selecione o registro que deseja editar:",
        list(options.keys()),
        help="Selecione o registro correspondente à informação que você deseja alterar."
    )
    selected_record = options[selected_label]

    st.markdown("### Dados Selecionados para Edição")
    st.write("Confira os dados abaixo. O campo **CPF** é somente leitura. Você pode alterar os demais campos, se necessário.")
    
    # Exibe o CPF em modo somente leitura
    st.text_input(
        "CPF (somente leitura)",
        value=selected_record[1],
        disabled=True
    )

    # Carrega as opções (já em formato de lista de strings)
    (
        setores_options,
        unidades_options,
        instrumentos_options,
        eixos_options,
        acoes_options,
    ) = obter_opcoes_cadastro()

    # selected_record[2] = setor atual
    try:
        setor = st.selectbox(
            "Selecione o Setor",
            options=setores_options,
            index=setores_options.index(selected_record[2]) if selected_record[2] in setores_options else 0,
            help="Selecione o setor correspondente à sua área de atuação."
        )
    except Exception as e:
        st.error(f"Erro ao carregar o setor: {e}")
        setor = selected_record[2]  # fallback

    # selected_record[3] = unidade atual
    try:
        unidade = st.selectbox(
            "Selecione a Unidade de Conservação",
            options=unidades_options,
            index=unidades_options.index(selected_record[3]) if selected_record[3] in unidades_options else 0,
            help="Selecione a unidade de conservação correta."
        )
    except Exception as e:
        st.error(f"Erro ao carregar a unidade: {e}")
        unidade = selected_record[3]  # fallback

    # selected_record[4] = instrumento atual
    try:
        instrumento = st.selectbox(
            "Selecione o Instrumento",
            options=instrumentos_options,
            index=instrumentos_options.index(selected_record[4]) if selected_record[4] in instrumentos_options else 0,
            help="Selecione o instrumento utilizado."
        )
    except Exception as e:
        st.error(f"Erro ao carregar o instrumento: {e}")
        instrumento = selected_record[4]  # fallback

    # selected_record[5] = objetivo atual (texto livre)
    objetivo = st.text_input(
        "Digite o Objetivo",
        value=selected_record[5],
        help="Edite o objetivo conforme necessário. Este campo permite entrada livre de texto."
    )

    # selected_record[6] = eixo temático atual
    try:
        eixo_tematico = st.selectbox(
            "Selecione o Eixo Temático",
            options=eixos_options,
            index=eixos_options.index(selected_record[6]) if selected_record[6] in eixos_options else 0,
            help="Selecione o eixo temático correspondente."
        )
    except Exception as e:
        st.error(f"Erro ao carregar o eixo temático: {e}")
        eixo_tematico = selected_record[6]  # fallback

    # selected_record[7] = ação de manejo atual
    try:
        acao_manejo = st.selectbox(
            "Selecione a Ação de Manejo",
            options=acoes_options,
            index=acoes_options.index(selected_record[7]) if selected_record[7] in acoes_options else 0,
            help="Selecione a ação de manejo adequada."
        )
    except Exception as e:
        st.error(f"Erro ao carregar a ação de manejo: {e}")
        acao_manejo = selected_record[7]  # fallback

    st.markdown("### Confirmação")
    st.info("Revise os dados alterados abaixo.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar Alterações"):
            editar_vinculacao(
                vinc_id=selected_record[0],
                setor=setor,
                unidade=unidade,
                instrumento=instrumento,
                objetivo=objetivo,
                eixo_tematico=eixo_tematico,
                acao_manejo=acao_manejo
            )
            st.success("Alterações salvas com sucesso!")
            # Limpa os registros em cache para forçar recarregar da base
            if "records" in st.session_state:
                del st.session_state["records"]
    
    with col2:
        if st.button("Deletar Registro"):
            if st.checkbox(
                "Confirmo que desejo deletar este registro",
                key="confirm_delete",
                help="Marque esta opção para confirmar a exclusão do registro selecionado."
            ):
                deletar_vinculacao(selected_record[0])
                st.success("Registro deletado com sucesso!")
                if "records" in st.session_state:
                    del st.session_state["records"]
            else:
                st.warning("Por favor, confirme que deseja deletar este registro.")


def render_crud_view():
    st.markdown("<h1 style='color:#E5EFE3;'>Visualização e Gerenciamento</h1>", unsafe_allow_html=True)
    st.info("Informe seu CPF para visualizar e gerenciar as informações de manejo. Somente registros vinculados ao setor do usuário serão exibidos.")

    cpf_input = st.text_input(
        "Digite seu CPF:",
        max_chars=11,
        help="Somente números, sem pontos ou traços."
    )

    # Se os registros ainda não foram carregados, exibe o botão para carregá-los
    if "records" not in st.session_state:
        if st.button("Carregar dados do Usuário"):
            records = carregar_registros(cpf_input)
            if records is None:
                return  # Se não encontrou registros ou CPF inválido, interrompe
            st.session_state["records"] = records
            st.session_state["cpf"] = cpf_input
        else:
            return

    # Se já temos "records" armazenados na sessão
    records = st.session_state["records"]

    # Exibe os registros em tabela
    exibir_registros(records)

    st.markdown("---")
    st.subheader("Editar / Deletar Registros")
    render_edit_delete_form(records)
