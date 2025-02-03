# utils/validation.py
import streamlit as st

def validar_campos(usuario, setor_escolhido, unidades_selecionadas, instrumentos_por_unidade, objetivos_por_instrumento, eixos_por_objetivo):
    """Valida se os campos obrigatórios foram preenchidos."""
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
            objetivos = objetivos_por_instrumento.get((unidade, instrumento), [])
            if not objetivos:
                st.error(f"Não há objetivos adicionados para o instrumento '{instrumento}' na unidade '{unidade}'.")
                return False
            for objetivo in objetivos:
                eixos = eixos_por_objetivo.get((unidade, instrumento, objetivo), [])
                if not eixos:
                    st.error(f"Não há eixos temáticos selecionados para o objetivo '{objetivo}' no instrumento '{instrumento}' na unidade '{unidade}'.")
                    return False
    return True
