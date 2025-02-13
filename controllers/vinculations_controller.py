from datetime import datetime
from models.database import conectar_banco
import streamlit as st

def get_id(cur, table, column, value):
    """
    Função auxiliar para buscar o ID de um registro em uma tabela a partir de um valor.
    """
    cur.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
    result = cur.fetchone()
    return result[0] if result else None

def salvar_usuario(cpf, nome, setor):
    """
    Insere um novo usuário na tabela 'usuarios', se ele ainda não existir.
    """
    try:
        conn = conectar_banco()
        cur = conn.cursor()

        # Verificar se o usuário já existe
        cur.execute("SELECT id FROM usuarios WHERE cpf = %s", (cpf,))
        usuario_existente = cur.fetchone()

        if not usuario_existente:
            # Obter o ID do setor escolhido
            setor_id = get_id(cur, 'setor', 'nome', setor)
            if not setor_id:
                st.error("Setor não encontrado no banco de dados.")
                cur.close()
                conn.close()
                return
            
            # Inserir novo usuário
            cur.execute(
                """
                INSERT INTO usuarios (cpf, nome, setor_id)
                VALUES (%s, %s, %s)
                """,
                (cpf, nome, setor_id)
            )
            conn.commit()
            st.success(f"Usuário {nome} cadastrado com sucesso!")

        cur.close()
        conn.close()

    except Exception as e:
        st.error(f"Erro ao salvar usuário: {e}")

