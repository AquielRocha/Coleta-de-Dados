import streamlit as st
from datetime import datetime
import streamlit_shadcn_ui as ui

# ---- import interno ----------------------------------------------------- #
from models.database import conectar_banco, obter_dados
from controllers.vinculations_controller import (
    salvar_vinculacoes,
    coletar_dados_para_exportar,
)
from utils.export_utils import exportar_para_excel
from utils.validation import validar_campos
from views.components.toast import show_toast


# ========================= helpers / cache ============================== #
@st.cache_data(show_spinner=False)
def get_cached_data(query: str, single_column: bool = False):
    return obter_dados(query, single_column=single_column)


def update_usuario_setor(cpf: str, novo_setor: str):
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute("SELECT id FROM setor WHERE nome = %s", (novo_setor,))
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE usuarios SET setor_id = %s WHERE cpf = %s", (row[0], cpf)
            )
            conn.commit()
        cur.close()
        conn.close()
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao atualizar setor do usuário: {e}")


# ========================= blocos de UI ================================= #
def render_identificacao():
    ui.element("h3", text="Identificação", className="font-bold", key="hdr_ident")

    cpf = ui.input(
        placeholder="Digite somente números do CPF...",
        type="text",
        key="cpf_input",
    ).strip()

    if not cpf:
        st.warning("Por favor, insira seu CPF para prosseguir.")
        st.stop()

    # Consulta usuário
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT u.nome, s.nome
              FROM usuarios u
              JOIN setor s ON u.setor_id = s.id
             WHERE u.cpf = %s
            """,
            (cpf,),
        )
        usuario = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao consultar o banco de dados: {e}")
        st.stop()

    if usuario:
        nome_usuario, setor = usuario
        st.session_state.update(
            {
                "user_registrado": True,
                "setor_registrado": setor,
                "cpf": cpf,
            }
        )
        show_toast(f"Bem‑vindo de volta, {nome_usuario}!", "info")
    else:
        st.session_state["user_registrado"] = False
        nome_usuario = ui.input(
            placeholder="Digite seu nome completo...",
            type="text",
            key="nome_usuario",
        ).strip()

        setores = get_cached_data("SELECT DISTINCT nome FROM setor", True)
        setor = ui.select(
            label="Setor",
            options=setores,
            key="setor_selectbox",
        )
        st.session_state["setor_registrado"] = setor

    return cpf, nome_usuario, st.session_state["setor_registrado"]


def render_setor():
    setores = get_cached_data("SELECT DISTINCT nome FROM setor", True)

    if st.session_state.get("user_registrado"):
        atual = st.session_state["setor_registrado"]
        st.info(f"Setor atual: {atual}")
        deseja_mudar = ui.switch(
            default_checked=False, label="Desejo mudar de setor", key="mudar_setor"
        )
        if deseja_mudar:
            setor_escolhido = ui.select(
                label="Novo setor",
                options=setores,
                key="setor_alterado",
            )
            if setor_escolhido and setor_escolhido != atual:
                st.warning(
                    f"Ao mudar de setor, você não poderá visualizar os dados do setor {atual}."
                )
                cpf = st.session_state.get("cpf")
                update_usuario_setor(cpf, setor_escolhido)
                st.session_state["setor_registrado"] = setor_escolhido
        else:
            setor_escolhido = atual
    else:
        setor_escolhido = st.session_state.get("setor_registrado")

    return setor_escolhido


def render_instrumentos_unidades():
    instrumentos = get_cached_data("SELECT id, nome FROM instrumento")
    if not instrumentos:
        st.error("Nenhum instrumento encontrado.")
        st.stop()

    instrumentos_sel = st.multiselect(
        "Selecione os Instrumentos",
        options=instrumentos,
        format_func=lambda x: x[1],
        key="instrumento_multiselect",
    )

    unidades = get_cached_data("SELECT DISTINCT nome FROM unidade_conservacao", True)

    instrumentos_unidades = {}
    if instrumentos_sel:
        if len(instrumentos_sel) == 1:
            instrumento = instrumentos_sel[0]
            if instrumento[0] == 8:  # PANs
                ucs = st.multiselect(
                    f"Unidades de Conservação para '{instrumento[1]}' (PANs)",
                    options=unidades,
                    key=f"uc_multiselect_{instrumento[0]}",
                )
            else:
                uc = ui.select(
                    label=f"Unidade de Conservação para '{instrumento[1]}'",
                    options=unidades,
                    key=f"uc_selectbox_{instrumento[0]}",
                )
                ucs = [uc] if uc else []
            instrumentos_unidades[instrumento] = ucs
        else:  # vários instrumentos → mesma UC
            uc = ui.select(
                label="Unidade de Conservação (comum)",
                options=unidades,
                key="uc_common_selectbox",
            )
            ucs = [uc] if uc else []
            for inst in instrumentos_sel:
                instrumentos_unidades[inst] = ucs

    # Descrição por instrumento
    descricao_instrumento = {}
    if instrumentos_sel:
        ui.element("h4", text="Descrição dos Instrumentos", key="hdr_desc", className="mt-4")
        for inst in instrumentos_sel:
            desc = ui.input(
                placeholder=f"Descrição para {inst[1]}",
                type="text",
                key=f"desc_{inst[0]}",
            )
            descricao_instrumento[inst] = desc

    return instrumentos_unidades, descricao_instrumento


def render_objetivos(instrumentos_unidades):
    if "objetivos_por_instrumento" not in st.session_state:
        st.session_state["objetivos_por_instrumento"] = {}

    ui.element("h3", text="Objetivos Específicos", key="hdr_obj", className="mt-6")

    for instrumento in instrumentos_unidades.keys():
        inst_id, inst_nome = instrumento
        chave = (inst_id, inst_nome)
        st.session_state["objetivos_por_instrumento"].setdefault(chave, [])

        novo_obj = ui.input(
            placeholder=f"Novo objetivo para {inst_nome}...",
            type="text",
            key=f"novo_obj_{inst_id}",
        )

        if ui.button(f"Adicionar objetivo para {inst_nome}", key=f"btn_add_obj_{inst_id}"):
            if novo_obj.strip():
                lst = st.session_state["objetivos_por_instrumento"][chave]
                if novo_obj not in lst:
                    lst.append(novo_obj)
                else:
                    st.warning("Objetivo já adicionado.")
            else:
                st.warning("Digite um objetivo válido antes de adicionar.")

        # listagem
        for idx, obj in enumerate(st.session_state["objetivos_por_instrumento"][chave]):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.write(f"{idx+1}. {obj}")
            with col2:
                if ui.button("🗑️", key=f"rem_obj_{inst_id}_{idx}"):
                    st.session_state["objetivos_por_instrumento"][chave].pop(idx)

    return st.session_state["objetivos_por_instrumento"]


def render_eixos(objetivos_por_instrumento):
    eixos = get_cached_data("SELECT nome FROM eixo_tematico", True)

    if "eixos_por_objetivo" not in st.session_state:
        st.session_state["eixos_por_objetivo"] = {}

    ui.element("h3", text="Eixos Temáticos", key="hdr_eixo", className="mt-6")
    st.info("Selecione os eixos relacionados a cada objetivo.")

    for (inst_id, inst_nome), objetivos in objetivos_por_instrumento.items():
        for obj in objetivos:
            chave = (inst_id, inst_nome, obj)
            eixos_sel = st.multiselect(
                f"Eixos para '{obj}' ({inst_nome})",
                options=eixos,
                key=f"eixo_{inst_id}_{obj}",
            )
            st.session_state["eixos_por_objetivo"][chave] = eixos_sel

    return st.session_state["eixos_por_objetivo"]


def render_acoes(eixos_por_objetivo):
    ui.element("h3", text="Ações de Manejo", key="hdr_acoes", className="mt-6")
    st.info("Selecione as ações correspondentes a cada eixo.")

    acoes_por_eixo = {}

    for (inst_id, inst_nome, obj), eixos in eixos_por_objetivo.items():
        for eixo in eixos:
            try:
                rows = obter_dados(
                    """
                    SELECT am.id, am.nome
                    FROM acao_manejo am
                    JOIN eixo_acao ea ON am.id = ea.acao_id
                    JOIN eixo_tematico et ON et.id = ea.eixo_id
                    WHERE et.nome = %s
                    """,
                    (eixo,),
                )
            except Exception as e:
                st.error(f"Erro ao buscar ações para '{eixo}': {e}")
                continue

            if not rows:
                st.warning(f"Sem ações para o eixo '{eixo}'.")
                continue

            acoes_dict = {r[0]: r[1] for r in rows}
            acoes_sel = st.multiselect(
                f"Ações para eixo '{eixo}' (objetivo '{obj}', {inst_nome})",
                options=list(acoes_dict.values()),
                key=f"acao_{inst_id}_{obj}_{eixo}",
            )
            acoes_por_eixo[(inst_id, inst_nome, obj, eixo)] = [
                {"id": k, "nome": v} for k, v in acoes_dict.items() if v in acoes_sel
            ]

    return acoes_por_eixo


def render_resumo(setor, inst_unid, obj_por_inst, eixos_por_obj, acoes_por_eixo):
    ui.element("h3", text="Resumo das Vinculações", key="hdr_res", className="mt-6")

    md = f"**Setor:** {setor}\n\n"
    for (inst_id, inst_nome), ucs in inst_unid.items():
        md += f"### Instrumento: {inst_nome}\n"
        md += f"**UC(s):** {', '.join(ucs) if ucs else 'Nenhuma'}\n"
        objetivos = obj_por_inst.get((inst_id, inst_nome), [])
        for obj in objetivos:
            md += f"- **Objetivo:** {obj}\n"
            eixos = eixos_por_obj.get((inst_id, inst_nome, obj), [])
            for eixo in eixos:
                md += f"    - **Eixo:** {eixo}\n"
                acoes = acoes_por_eixo.get((inst_id, inst_nome, obj, eixo), [])
                md += (
                    f"        - **Ações:** "
                    f"{', '.join(a['nome'] for a in acoes) or 'Nenhuma'}\n"
                )
        md += "\n---\n"

    st.markdown(md, unsafe_allow_html=True)


# ========================= fluxo principal ============================== #
def render():
    st.markdown(
        """
        <style>
          h3 { color: #2C3E50; margin-top: 1.2rem; }
          .stButton>button { background:#3498DB; color:white; border:none; }
          .stButton>button:hover { background:#2980B9; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Preencha as informações abaixo para registrar as associações. "
        "Siga as instruções cuidadosamente."
    )

    cpf, nome_usr, _ = render_identificacao()
    setor_escolhido = render_setor()
    inst_unid, desc_inst = render_instrumentos_unidades()
    obj_por_inst = render_objetivos(inst_unid)
    eixos_por_obj = render_eixos(obj_por_inst)
    acoes_por_eixo = render_acoes(eixos_por_obj)
    render_resumo(setor_escolhido, inst_unid, obj_por_inst, eixos_por_obj, acoes_por_eixo)

    # ---------- exportar ------------------------------------------------ #
    dados_export = coletar_dados_para_exportar(
        cpf,
        setor_escolhido,
        inst_unid,
        obj_por_inst,
        eixos_por_obj,
        acoes_por_eixo,
        desc_inst,
    )
    if dados_export:
        buffer = exportar_para_excel(dados_export)
        st.download_button(
            label="Exportar para Excel",
            data=buffer,
            file_name="relacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # ---------- salvar -------------------------------------------------- #
    if "dados_salvos" not in st.session_state:
        st.session_state["dados_salvos"] = False

    if not st.session_state["dados_salvos"]:
        if ui.button("💾 Salvar Dados", key="btn_salvar"):
            if validar_campos(
                cpf, setor_escolhido, inst_unid, obj_por_inst, eixos_por_obj
            ):
                acoes_conv = {
                    k: [a["id"] for a in v] for k, v in acoes_por_eixo.items()
                }
                salvar_vinculacoes(
                    cpf,
                    nome_usr,
                    setor_escolhido,
                    inst_unid,
                    obj_por_inst,
                    eixos_por_obj,
                    acoes_conv,
                    desc_inst,
                )
                st.session_state["dados_salvos"] = True
                st.success("Dados salvos com sucesso!")
                st.rerun()
            else:
                st.warning("Preencha todos os campos obrigatórios antes de salvar.")
    else:
        if ui.button("🔄 Preencher novamente?", key="btn_reiniciar"):
            for k in list(st.session_state.keys()):
                if k not in [
                    "cpf",
                    "user_registrado",
                    "setor_registrado",
                    "dados_salvos",
                ]:
                    del st.session_state[k]
            st.session_state["dados_salvos"] = False
            st.rerun()


if __name__ == "__main__":
    render()
