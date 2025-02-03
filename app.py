# app.py
import streamlit as st
from views import main_view

def main():
    st.set_page_config(page_title="Gestão de Manejo - ICMBio")
    main_view.render()  # Renderiza a interface principal

if __name__ == '__main__':
    main()
