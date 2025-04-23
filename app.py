import streamlit as st
from views import crud_view, main_view

# ---------- NOVA PALETA & VARS ----------
CSS = """
<style>
:root{
    --primary:      #006d77;
    --primary-dark: #004f55;
    --secondary:    #83c5be;
    --bg-light:     #f9fbfc;
    --bg-card:      rgba(255,255,255,0.75);    /* glass effect */
    --text-default: #233142;
    --radius:       10px;
    --shadow:       0 4px 16px rgba(0,0,0,0.06);
    --blur:         12px;
    --font-title:   "Poppins", sans-serif;
    --font-body:    "Inter",   sans-serif;
}
/* RESET corpo --------------------------------------------------*/
html, body            {background:var(--bg-light);}
body                  {font-family:var(--font-body);color:var(--text-default);}

/* HEADER -------------------------------------------------------*/
.main-header{
    font-family:var(--font-title);
    font-size:clamp(1.8rem,4vw,2.6rem);
    font-weight:600;
    color:var(--primary);
    text-align:center;
    margin:1.5rem 0 2rem;
}

/* SIDEBAR (degrade + blur) ------------------------------------*/
[data-testid="stSidebar"]{
    background: linear-gradient(180deg,var(--primary),var(--secondary));
    color:white;
    backdrop-filter: blur(var(--blur));
}
[data-testid="stSidebar"] * {color:white;}

/* CARDS (qualquer container sozinho) ---------------------------*/
section, .stTabs [data-baseweb="tab"]{
    background:var(--bg-card);
    backdrop-filter: blur(var(--blur));
    border-radius:var(--radius);
    box-shadow:var(--shadow);
    padding:1rem;
}

/* TABS ---------------------------------------------------------*/
.stTabs [data-baseweb="tab-list"]{
    gap:.5rem;
}
.stTabs [data-baseweb="tab"]{
    font-weight:500;
    border:none!important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"]{
    background:var(--primary);
    color:#fff;
}

/* CAMPOS INPUT -------------------------------------------------*/
input, textarea, select{
    border-radius:var(--radius)!important;
    border:1px solid #d8e1e8!important;
    padding:.55rem .75rem!important;
    transition:border .2s, box-shadow .2s;
}
input:focus, textarea:focus, select:focus{
    border:1px solid var(--primary)!important;
    box-shadow:0 0 0 2px rgba(0,109,119,.15)!important;
}

/* BOTÕES -------------------------------------------------------*/
.stButton>button{
    background:var(--primary);
    border:none;
    color:#fff;
    font-weight:600;
    padding:.6rem 1.2rem;
    border-radius:var(--radius);
    box-shadow:var(--shadow);
    transition:background .25s, transform .15s;
}
.stButton>button:hover{background:var(--primary-dark); transform:translateY(-2px);}
.stButton>button:active{transform:translateY(0);}

/* CHECKBOX / RADIO --------------------------------------------*/
input[type="checkbox"]:checked+div>svg>path{fill:var(--primary)!important;}
input[type="radio"]:checked+div>svg>circle{fill:var(--primary)!important;}
</style>
"""

def main():
    st.set_page_config(page_title="Gestão de Manejo - ICMBio", layout="wide")

    # Oculta barra padrão do Streamlit Cloud
    st.markdown(
        """
        <style>#MainMenu{visibility:hidden;}header{visibility:hidden;}footer{visibility:hidden;}</style>
        """,
        unsafe_allow_html=True,
    )

    # Aplica o novo tema
    st.markdown(CSS, unsafe_allow_html=True)

    # ---------- CONTEÚDO ----------
    st.markdown("<h1 class='main-header'>Catálogo de Instrumentos e Objetivos&nbsp;-&nbsp;ICMBio</h1>",
                unsafe_allow_html=True)

    aba_consulta, aba_novo = st.tabs(
        ["📄 Consultar catálogo", "📝 Novo formulário"])

    with aba_consulta:
        crud_view.render_crud_view()

    with aba_novo:
        main_view.render()

if __name__ == "__main__":
    main()
