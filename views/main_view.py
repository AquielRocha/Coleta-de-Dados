import streamlit as st
from datetime import datetime

# Import das suas funções de banco e controladores
from models.database import conectar_banco, obter_dados
from controllers.vinculations_controller import salvar_vinculacoes, coletar_dados_para_exportar
from utils.export_utils import exportar_para_excel
from utils.validation import validar_campos

def update_usuario_setor(cpf, novo_setor):
    """
    Atualiza o setor do usuário no banco de dados.
    """
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute("SELECT id FROM setor WHERE nome = %s", (novo_setor,))
        setor_row = cur.fetchone()
        if setor_row:
            novo_setor_id = setor_row[0]
            cur.execute("UPDATE usuarios SET setor_id = %s WHERE cpf = %s", (novo_setor_id, cpf))
            conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao atualizar setor do usuário: {e}")

def render_identificacao():
    cpf = st.text_input(
        "Digite seu CPF:",
        max_chars=11,
        help="Digite somente os números do CPF, sem pontos ou traços.",
        key="cpf_input"
    ).strip()

    if not cpf:
        st.warning("Por favor, insira seu CPF para prosseguir.")
        st.stop()

    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute(
            "SELECT u.nome, s.nome FROM usuarios u JOIN setor s ON u.setor_id = s.id WHERE u.cpf = %s",
            (cpf,)
        )
        usuario = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao consultar o banco de dados: {e}")
        st.stop()

    if usuario:
        nome_usuario, setor = usuario
        st.session_state["user_registrado"] = True
        st.session_state["setor_registrado"] = setor
        st.session_state["cpf"] = cpf
        st.info(f"Bem-vindo de volta, {nome_usuario}!")
        st.text_input("Nome", value=nome_usuario, disabled=True, key="nome_usuario_input")
        st.text_input("Setor", value=setor, disabled=True, key="setor_usuario_input")
    else:
        st.session_state["user_registrado"] = False
        nome_usuario = st.text_input(
            "Digite seu Nome Completo:",
            help="Informe seu nome completo para o cadastro.",
            key="nome_usuario"
        ).strip()

        setores = obter_dados("SELECT DISTINCT nome FROM setor", single_column=True)
        setor = st.selectbox(
            "Selecione o Setor",
            setores,
            help="Escolha o setor onde a atividade ocorrerá.",
            key="setor_selectbox"
        )
        st.session_state["setor_registrado"] = setor

    return cpf, nome_usuario, st.session_state["setor_registrado"]

def render_setor():
    """
    Exibe o setor atual e possibilita a alteração se necessário.
    """
    setores = obter_dados("SELECT DISTINCT nome FROM setor", single_column=True)
    if st.session_state.get("user_registrado"):
        atual = st.session_state["setor_registrado"]
        st.info(f"Setor atual: {atual}.")
        deseja_mudar = st.checkbox("Desejo mudar de setor", key="mudar_setor")
        if deseja_mudar:
            setor_escolhido = st.selectbox(
                "Selecione o Novo Setor",
                setores,
                help="Escolha o novo setor. ATENÇÃO: Ao mudar de setor, você não poderá visualizar os dados do setor anterior.",
                key="setor_alterado"
            )
            if setor_escolhido != atual:
                st.warning(f"Ao mudar de setor, você não poderá visualizar os dados do setor {atual}. Atualizando seu setor...")
                cpf = st.session_state.get("cpf")
                update_usuario_setor(cpf, setor_escolhido)
                st.session_state["setor_registrado"] = setor_escolhido
        else:
            setor_escolhido = atual
    else:
        setor_escolhido = st.session_state.get("setor_registrado")
    return setor_escolhido