def salvar_vinculacoes(
    cpf, nome_usuario, setor_escolhido, instrumentos_unidades, 
    objetivos_por_instrumento, eixos_por_objetivo, acoes_por_eixo, descricao_instrumento
):
    try:
        conn = conectar_banco()
        cur = conn.cursor()

        # Garantir que o usuário esteja cadastrado
        salvar_usuario(cpf, nome_usuario, setor_escolhido)

        # Obter usuário e setor
        cur.execute("SELECT id FROM usuarios WHERE cpf = %s", (cpf,))
        usuario_rec = cur.fetchone()
        if not usuario_rec:
            st.error("Usuário não encontrado após cadastro.")
            cur.close()
            conn.close()
            return
        usuario_id = usuario_rec[0]
        
        setor_id = get_id(cur, 'setor', 'nome', setor_escolhido)
        if not setor_id:
            st.error("Setor não encontrado no banco de dados.")
            cur.close()
            conn.close()
            return

        # Iterar sobre cada instrumento e suas UC(s)
        for instrumento, ucs in instrumentos_unidades.items():
            instrumento_id = get_id(cur, 'instrumento', 'nome', instrumento[1])
            if not instrumento_id:
                st.error(f"Instrumento '{instrumento[1]}' não encontrado.")
                continue

            # Recupera a descrição específica para esse instrumento
            descricao = descricao_instrumento.get(instrumento, None)

            chave_inst = (instrumento[0], instrumento[1])
            objetivos = objetivos_por_instrumento.get(chave_inst, [])
            if not objetivos:
                st.warning(f"Sem objetivos cadastrados para o instrumento '{instrumento[1]}'.")
                continue

            for uc in ucs:
                unidade_id = get_id(cur, 'unidade_conservacao', 'nome', uc)
                if not unidade_id:
                    st.error(f"Unidade de Conservação '{uc}' não encontrada.")
                    continue

                for objetivo in objetivos:
                    objetivo_id = get_id(cur, 'objetivo_especifico', 'descricao', objetivo)
                    if not objetivo_id:
                        cur.execute(
                            "INSERT INTO objetivo_especifico (descricao) VALUES (%s) RETURNING id",
                            (objetivo,)
                        )
                        objetivo_id = cur.fetchone()[0]
                        conn.commit()

                    chave_obj = (instrumento[0], instrumento[1], objetivo)
                    eixos = eixos_por_objetivo.get(chave_obj, [])
                    if not eixos:
                        st.warning(f"Sem eixos temáticos para o objetivo '{objetivo}' no instrumento '{instrumento[1]}'.")
                        continue

                    for eixo in eixos:
                        eixo_id = get_id(cur, 'eixo_tematico', 'nome', eixo) if eixo and eixo != 'Nenhuma' else None

                        chave_acao = (instrumento[0], instrumento[1], objetivo, eixo)
                        acoes = acoes_por_eixo.get(chave_acao, [])
                        if acoes:
                            for acao in acoes:
                                # acao já é o ID
                                acao_id = acao
                                cur.execute(
                                    """
                                    INSERT INTO relacionamentos_coleta
                                    (usuario_id, setor_id, unidade_id, instrumento_id, descricao_instrumento, 
                                     objetivo_id, eixo_tematico_id, acao_manejo_id, preenchido_em)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """,
                                    (
                                        usuario_id,
                                        setor_id,
                                        unidade_id,
                                        instrumento_id,
                                        descricao,  # novo campo com a descrição
                                        objetivo_id,
                                        eixo_id,
                                        acao_id,
                                        datetime.now(),
                                    ),
                                )
                        else:
                            cur.execute(
                                """
                                INSERT INTO relacionamentos_coleta
                                (usuario_id, setor_id, unidade_id, instrumento_id, descricao_instrumento, 
                                 objetivo_id, eixo_tematico_id, acao_manejo_id, preenchido_em)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    usuario_id,
                                    setor_id,
                                    unidade_id,
                                    instrumento_id,
                                    descricao,
                                    objetivo_id,
                                    eixo_id,
                                    None,
                                    datetime.now(),
                                ),
                            )
        conn.commit()
        cur.close()
        conn.close()
        st.success("Dados de vinculação salvos com sucesso!")

    except Exception as e:
        st.error(f"Erro ao salvar os dados: {e}")

def coletar_dados_para_exportar(usuario, setor_escolhido, instrumentos_unidades, 
                                objetivos_por_instrumento, eixos_por_objetivo, acoes_por_eixo, descricao_instrumento):
    dados = []
    for instrumento, ucs in instrumentos_unidades.items():
        inst_id, inst_nome = instrumento
        # Obter a descrição específica para este instrumento
        desc = descricao_instrumento.get(instrumento, "")
        # Obter os objetivos para este instrumento
        chave_inst = (inst_id, inst_nome)
        objetivos = objetivos_por_instrumento.get(chave_inst, [])
        for uc in ucs:
            for objetivo in objetivos:
                chave_obj = (inst_id, inst_nome, objetivo)
                eixos = eixos_por_objetivo.get(chave_obj, [])
                for eixo in eixos:
                    chave_acao = (inst_id, inst_nome, objetivo, eixo)
                    acoes = acoes_por_eixo.get(chave_acao, [])
                    if acoes:
                        for acao in acoes:
                            # Verifica se 'acao' é um dicionário com a chave 'nome'
                            acao_nome = acao['nome'] if isinstance(acao, dict) and 'nome' in acao else acao
                            dados.append([
                                setor_escolhido,
                                uc,
                                desc,         # Descrição do instrumento
                                inst_nome,
                                objetivo,
                                eixo,
                                acao_nome,    # Ação de Manejo: exibe o nome
                                usuario,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            ])
                    else:
                        dados.append([
                            setor_escolhido,
                            uc,
                            desc,         # Descrição do instrumento
                            inst_nome,
                            objetivo,
                            eixo,
                            'Nenhuma',
                            usuario,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ])
    return dados

def listar_vinculacoes(cpf=None):
    """
    Retorna todas as vinculações cadastradas para um usuário filtrando pelo setor ao qual ele pertence.
    Se o parâmetro cpf for informado, retorna somente os registros relacionados ao setor do usuário.
    """
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        
        # Buscar o setor do usuário pelo CPF
        cur.execute("""
            SELECT s.nome FROM usuarios u
            JOIN setor s ON u.setor_id = s.id
            WHERE u.cpf = %s
        """, (cpf,))
        setor_usuario = cur.fetchone()

        if not setor_usuario:
            st.warning("Usuário não encontrado ou não associado a um setor.")
            cur.close()
            conn.close()
            return []

        setor_usuario = setor_usuario[0]

        # Note que aqui, em vez de u.cpf, usamos u.nome para exibir o nome do usuário.
        cur.execute("""
            SELECT rc.id, u.nome AS nome, s.nome AS setor, uc.nome AS unidade, i.nome AS instrumento, 
                   oe.descricao AS objetivo, et.nome AS eixo_tematico, am.nome AS acao_manejo, 
                   rc.preenchido_em, rc.descricao_instrumento AS descricao_instrumento
            FROM relacionamentos_coleta rc
            JOIN usuarios u ON rc.usuario_id = u.id
            JOIN setor s ON rc.setor_id = s.id
            JOIN unidade_conservacao uc ON rc.unidade_id = uc.id
            JOIN instrumento i ON rc.instrumento_id = i.id
            JOIN objetivo_especifico oe ON rc.objetivo_id = oe.id
            LEFT JOIN eixo_tematico et ON rc.eixo_tematico_id = et.id
            LEFT JOIN acao_manejo am ON rc.acao_manejo_id = am.id
            WHERE s.nome = %s
            ORDER BY rc.id
        """, (setor_usuario,))

        records = cur.fetchall()
        cur.close()
        conn.close()
        return records

    except Exception as e:
        st.error(f"Erro ao listar as vinculações: {e}")
        return []

def obter_vinculacao_por_id(vinc_id):
    """
    Retorna os dados completos de uma vinculação específica, dado o ID.
    """
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute("""
            SELECT rc.id, u.cpf, s.nome AS setor, uc.nome AS unidade, i.nome AS instrumento, 
                   oe.descricao AS objetivo, et.nome AS eixo_tematico, am.nome AS acao_manejo, rc.preenchido_em
            FROM relacionamentos_coleta rc
            JOIN usuarios u ON rc.usuario_id = u.id
            JOIN setor s ON rc.setor_id = s.id
            JOIN unidade_conservacao uc ON rc.unidade_id = uc.id
            JOIN instrumento i ON rc.instrumento_id = i.id
            JOIN objetivo_especifico oe ON rc.objetivo_id = oe.id
            LEFT JOIN eixo_tematico et ON rc.eixo_tematico_id = et.id
            LEFT JOIN acao_manejo am ON rc.acao_manejo_id = am.id
            WHERE rc.id = %s
        """, (vinc_id,))
        record = cur.fetchone()
        cur.close()
        conn.close()
        return record
    except Exception as e:
        st.error(f"Erro ao obter a vinculação: {e}")
        return None

def editar_vinculacao(vinc_id, setor, unidade, instrumento, objetivo, eixo_tematico, acao_manejo, descricao_instrumento):
    try:
        conn = conectar_banco()
        cur = conn.cursor()

        setor_id = get_id(cur, 'setor', 'nome', setor)
        unidade_id = get_id(cur, 'unidade_conservacao', 'nome', unidade)
        instrumento_id = get_id(cur, 'instrumento', 'nome', instrumento)
     
        objetivo_id = get_id(cur, 'objetivo_especifico', 'descricao', objetivo)
        if not objetivo_id:
            cur.execute(
                "INSERT INTO objetivo_especifico (descricao) VALUES (%s) RETURNING id",
                (objetivo,)
            )
            objetivo_id = cur.fetchone()[0]
            conn.commit()
     
        eixo_id = get_id(cur, 'eixo_tematico', 'nome', eixo_tematico) if eixo_tematico and eixo_tematico != 'Nenhuma' else None
        acao_id = get_id(cur, 'acao_manejo', 'nome', acao_manejo) if acao_manejo and acao_manejo != 'Nenhuma' else None

        cur.execute(
            """
            UPDATE relacionamentos_coleta
            SET setor_id = %s, unidade_id = %s, instrumento_id = %s, descricao_instrumento = %s,
                objetivo_id = %s, eixo_tematico_id = %s, acao_manejo_id = %s, preenchido_em = %s
            WHERE id = %s
            """,
            (setor_id, unidade_id, instrumento_id, descricao_instrumento,
             objetivo_id, eixo_id, acao_id, datetime.now(), vinc_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        st.success("Dados atualizados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao atualizar a vinculação: {e}")

def deletar_vinculacao(vinc_id):
    """
    Deleta a vinculação com o ID especificado.
    """
    try:
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute("DELETE FROM relacionamentos_coleta WHERE id = %s", (vinc_id,))
        conn.commit()
        cur.close()
        conn.close()
        st.success("Vinculação deletada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao deletar a vinculação: {e}")
