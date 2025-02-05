import psycopg2
import streamlit as st

def conectar_banco():
    """
    Conecta ao banco de dados PostgreSQL.
    Ajuste os parâmetros conforme suas credenciais.
    """
    return psycopg2.connect(
        dbname="db_samge_hmg",
        user="samge_read",
        password="samge_read",
        host="162.243.243.165",
        port="5432"
    )

@st.cache_data(ttl=600)  # Cache por 10 minutos
def obter_dados(query, params=None, single_column=False):
    """
    Executa uma consulta SQL e retorna os dados.
    - query: string com a consulta (ex.: "SELECT nome FROM tabela").
    - params: tupla ou lista de parâmetros para a consulta parametrizada.
    - single_column: se True, e a query tiver só 1 coluna, retorna lista de valores (strings/ints).
                     caso contrário, retorna lista de tuplas.
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
