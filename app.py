import streamlit as st
from views import crud_view, main_view

def main():
    st.set_page_config(page_title="Gestão de Manejo - ICMBio", layout="wide")
    
    # CSS customizado para padronização (definindo cores e fontes via variáveis)
    st.markdown(
        """
        <style>
            :root {
                --primary-color: #2C3E50;
                --secondary-color: #3498DB;
                --hover-color: #2980B9;
                --header-font: 'Arial', sans-serif;
                --body-font: 'Arial', sans-serif;
            }
            body {
                font-family: var(--body-font);
            }
            /* Estilo para o cabeçalho principal */
            .main-header {
                font-family: var(--header-font);
                font-size: 2.5em;
                color: var(--primary-color);
                text-align: center;
                margin-bottom: 1rem;
            }
            /* Estilo para a sidebar */
            [data-testid="stSidebar"] {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
            }
            [data-testid="stSidebar"] a {
                color: white;
            }
            /* Ajuste de cores dos títulos e textos */
            h1, h2, h3 {
                color: var(--primary-color);
            }
            /* Estilo para botões */
            .stButton button {
                background-color: var(--secondary-color);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.5em 1em;
            }
            .stButton button:hover {
                background-color: var(--hover-color);
            }
        </style>
        """, unsafe_allow_html=True
    )
    
    # Cabeçalho centralizado (utilizando o estilo definido no CSS)
    st.markdown("<h1 class='main-header'>Catálogo de Instrumentos e Objetivos - ICMBio</h1>", unsafe_allow_html=True)
    
    # Se desejar, você pode incluir um logo na sidebar
    # st.sidebar.image("logo.png", width=200)
    
    # Utilizando tabs para navegação
    tabs = st.tabs(["Consultar Catálogo dos Instrumentos", "Preencher novo formulário"])
    
    with tabs[0]:
        crud_view.render_crud_view()
    
    with tabs[1]:
        main_view.render()

if __name__ == '__main__':
    main()
