import streamlit as st
from datetime import datetime
from models.database import conectar_banco, obter_dados
from controllers.vinculations_controller import salvar_vinculacoes, coletar_dados_para_exportar
from utils.export_utils import exportar_para_excel
from utils.validation import validar_campos

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

    # Tenta buscar o usuário no banco pelo CPF
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
        # Usuário já cadastrado: nome e setor são automaticamente preenchidos
        nome_usuario, setor = usuario
        st.info(f"Bem-vindo de volta, {nome_usuario}! ")
        st.text_input("Nome", value=nome_usuario, disabled=True, key="nome_usuario_input")
        st.text_input("Setor", value=setor, disabled=True, key="setor_usuario_input")
    else:
        # Usuário não cadastrado: solicitar os dados
        nome_usuario = st.text_input(
            "Digite seu Nome Completo:",
            help="Informe seu nome completo para o cadastro.",
            key="nome_usuario"
        ).strip()
        # Recupera as opções de setor para cadastro
        setores = obter_dados("SELECT DISTINCT nome FROM setor")
        setor = st.selectbox(
            "Selecione o Setor", 
            setores, 
            help="Escolha o setor onde a atividade ocorrerá.",
            key="setor_selectbox"
        )

    return cpf, nome_usuario, setor

def render_setor_unidade():
    setores = obter_dados("SELECT DISTINCT nome FROM setor")
    setor_escolhido = st.selectbox(
        "Selecione o Setor",
        setores,
        help="Escolha o setor onde a atividade ocorrerá.",
        key="setor_unidade_selectbox"
    )

    unidades = obter_dados("SELECT DISTINCT nome FROM unidade_conservacao")
    unidade_selecionada = st.selectbox(
        "Selecione a Unidade de Conservação",
        unidades,
        help="Selecione a unidade relacionada à atividade.",
        key="unidade_conservacao_selectbox"
    )
    return setor_escolhido, unidade_selecionada

def render_instrumentos(unidade_selecionada):
    instrumentos_por_unidade = {}
    instrumentos = obter_dados("SELECT DISTINCT nome FROM instrumento")
    if unidade_selecionada:
        instrumentos_escolhidos = st.multiselect(
            f"Selecione os Instrumentos para '{unidade_selecionada}'",
            instrumentos,
            key=f"inst_{unidade_selecionada}_multiselect",
            help="Selecione um ou mais instrumentos conforme aplicável."
        )
        instrumentos_por_unidade[unidade_selecionada] = instrumentos_escolhidos
    return instrumentos_por_unidade

def render_objetivos(instrumentos_por_unidade):
    # Inicializa as variáveis de sessão, se necessário
    if "objetivos_por_instrumento" not in st.session_state:
        st.session_state["objetivos_por_instrumento"] = {}
    if "objetivos_inputs" not in st.session_state:
        st.session_state["objetivos_inputs"] = {}

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:28px; color:#E6F0F3;'>Objetivos Específicos</h2>", unsafe_allow_html=True)
    st.info("Para cada instrumento selecionado, digite os objetivos específicos detalhados. Exemplo: 'Melhorar a eficiência do monitoramento'.")

    for unidade, instrumentos_list in instrumentos_por_unidade.items():
        for instrumento in instrumentos_list:
            chave = (unidade, instrumento)
            if chave not in st.session_state["objetivos_por_instrumento"]:
                st.session_state["objetivos_por_instrumento"][chave] = []
            if chave not in st.session_state["objetivos_inputs"]:
                st.session_state["objetivos_inputs"][chave] = ""

            st.write(f"#### Instrumento: '{instrumento}' na Unidade: '{unidade}'")
            col1, col2 = st.columns([3, 1])
            with col1:
                novo_objetivo = st.text_input(
                    "Digite um objetivo específico:",
                    key=f"novo_obj_{unidade}_{instrumento}_input",
                    help="Insira um objetivo específico para este instrumento."
                )
            with col2:
                if st.button("Adicionar", key=f"add_obj_{unidade}_{instrumento}_button"):
                    if novo_objetivo.strip():
                        if novo_objetivo.strip() not in st.session_state["objetivos_por_instrumento"][chave]:
                            st.session_state["objetivos_por_instrumento"][chave].append(novo_objetivo.strip())
                        else:
                            st.warning("Este objetivo já foi adicionado.")
                    else:
                        st.warning("Por favor, insira um objetivo válido antes de adicionar.")

            objetivos_atualizados = st.session_state["objetivos_por_instrumento"][chave]
            if objetivos_atualizados:
                st.markdown("<b>Objetivos Adicionados:</b>", unsafe_allow_html=True)
                for idx, obj in enumerate(objetivos_atualizados, 1):
                    col3, col4 = st.columns([10, 1])
                    with col3:
                        st.write(f"{idx}. {obj}")
                    with col4:
                        if st.button("Remover", key=f"remove_obj_{unidade}_{instrumento}_{idx}_button"):
                            st.session_state["objetivos_por_instrumento"][chave].pop(idx - 1)
                            st.experimental_rerun()

    return st.session_state["objetivos_por_instrumento"]

