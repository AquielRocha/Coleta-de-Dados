import streamlit as st

def validar_campos(usuario, setor_escolhido, instrumentos_unidades, objetivos_por_instrumento, eixos_por_objetivo):
    """Valida se os campos obrigatórios foram preenchidos."""
    if not usuario.strip():
        st.error("O campo de usuário está vazio.")
        return False
    if not setor_escolhido:
        st.error("Nenhum setor selecionado.")
        return False
    if not instrumentos_unidades:
        st.error("Nenhum instrumento foi selecionado.")
        return False
    for instrumento, ucs in instrumentos_unidades.items():
        if not ucs:
            st.error(f"Não há Unidade(s) de Conservação selecionada(s) para o instrumento '{instrumento[1]}'.")
            return False
        chave_inst = (instrumento[0], instrumento[1])
        objetivos = objetivos_por_instrumento.get(chave_inst, [])
        if not objetivos:
            st.error(f"Não há objetivos adicionados para o instrumento '{instrumento[1]}'.")
            return False
        for objetivo in objetivos:
            chave_obj = (instrumento[0], instrumento[1], objetivo)
            eixos = eixos_por_objetivo.get(chave_obj, [])
            if not eixos:
                st.error(f"Não há eixos temáticos selecionados para o objetivo '{objetivo}' no instrumento '{instrumento[1]}'.")
                return False
    return True
