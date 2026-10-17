from modules.database import get_connection

def listar_jogos():
    """Retorna todos os jogos cadastrados ordenados pelo nome."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, categoria, url_mapa FROM jogos ORDER BY nome ASC")
        return [dict(row) for row in cursor.fetchall()]

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
        cursor.execute("SELECT id, item_nome, concluido FROM checklist WHERE jogo_id = ? ORDER BY id ASC", (jogo_id,))
        return [dict(row) for row in cursor.fetchall()]

def adicionar_item_checklist(jogo_id, item_nome):
    """Adiciona um novo item ao checklist do jogo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO checklist (jogo_id, item_nome) VALUES (?, ?)", (jogo_id, item_nome))
        conn.commit()

def alternar_status_checklist(item_id, concluido):
    """Atualiza o estado de concluído de um item (1 ou 0)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE checklist SET concluido = ? WHERE id = ?", (1 if concluido else 0, item_id))
        conn.commit()

def remover_item_checklist(item_id):
    """Remove um item do checklist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM checklist WHERE id = ?", (item_id,))
        conn.commit()