def render_eixos(objetivos_por_instrumento):
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:24px; color:#E6F0F3;'>Eixos Temáticos</h3>", unsafe_allow_html=True)
    st.info("Selecione os eixos temáticos relacionados aos objetivos específicos acima.")
    eixos_por_objetivo = {}
    eixos = obter_dados("SELECT nome FROM eixo_tematico")
    if objetivos_por_instrumento:
        for (unidade, instrumento), objetivos in objetivos_por_instrumento.items():
            for objetivo in objetivos:
                eixos_selecionados = st.multiselect(
                    f"Selecione os eixos para o objetivo: '{objetivo}' no instrumento: '{instrumento}'",
                    eixos,
                    key=f"eixo_{unidade}_{instrumento}_{objetivo}_multiselect",
                    help="Selecione os eixos temáticos que se aplicam a este objetivo."
                )
                eixos_por_objetivo[(unidade, instrumento, objetivo)] = eixos_selecionados
    return eixos_por_objetivo

def render_acoes(eixos_por_objetivo):
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size:20px; color:#E6F0F3;'>Ações de Manejo</h4>", unsafe_allow_html=True)
    st.info("Selecione as ações de manejo correspondentes a cada eixo temático.")
    acoes_por_eixo = {}
    acoes = obter_dados("SELECT nome FROM acao_manejo")
    if eixos_por_objetivo:
        for (unidade, instrumento, objetivo), eixos in eixos_por_objetivo.items():
            for eixo in eixos:
                acoes_selecionadas = st.multiselect(
                    f"Selecione as ações para o eixo: '{eixo}' (Objetivo: {objetivo})",
                    acoes,
                    key=f"acao_{unidade}_{instrumento}_{objetivo}_{eixo}_multiselect",
                    help="Selecione as ações de manejo que se aplicam a este eixo temático."
                )
                acoes_por_eixo[(unidade, instrumento, objetivo, eixo)] = acoes_selecionadas
    return acoes_por_eixo

def render_resumo(setor_escolhido, unidade_selecionada, instrumentos_por_unidade,
                  objetivos_por_instrumento, eixos_por_objetivo, acoes_por_eixo):
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:24px; color:#E6F0F3;'>Resumo das Vinculações</h2>", unsafe_allow_html=True)
    st.write(f"<b>Setor Selecionado:</b> {setor_escolhido}", unsafe_allow_html=True)
    st.write(f"<b>Unidade de Conservação:</b> {unidade_selecionada}", unsafe_allow_html=True)
    for unidade in instrumentos_por_unidade:
        for instrumento in instrumentos_por_unidade.get(unidade, []):
            st.write(f"<b>Instrumento:</b> {instrumento}", unsafe_allow_html=True)
            objetivos = objetivos_por_instrumento.get((unidade, instrumento), [])
            for objetivo in objetivos:
                st.write(f" - <b>Objetivo:</b> {objetivo}", unsafe_allow_html=True)
                eixos = eixos_por_objetivo.get((unidade, instrumento, objetivo), [])
                for eixo in eixos:
                    st.write(f"   - <b>Eixo Temático:</b> {eixo}", unsafe_allow_html=True)
                    acoes = acoes_por_eixo.get((unidade, instrumento, objetivo, eixo), [])
                    st.write(
                        f"     - <b>Ações de Manejo:</b> {', '.join(acoes) if acoes else 'Nenhuma'}",
                        unsafe_allow_html=True
                    )

def render():
    st.markdown("<h1 style='color:#E5EFE3;'>Gestão de Manejo - ICMBio</h1>", unsafe_allow_html=True)
    st.info("Preencha as informações abaixo para registrar as vinculações de manejo. Por favor, siga as instruções cuidadosamente.")

    # Identificação do usuário
    cpf, nome_usuario, setor = render_identificacao()

    # Seleção de Setor e Unidade de Conservação
    setor_escolhido, unidade_selecionada = render_setor_unidade()

    # Seleção de Instrumentos
    instrumentos_por_unidade = render_instrumentos(unidade_selecionada)

    # Preenchimento dos Objetivos Específicos
    objetivos_por_instrumento = render_objetivos(instrumentos_por_unidade)

    # Seleção dos Eixos Temáticos
    eixos_por_objetivo = render_eixos(objetivos_por_instrumento)

    # Seleção das Ações de Manejo
    acoes_por_eixo = render_acoes(eixos_por_objetivo)

    # Exibição do resumo das informações preenchidas
    render_resumo(setor_escolhido, unidade_selecionada, instrumentos_por_unidade,
                  objetivos_por_instrumento, eixos_por_objetivo, acoes_por_eixo)

    # Preparar dados para exportação
    dados_para_exportar = coletar_dados_para_exportar(
        cpf,
        setor_escolhido,
        instrumentos_por_unidade,
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

    # Botão para salvar os dados, com validação dos campos obrigatórios
    if st.button("Salvar Dados"):
        if validar_campos(
            cpf,
            setor_escolhido,
            unidade_selecionada,
            instrumentos_por_unidade,
            objetivos_por_instrumento,
            eixos_por_objetivo
        ):
            salvar_vinculacoes(
                cpf,
                nome_usuario,
                setor_escolhido,
                instrumentos_por_unidade,
                objetivos_por_instrumento,
                eixos_por_eixo
            )
        else:
            st.warning("Por favor, preencha todos os campos obrigatórios antes de salvar.")