import streamlit as st
from views import crud_view, main_view

def main():
    st.set_page_config(page_title="Gestão de Manejo - ICMBio", layout="wide")
    
    # Esconder o cabeçalho do deploy
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # CSS modernizado
    st.markdown(
        """
        <style>
            :root {
                --primary-color: #1a73e8;
                --secondary-color: #7CB9E8;
                --accent-color: #F0F8FF;
                --text-color: #2c3e50;
                --header-font: 'Helvetica Neue', sans-serif;
                --body-font: 'Roboto', sans-serif;
            }
            
            body {
                font-family: var(--body-font);
                color: var(--text-color);
            }
            
            /* Cabeçalho principal */
            .main-header {
                font-family: var(--header-font);
                font-size: 2.2em;
                color: var(--primary-color);
                text-align: center;
                margin-bottom: 2rem;
                font-weight: 600;
            }
            
            /* Sidebar */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, var(--primary-color), var(--secondary-color));
                padding: 2rem 1rem;
            }
            
            /* Estilização dos selects */
            .stSelectbox div[data-baseweb="select"] {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            .stSelectbox div[data-baseweb="select"]:hover {
                border-color: var(--primary-color);
            }
            
            /* Botões */
            .stButton button {
                background-color: var(--primary-color);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.6em 1.2em;
                font-weight: 500;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .stButton button:hover {
                background-color: #f4f4f4;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                transform: translateY(-1px);
            }
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
                border-radius: 8px;
                padding: 0.5rem;
            }
            
            .stTabs [data-baseweb="tab"] {
                background-color: transparent;
                border-radius: 6px;
                color: var(--text-color);
                font-weight: 500;
            }
            
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
                background-color: white;
                color: var(--primary-color);
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            /* Inputs e text areas */
            .stTextInput input, .stTextArea textarea {
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 0.5rem;
            }
            
            .stTextInput input:focus, .stTextArea textarea:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 2px rgba(26,115,232,0.2);
            }
        </style>
        """, unsafe_allow_html=True
    )
    
    # Cabeçalho
    st.markdown("<h1 class='main-header'>Catálogo de Instrumentos e Objetivos - ICMBio</h1>", unsafe_allow_html=True)
    
    # Tabs
    tabs = st.tabs(["Consultar Catálogo dos Instrumentos", "Preencher novo formulário"])
    
    with tabs[0]:
        crud_view.render_crud_view()
    
    with tabs[1]:
        main_view.render()

if __name__ == '__main__':
    main()
