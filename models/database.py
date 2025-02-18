import psycopg2
import streamlit as st
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def conectar_banco():
    """
    Conecta ao banco de dados PostgreSQL de forma segura usando variáveis de ambiente.
    """
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

@st.cache_data(ttl=600)  # Cache por 10 minutos
def obter_dados(query, params=None, single_column=False):
    """
    Executa uma consulta SQL e retorna os dados.
    - query: string com a consulta (ex.: "SELECT nome FROM tabela").
    - params: tupla ou lista de parâmetros para a consulta parametrizada.
    - single_column: se True, e a query tiver só 1 coluna, retorna lista de valores (strings/ints).
                     Caso contrário, retorna lista de tuplas.
    """
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute(query, params if params else ())
        dados = cur.fetchall()

        # Se pedimos para retornar só a primeira coluna (e de fato só há 1 coluna no SELECT):
        if single_column and cur.description and len(cur.description) == 1:
            dados = [row[0] for row in dados]

        cur.close()
        conn.close()
        return dados

    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return []
