import shutil
from modules.database import get_connection, inserir_novo_jogo, get_db_path

def listar_jogos():
    """Retorna todos os jogos cadastrados ordenados pelo nome."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, categoria, url_mapa FROM jogos ORDER BY nome ASC")
        return [dict(row) for row in cursor.fetchall()]

def cadastrar_jogo(nome, url_mapa, categoria="Geral"):
    """Cadastra um novo jogo no banco."""
    inserir_novo_jogo(nome, url_mapa, categoria)

def exportar_backup_db(caminho_destino):
    """Copia o banco de dados atual para um destino escolhido pelo usuário."""
    db_atual = get_db_path()
    shutil.copy(db_atual, caminho_destino)

def importar_backup_db(caminho_origem):
    """Substitui o banco de dados atual por um arquivo de backup."""
    db_atual = get_db_path()
    shutil.copy(caminho_origem, db_atual)

def obter_anotacao(jogo_id):
    """Busca o texto de anotação do jogo informado."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT conteudo FROM anotacoes WHERE jogo_id = ?", (jogo_id,))
        row = cursor.fetchone()
        return row["conteudo"] if row else ""

def salvar_anotacao(jogo_id, conteudo):
    """Salva ou atualiza a anotação para o jogo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO anotacoes (jogo_id, conteudo)
            VALUES (?, ?)
            ON CONFLICT(jogo_id) DO UPDATE SET conteudo = excluded.conteudo
        """, (jogo_id, conteudo))
        conn.commit()

def listar_checklist(jogo_id):
    """Lista todos os itens de checklist do jogo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, item_nome, atual, total, concluido FROM checklist WHERE jogo_id = ? ORDER BY id ASC", (jogo_id,))
        return [dict(row) for row in cursor.fetchall()]

def adicionar_item_checklist(jogo_id, item_nome, total):
    """Adiciona um novo item ao checklist com valor inicial 0 e total definido."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO checklist (jogo_id, item_nome, atual, total, concluido) 
            VALUES (?, ?, 0, ?, 0)
        """, (jogo_id, item_nome, total))
        conn.commit()

def atualizar_contador_checklist(item_id, delta):
    """Incrementa ou decrementa o contador atual do item respeitando os limites [0, total]."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT atual, total FROM checklist WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            return
        
        novo_atual = max(0, min(row["total"], row["atual"] + delta))
        concluido = 1 if novo_atual >= row["total"] else 0
        
        cursor.execute("""
            UPDATE checklist 
            SET atual = ?, concluido = ? 
            WHERE id = ?
        """, (novo_atual, concluido, item_id))
        conn.commit()

def remover_item_checklist(item_id):
    """Remove um item do checklist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM checklist WHERE id = ?", (item_id,))
        conn.commit()