def render_instrumentos_unidades():
    """
    Permite a seleção de um ou mais instrumentos e, conforme a quantidade selecionada,
    exibe apenas UM campo para a escolha da Unidade de Conservação (UC), que será comum a todos os instrumentos.
    Se apenas um instrumento for selecionado e este for o PANs (ID 8), permite selecionar múltiplas UCs.
    """
    # Consulta a lista de instrumentos (cada registro é uma tupla: (id, nome))
    instrumentos = obter_dados("SELECT id, nome FROM instrumento")
    if not instrumentos:
        st.error("Nenhum instrumento encontrado.")
        st.stop()

    # Seleção múltipla de instrumentos
    instrumentos_selecionados = st.multiselect(
        "Selecione os Instrumentos",
        options=instrumentos,
        format_func=lambda x: x[1],
        key="instrumento_multiselect",
        help="Selecione um ou mais instrumentos conforme aplicável."
    )

    # Consulta as unidades de conservação
    unidades = obter_dados("SELECT DISTINCT nome FROM unidade_conservacao", single_column=True)

    instrumentos_unidades = {}
    if instrumentos_selecionados:
        if len(instrumentos_selecionados) == 1:
            # Se apenas um instrumento for selecionado
            instrumento = instrumentos_selecionados[0]
            if instrumento[0] == 8:
                # Caso PANs, permite selecionar várias UCs
                ucs = st.multiselect(
                    f"Selecione as Unidades de Conservação para o instrumento '{instrumento[1]}' (PANs)",
                    options=unidades,
                    key=f"uc_multiselect_{instrumento[0]}",
                    help="Mesmo que sejam várias, serão consideradas como uma única unidade."
                )
            else:
                uc = st.selectbox(
                    f"Selecione a Unidade de Conservação para o instrumento '{instrumento[1]}'",
                    options=unidades,
                    key=f"uc_selectbox_{instrumento[0]}",
                    help="Selecione uma UC."
                )
                ucs = [uc] if uc else []
            instrumentos_unidades[instrumento] = ucs
        elif len(instrumentos_selecionados) > 1:
            # Se mais de um instrumento for selecionado, exibe apenas um campo para UC
            uc = st.selectbox(
                "Selecione a Unidade de Conservação (única para todos os instrumentos)",
                options=unidades,
                key="uc_common_selectbox",
                help="A UC selecionada será aplicada a todos os instrumentos."
            )
            ucs = [uc] if uc else []
            for instrumento in instrumentos_selecionados:
                instrumentos_unidades[instrumento] = ucs
    return instrumentos_unidades

def render_objetivos(instrumentos_unidades):
    """
    Permite a inserção de objetivos específicos para cada instrumento selecionado.
    Mesmo que para o PANs várias UCs sejam selecionadas, os objetivos são vinculados unicamente ao instrumento.
    """
    if "objetivos_por_instrumento" not in st.session_state:
        st.session_state["objetivos_por_instrumento"] = {}

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:28px; color:#E6F0F3;'>Objetivos Específicos</h2>", unsafe_allow_html=True)

    for instrumento, ucs in instrumentos_unidades.items():
        chave_inst = (instrumento[0], instrumento[1])
        st.markdown(f"#### Instrumento: {instrumento[1]} (UC: {', '.join(ucs) if ucs else 'Nenhuma'})")
        if chave_inst not in st.session_state["objetivos_por_instrumento"]:
            st.session_state["objetivos_por_instrumento"][chave_inst] = []

        novo_objetivo = st.text_input(
            f"Digite um objetivo específico para '{instrumento[1]}':",
            key=f"novo_obj_{instrumento[0]}",
            help="Insira um objetivo específico para este instrumento."
        )
        if st.button(f"Adicionar Objetivo para '{instrumento[1]}'", key=f"add_obj_{instrumento[0]}"):
            if novo_objetivo.strip():
                if novo_objetivo.strip() not in st.session_state["objetivos_por_instrumento"][chave_inst]:
                    st.session_state["objetivos_por_instrumento"][chave_inst].append(novo_objetivo.strip())
                else:
                    st.warning("Este objetivo já foi adicionado.")
            else:
                st.warning("Por favor, insira um objetivo válido antes de adicionar.")

        if st.session_state["objetivos_por_instrumento"][chave_inst]:
            st.markdown("**Objetivos Adicionados:**", unsafe_allow_html=True)
            for idx, obj in enumerate(st.session_state["objetivos_por_instrumento"][chave_inst], 1):
                col1, col2 = st.columns([10, 1])
                with col1:
                    st.write(f"{idx}. {obj}")
                with col2:
                    if st.button("Remover", key=f"remove_obj_{instrumento[0]}_{idx}_button"):
                        st.session_state["objetivos_por_instrumento"][chave_inst].pop(idx - 1)
                        # Atualiza a interface após a remoção (se necessário)
    return st.session_state["objetivos_por_instrumento"]



