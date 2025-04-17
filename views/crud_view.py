import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
from controllers.vinculations_controller import (
    listar_vinculacoes,
    editar_vinculacao,
    deletar_vinculacao,
)
from models.database import obter_dados


# ---------------- util ---------------- #
def move_first(lst, value):
    """Coloca value como primeiro item da lista."""
    if value in lst:
        return [value] + [v for v in lst if v != value]
    return lst


# ------------- carregamento ------------ #
def carregar_registros(cpf_input: str):
    if not cpf_input.strip():
        st.error("Por favor, insira um CPF válido.")
        return None

    records = listar_vinculacoes(cpf=cpf_input)
    if not records:
        st.warning(
            "Nenhum dado encontrado para este CPF ou o usuário não tem setor vinculado."
        )
        return None
    return records


# -------------- exibição --------------- #
def exibir_registros(records):
    df = pd.DataFrame(
        records,
        columns=[
            "ID",
            "Nome",
            "Setor",
            "Unidade",
            "Instrumento",
            "Objetivo",
            "Eixo Temático",
            "Ação de Manejo",
            "Preenchido em",
            "Descrição do Instrumento",
        ],
    )

    ordem = [
        "Setor",
        "Unidade",
        "Descrição do Instrumento",
        "Instrumento",
        "Objetivo",
        "Eixo Temático",
        "Ação de Manejo",
        "Nome",
        "Preenchido em",
    ]
    df_view = df[ordem].copy()

    # Converte datetime para string (evita erro JSON)
    for c in df_view.select_dtypes(include=["datetime64[ns]", "datetimetz"]):
        df_view[c] = df_view[c].dt.strftime("%d/%m/%Y")

    ui.element(
        "h4",
        text="Registros de Manejo do seu setor",
        className="font-bold",
        key="hdr_tbl",
    )
    ui.table(data=df_view, maxHeight=400, key="tbl_registros")


# -------- opções para selects ---------- #
def obter_opcoes_cadastro():
    return (
        obter_dados("SELECT DISTINCT nome FROM setor", single_column=True),
        obter_dados(
            "SELECT DISTINCT nome FROM unidade_conservacao", single_column=True
        ),
        obter_dados("SELECT DISTINCT nome FROM instrumento", single_column=True),
        obter_dados("SELECT DISTINCT nome FROM eixo_tematico", single_column=True),
        obter_dados("SELECT DISTINCT nome FROM acao_manejo", single_column=True),
    )


# ------------- formulário -------------- #
def render_edit_delete_form(records):
    label_map = {
        f"Unidade: {r[3]} | Instrumento: {r[4]} | Objetivo: {r[5]}": r for r in records
    }

    ui.element("label", text="Selecione o registro para editar", key="lbl_sel")
    selected_label = ui.select(options=list(label_map.keys()), key="sel_registro")
    if not selected_label:
        return
    selected_record = label_map[selected_label]

    # Cabeçalho de edição
    ui.element(
        "h4",
        text=f"📝 Editando registro (ID {selected_record[0]})",
        className="mt-4 font-bold text-primary",
        key="hdr_editando",
    )

    # Nome apenas leitura
    ui.element(
        "p",
        text=f"Nome: {selected_record[1]}",
        className="font-semibold mb-2",
        key="nome_readonly",
    )

    setores, unidades, instrumentos, eixos, acoes = obter_opcoes_cadastro()

    # --- Setor ------------------------------------------------------------
    ui.element("label", text="Setor (editando)", className="text-gray-500", key="lbl_setor")
    setor = ui.select(options=move_first(setores, selected_record[2]), key="sel_setor")

    # --- Unidade ----------------------------------------------------------
    ui.element("label", text="Unidade de Conservação (editando)", className="text-gray-500", key="lbl_unid")
    unidade = ui.select(
        options=move_first(unidades, selected_record[3]), key="sel_unid"
    )

    # --- Instrumento ------------------------------------------------------
    ui.element("label", text="Instrumento (editando)", className="text-gray-500", key="lbl_inst")
    instrumento = ui.select(
        options=move_first(instrumentos, selected_record[4]), key="sel_inst"
    )

    # --- Objetivo ----------------------------------------------------------
    ui.element("label", text="Objetivo (editando)", className="text-gray-500", key="lbl_obj")
    objetivo = ui.input(
        default_value=selected_record[5],
        type="text",
        placeholder="Objetivo",
        key="txt_obj",
    )

    # --- Eixo Temático ----------------------------------------------------
    ui.element("label", text="Eixo Temático (editando)", className="text-gray-500", key="lbl_eixo")
    eixo_tematico = ui.select(
        options=move_first(eixos, selected_record[6]), key="sel_eixo"
    )

    # --- Ação de Manejo ---------------------------------------------------
    ui.element("label", text="Ação de Manejo (editando)", className="text-gray-500", key="lbl_acao")
    acao_manejo = ui.select(
        options=move_first(acoes, selected_record[7]), key="sel_acao"
    )

    # --- Descrição --------------------------------------------------------
    ui.element("label", text="Descrição do Instrumento (editando)", className="text-gray-500", key="lbl_desc")
    descricao_instrumento = ui.textarea(
        default_value=selected_record[9] or "",
        placeholder="Descrição do Instrumento",
        key="txt_desc",
    )

    # --- Botões -----------------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        if ui.button("💾 Salvar Alterações", key="btn_save"):
            editar_vinculacao(
                vinc_id=selected_record[0],
                setor=setor,
                unidade=unidade,
                instrumento=instrumento,
                objetivo=objetivo,
                eixo_tematico=eixo_tematico,
                acao_manejo=acao_manejo,
                descricao_instrumento=descricao_instrumento,
            )
            st.success("Alterações salvas!")
            st.session_state.pop("records", None)
            st.rerun()

    with col2:
        confirm = ui.switch(
            default_checked=False,
            label="Confirmo a exclusão",
            key="chk_del",
        )

        if ui.button(
            "🗑️ Deletar Registro", variant="destructive", key="btn_del"
        ) and confirm:
            deletar_vinculacao(selected_record[0])
            st.success("Registro deletado!")
            st.session_state.pop("records", None)
            st.rerun()


# ------------- view principal ----------- #
def render_crud_view():
    ui.element(
        "h2",
        text="Visualização e Gerenciamento",
        className="font-bold",
        key="hdr_main",
    )
    st.info(
        "Informe seu CPF para visualizar e gerenciar as informações de manejo. "
        "Somente registros vinculados ao setor do usuário serão exibidos."
    )

    # CPF input
    ui.element("label", text="CPF", key="lbl_cpf")
    cpf_input = ui.input(
        placeholder="Digite somente números do CPF…",
        type="text",
        key="cpf_input",
    )

    # Carregar dados
    if "records" not in st.session_state:
        if ui.button("🔍 Carregar dados", key="btn_load"):
            records = carregar_registros(cpf_input)
            if records is None:
                return
            st.session_state["records"] = records
    else:
        records = st.session_state["records"]
        exibir_registros(records)
        ui.element("hr", key="divider1")
        ui.element(
            "h3",
            text="Editar / Deletar Registros",
            className="font-medium",
            key="hdr_edit",
        )
        render_edit_delete_form(records)
