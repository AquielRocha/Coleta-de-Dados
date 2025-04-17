import streamlit as st
import streamlit_shadcn_ui as ui

# set_page_config TEM de ser a primeira instrução Streamlit
st.set_page_config(page_title="Gestão de Manejo - ICMBio", layout="wide")

from views import crud_view, main_view   # depois do set_page_config ✔


def main():
    # Remove menu/rodapé padrão
    st.markdown(
        """
        <style>
            #MainMenu { visibility: hidden; }
            header, footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Cabeçalho centralizado
    with ui.element("div", className="flex justify-center py-4", key="hdr_wrap"):
        ui.element(
            "h1",
            text="Catálogo de Instrumentos e Objetivos - ICMBio",
            className="text-3xl font-bold text-primary",
            key="hdr_title",
        )

    # Abas
    selected_tab = ui.tabs(
        options=[
            "Consultar Catálogo dos Instrumentos",
            "Preencher novo formulário",
        ],
        default_value="Consultar Catálogo dos Instrumentos",
        key="main_tabs",
    )

    st.divider()

    if selected_tab == "Consultar Catálogo dos Instrumentos":
        crud_view.render_crud_view()
    else:
        main_view.render()


if __name__ == "__main__":
    main()
