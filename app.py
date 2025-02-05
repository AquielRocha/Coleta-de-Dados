import streamlit as st
from views import crud_view, main_view

def main():
    st.set_page_config(page_title="Gestão de Manejo - ICMBio", layout="wide")
    
    # Injetando CSS customizado para melhorar a aparência

    
    st.markdown(
        """
        <style>
            /* Estilo para o cabeçalho principal */
            .main-header {
                font-family: 'Arial', sans-serif;
                font-size: 2.5em;
                color: #2C3E50;
                text-align: center;
                margin-bottom: 1rem;
            }
            /* Estilo para a sidebar */
            [data-testid="stSidebar"] {
                background: linear-gradient(135deg, #2C3E50, #3498DB);
                color: white;
            }
            [data-testid="stSidebar"] a {
                color: white;
            }
            /* Ajuste de cores dos títulos e textos */
            h1, h2, h3 {
                color: #2C3E50;
            }
            .stButton button {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.5em 1em;
            }
            .stButton button:hover {
                background-color: #2980B9;
            }
        </style>
        """, unsafe_allow_html=True
    )
    
    # Cabeçalho centralizado
    st.markdown("<h1 class='main-header' style='color:#E5EFE3;'>Gestão de Manejo - ICMBio</h1>", unsafe_allow_html=True)
    
    # Se desejar, você pode incluir um logo na sidebar
    # st.sidebar.image("logo.png", width=200)
    
    # Utilizando tabs para navegação
    tabs = st.tabs(["Consultar Gestão de Manejo", "Preencher novo formulário"])
    
    with tabs[0]:
        crud_view.render_crud_view()
    
    with tabs[1]:
        main_view.render()

if __name__ == '__main__':
    main()