def render_eixos(objetivos_por_instrumento):
    """
    Permite a seleção dos eixos temáticos para cada objetivo de cada instrumento.
    """
    eixos = obter_dados("SELECT nome FROM eixo_tematico", single_column=True)
    if "eixos_por_objetivo" not in st.session_state:
        st.session_state["eixos_por_objetivo"] = {}

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:24px; color:#E6F0F3;'>Eixos Temáticos</h3>", unsafe_allow_html=True)
    st.info("Selecione os eixos temáticos relacionados aos objetivos.")

    # Para cada instrumento e seus objetivos
    for chave_inst, objetivos in objetivos_por_instrumento.items():
        inst_id, inst_nome = chave_inst
        for objetivo in objetivos:
            chave_obj = (inst_id, inst_nome, objetivo)
            eixos_selecionados = st.multiselect(
                f"Selecione os eixos para o objetivo '{objetivo}' no instrumento '{inst_nome}':",
                options=eixos,
                key=f"eixo_{inst_id}_{objetivo}"
            )
            st.session_state["eixos_por_objetivo"][chave_obj] = eixos_selecionados

    return st.session_state["eixos_por_objetivo"]

def render_acoes(eixos_por_objetivo):
    """
    Permite a seleção das ações de manejo correspondentes a cada eixo temático.
    """
    acoes_por_eixo = {}
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size:20px; color:#E6F0F3;'>Ações de Manejo</h4>", unsafe_allow_html=True)
    st.info("Selecione as ações de manejo correspondentes aos eixos temáticos.")

    for (inst_id, inst_nome, objetivo), eixos in st.session_state["eixos_por_objetivo"].items():
        for eixo in eixos:
            st.write(f"Buscando ações para o eixo '{eixo}' (Objetivo: {objetivo}, Instrumento: {inst_nome})")
            try:
                acoes_relacionadas = obter_dados(
                    """
                    SELECT am.id, am.nome
                      FROM acao_manejo am
                      JOIN eixo_acao ea ON am.id = ea.acao_id
                      JOIN eixo_tematico et ON et.id = ea.eixo_id
                     WHERE et.nome = %s
                    """,
                    (eixo,)
                )
            except Exception as e:
                st.error(f"Ocorreu um erro na consulta ao eixo '{eixo}': {e}")
                st.stop()

            if not acoes_relacionadas:
                st.warning(f"Não foram encontradas ações de manejo para o eixo '{eixo}'.")
                continue

            # Verifica se o retorno possui o formato adequado: lista de tuplas (id, nome)
            formato_ok = (
                isinstance(acoes_relacionadas, list)
                and all(isinstance(acao, tuple) and len(acao) == 2 for acao in acoes_relacionadas)
            )
            if formato_ok:
                acoes_dict = {acao[0]: acao[1] for acao in acoes_relacionadas}
                acoes_selecionadas = st.multiselect(
                    f"Selecione as ações para o eixo '{eixo}' (Objetivo: {objetivo}, Instrumento: {inst_nome})",
                    options=list(acoes_dict.values()),
                    key=f"acao_{inst_id}_{objetivo}_{eixo}"
                )
                acoes_por_eixo[(inst_id, inst_nome, objetivo, eixo)] = [
                    key for key, value in acoes_dict.items() if value in acoes_selecionadas
                ]
            else:
                st.error(f"Formato inválido ao retornar as ações para o eixo '{eixo}'.")
                st.write(f"Retorno obtido: {acoes_relacionadas}")
                st.stop()

    return acoes_por_eixo

