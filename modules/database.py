import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "gamer_hub.db")

def get_connection():
    """Retorna a conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa a estrutura do banco de dados e popula com os jogos iniciais."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela de Jogos e seus Links principais
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jogos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                categoria TEXT DEFAULT 'Geral',
                url_mapa TEXT NOT NULL
            )
        """)
        
        # Tabela de Anotações por Jogo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anotacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jogo_id INTEGER UNIQUE,
                conteudo TEXT DEFAULT '',
                FOREIGN KEY (jogo_id) REFERENCES jogos (id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de Checklist de Progresso
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jogo_id INTEGER NOT NULL,
                item_nome TEXT NOT NULL,
                concluido INTEGER DEFAULT 0,
                FOREIGN KEY (jogo_id) REFERENCES jogos (id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
    
    # Insere os links pré-cadastrados
    _popular_jogos_iniciais()

def _popular_jogos_iniciais():
    jogos_iniciais = [
        ("GTA 5 (Modo Campanha)", "Mundo Aberto", "https://mapgenie.io/gta5"),
        ("GTA 5 Online", "Mundo Aberto", "https://gtaweb.eu/gtao-map"),
        ("Red Dead Redemption 2", "Mundo Aberto", "https://www.shackmaps.com/red-dead-redemption-2/map"),
        ("The Crew Motorfest", "Corrida", "https://tcminteractivemap.netlify.app/"),
        ("Payday 2 (Big Oil Resolver)", "Ação", "https://payday2skills.ru/bigoil.html"),
        ("Bully", "Mundo Aberto", "https://mapgenie.io/bully/maps/bullworth"),
        ("Dead Island 2", "Ação / Sobrevivência", "https://mapgenie.io/dead-island-2"),
        ("Hogwarts Legacy", "RPG", "https://mapgenie.io/hogwarts-legacy/maps/world"),
        ("Far Cry 4", "Mundo Aberto", "https://mapgenie.io/far-cry-4"),
        ("Far Cry 5", "Mundo Aberto", "https://mapgenie.io/far-cry-5"),
        ("Far Cry 6", "Mundo Aberto", "https://mapgenie.io/far-cry-6"),
        ("Watch Dogs 2", "Mundo Aberto", "https://mapgenie.io/watch-dogs-2/maps/san-francisco"),
        ("God of War Ragnarok", "Ação / Aventura", "https://mapgenie.io/god-of-war-ragnarok"),
        ("Resident Evil Village", "Terror / Sobrevivência", "https://mapgenie.io/resident-evil-village"),
        ("GTA San Andreas", "Mundo Aberto", "https://mapgenie.io/grand-theft-auto-san-andreas")
    ]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        for nome, categoria, url in jogos_iniciais:
            cursor.execute("""
                INSERT OR IGNORE INTO jogos (nome, categoria, url_mapa)
                VALUES (?, ?, ?)
            """, (nome, categoria, url))
        conn.commit()