# models/database.py
import psycopg2
import streamlit as st
from datetime import datetime

def conectar_banco():
    """Conecta ao banco de dados PostgreSQL."""
    return psycopg2.connect(
        dbname="db_samge_hmg",
        user="samge_read",
        password="samge_read",
        host="162.243.243.165",
        port="5432"
    )

@st.cache_data(ttl=600)  # Cache por 10 minutos
def obter_dados(query, params=None):
    """Busca dados no banco com cache."""
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute(query, params if params else ())
        dados = cur.fetchall()
        cur.close()
        conn.close()
        return [d[0] for d in dados]
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return []