def render_resumo(setor_escolhido, instrumentos_unidades, objetivos_por_instrumento, eixos_por_objetivo, acoes_por_eixo):
    """
    Monta um resumo hierárquico das vinculações para visualização.
    """
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:24px; color:#E6F0F3;'>Resumo das Vinculações</h2>", unsafe_allow_html=True)

    resumo_md = f"**Setor Selecionado**: {setor_escolhido}\n\n"

    for instrumento, ucs in instrumentos_unidades.items():
        inst_id, inst_nome = instrumento
        resumo_md += f"**Instrumento**: {inst_nome}\n"
        resumo_md += f"**Unidade(s) de Conservação**: {', '.join(ucs) if ucs else 'Nenhuma'}\n"
        chave_inst = (inst_id, inst_nome)
        objetivos = objetivos_por_instrumento.get(chave_inst, [])
        if objetivos:
            for obj in objetivos:
                resumo_md += f"- **Objetivo**: {obj}\n"
                chave_obj = (inst_id, inst_nome, obj)
                eixos = eixos_por_objetivo.get(chave_obj, [])
                if eixos:
                    for eixo in eixos:
                        resumo_md += f"  - **Eixo Temático**: {eixo}\n"
                        acoes = acoes_por_eixo.get((inst_id, inst_nome, obj, eixo), [])
                        if acoes:
                            # Realiza um join utilizando o nome da ação, se disponível
                            acoes_nomes = ", ".join(
                                [acao['nome'] if isinstance(acao, dict) and 'nome' in acao else str(acao)
                                 for acao in acoes]
                            )
                            resumo_md += f"      - **Ações de Manejo**: {acoes_nomes}\n"
                        else:
                            resumo_md += "      - **Ações de Manejo**: Nenhuma\n"
                else:
                    resumo_md += "  - **Eixos Temáticos**: Nenhum\n"
        else:
            resumo_md += "Nenhum objetivo adicionado.\n"
        # Separador para visualização mais clara de cada instrumento
        resumo_md += "\n---\n\n"

    st.markdown(resumo_md, unsafe_allow_html=True)

def render():
    st.markdown("<h1 style='color:#E5EFE3;'>Gestão de Manejo - ICMBio</h1>", unsafe_allow_html=True)
    st.info("Preencha as informações abaixo para registrar as vinculações de manejo. Por favor, siga as instruções cuidadosamente.")

    # 1) Identificação
    cpf, nome_usuario, setor_inicial = render_identificacao()

    # 2) Setor (com opção de alteração)
    setor_escolhido = render_setor()

    # 3) Seleção de Instrumentos e respectiva Unidade de Conservação
    instrumentos_unidades = render_instrumentos_unidades()

    # 4) Objetivos específicos para cada instrumento
    objetivos_por_instrumento = render_objetivos(instrumentos_unidades)

    # 5) Seleção dos eixos temáticos para cada objetivo
    eixos_por_objetivo = render_eixos(objetivos_por_instrumento)

    # 6) Seleção das ações de manejo para cada eixo temático
    acoes_por_eixo = render_acoes(eixos_por_objetivo)

    # 7) Resumo das vinculações
    render_resumo(
        setor_escolhido,
        instrumentos_unidades,
        objetivos_por_instrumento,
        eixos_por_objetivo,
        acoes_por_eixo
    )

    # 8) Exportação para Excel (se houver dados)
    dados_para_exportar = coletar_dados_para_exportar(
        cpf,
        setor_escolhido,
        instrumentos_unidades,
        objetivos_por_instrumento,
        eixos_por_objetivo,
        acoes_por_eixo
    )
    if dados_para_exportar:
        excel_buffer = exportar_para_excel(dados_para_exportar)
        st.download_button(
            label="Exportar Dados para Excel",
            data=excel_buffer,
            file_name="relacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Clique para baixar um arquivo Excel com os dados preenchidos."
        )

    # 9) Botão Salvar (com validação)
    if st.button("Salvar Dados"):
        if validar_campos(
            cpf,
            setor_escolhido,
            instrumentos_unidades,
            objetivos_por_instrumento,
            eixos_por_objetivo
        ):
            salvar_vinculacoes(
                cpf,
                nome_usuario,
                setor_escolhido,
                instrumentos_unidades,
                objetivos_por_instrumento,
                eixos_por_objetivo,
                acoes_por_eixo
            )
        else:
            st.warning("Por favor, preencha todos os campos obrigatórios antes de salvar.")

if __name__ == "__main__":
    render()
