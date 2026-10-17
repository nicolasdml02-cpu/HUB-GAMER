import sys
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QLineEdit, QTextEdit, QLabel, QPushButton, QCheckBox, QListWidgetItem,
    QTabWidget, QSplitter
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from modules.database import init_db
from modules.services import (
    listar_jogos, obter_anotacao, salvar_anotacao,
    listar_checklist, adicionar_item_checklist,
    alternar_status_checklist, remover_item_checklist
)

# QSS: Estilo Gamer Dark / Neon
GAMER_STYLE = """
QMainWindow {
    background-color: #0f1015;
}

/* Divisores de painel */
QSplitter::handle {
    background-color: #1a1c23;
    width: 3px;
}

/* Painéis e Labels */
QWidget {
    background-color: #0f1015;
    color: #e0e6ed;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

QLabel {
    color: #00f0ff;
    font-weight: bold;
}

/* Campo de busca e inputs */
QLineEdit {
    background-color: #181a20;
    border: 1px solid #2d313e;
    border-radius: 6px;
    padding: 8px;
    color: #ffffff;
    selection-background-color: #7000ff;
}

QLineEdit:focus {
    border: 1px solid #00f0ff;
}

/* Lista de Jogos */
QListWidget {
    background-color: #14151b;
    border: 1px solid #232631;
    border-radius: 8px;
    outline: none;
    padding: 4px;
}

QListWidget::item {
    padding: 10px;
    border-radius: 6px;
    color: #c0c7d1;
    margin-bottom: 2px;
}

QListWidget::item:hover {
    background-color: #1e212b;
    color: #00f0ff;
}

QListWidget::item:selected {
    background-color: #7000ff;
    color: #ffffff;
    font-weight: bold;
}

/* Abas Direitas */
QTabWidget::pane {
    border: 1px solid #232631;
    background-color: #14151b;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #181a20;
    color: #a0a7b5;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #7000ff;
    color: #ffffff;
    font-weight: bold;
}

/* Caixa de Anotações */
QTextEdit {
    background-color: #181a20;
    border: 1px solid #232631;
    border-radius: 6px;
    color: #e0e6ed;
    padding: 8px;
}

/* Botões Gamer */
QPushButton {
    background-color: #7000ff;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #8b24ff;
    color: #00f0ff;
}

QPushButton:pressed {
    background-color: #5300bd;
}

/* Checkboxes */
QCheckBox {
    color: #d0d7de;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #3b4050;
    background-color: #181a20;
}

QCheckBox::indicator:checked {
    background-color: #00f0ff;
    border: 1px solid #00f0ff;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hub Gamer - Central de Guias & Mapas")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet(GAMER_STYLE)

        init_db()
        self.todos_jogos = listar_jogos()
        self.jogo_atual = None

        self._init_ui()

    def _init_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # -----------------------------------------------------------------
        # PAINEL ESQUERDO: LISTA DE JOGOS & BUSCA
        # -----------------------------------------------------------------
        panel_left = QWidget()
        layout_left = QVBoxLayout(panel_left)

        lbl_jogos = QLabel("🎮 MEUS JOGOS")
        lbl_jogos.setStyleSheet("font-size: 15px; letter-spacing: 1px; color: #00f0ff;")
        layout_left.addWidget(lbl_jogos)

        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("🔍 Buscar jogo...")
        self.input_busca.textChanged.connect(self._filtrar_jogos)
        layout_left.addWidget(self.input_busca)

        self.list_jogos = QListWidget()
        self.list_jogos.itemClicked.connect(self._ao_selecionar_jogo)
        layout_left.addWidget(self.list_jogos)

        # -----------------------------------------------------------------
        # PAINEL CENTRAL: NAVEGADOR
        # -----------------------------------------------------------------
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("about:blank"))

        # -----------------------------------------------------------------
        # PAINEL DIREITO: ABAS DE ANOTAÇÕES & CHECKLIST
        # -----------------------------------------------------------------
        panel_right = QWidget()
        layout_right = QVBoxLayout(panel_right)

        self.tabs_right = QTabWidget()

        # Aba Anotações
        tab_anotacoes = QWidget()
        layout_anotacoes = QVBoxLayout(tab_anotacoes)
        
        self.lbl_jogo_anotacao = QLabel("Selecione um jogo")
        self.lbl_jogo_anotacao.setStyleSheet("color: #00f0ff; font-size: 14px;")
        layout_anotacoes.addWidget(self.lbl_jogo_anotacao)

        self.txt_anotacao = QTextEdit()
        self.txt_anotacao.setPlaceholderText("Escreva dicas, códigos ou notas de localização...")
        layout_anotacoes.addWidget(self.txt_anotacao)

        btn_salvar_nota = QPushButton("💾 Salvar Anotações")
        btn_salvar_nota.clicked.connect(self._salvar_anotacao_atual)
        layout_anotacoes.addWidget(btn_salvar_nota)

        self.tabs_right.addTab(tab_anotacoes, "📝 Anotações")

        # Aba Checklist
        tab_checklist = QWidget()
        layout_checklist = QVBoxLayout(tab_checklist)

        self.input_item_check = QLineEdit()
        self.input_item_check.setPlaceholderText("Novo item/colecionável...")
        
        btn_add_check = QPushButton("➕ Add")
        btn_add_check.clicked.connect(self._adicionar_item_check)

        layout_add_item = QHBoxLayout()
        layout_add_item.addWidget(self.input_item_check)
        layout_add_item.addWidget(btn_add_check)
        layout_checklist.addLayout(layout_add_item)

        self.list_checklist = QListWidget()
        layout_checklist.addWidget(self.list_checklist)

        self.tabs_right.addTab(tab_checklist, "✅ Checklist")

        layout_right.addWidget(self.tabs_right)

        splitter.addWidget(panel_left)
        splitter.addWidget(self.browser)
        splitter.addWidget(panel_right)

        splitter.setSizes([220, 880, 300])
        self.setCentralWidget(splitter)

        self._carregar_lista_jogos(self.todos_jogos)

        if self.todos_jogos:
            self.list_jogos.setCurrentRow(0)
            self._ao_selecionar_jogo(self.list_jogos.item(0))

    def _carregar_lista_jogos(self, lista):
        self.list_jogos.clear()
        for jogo in lista:
            item = QListWidgetItem(f"{jogo['nome']}")
            item.setData(Qt.ItemDataRole.UserRole, jogo)
            self.list_jogos.addItem(item)

    def _filtrar_jogos(self, texto):
        termo = texto.lower()
        filtrados = [j for j in self.todos_jogos if termo in j['nome'].lower() or termo in j['categoria'].lower()]
        self._carregar_lista_jogos(filtrados)

    def _ao_selecionar_jogo(self, item):
        if not item:
            return
        
        # Salva a anotação do jogo anterior antes de trocar
        self._salvar_anotacao_atual()

        self.jogo_atual = item.data(Qt.ItemDataRole.UserRole)
        
        # 1. Carrega URL
        url = QUrl(self.jogo_atual["url_mapa"])
        self.browser.setUrl(url)

        # 2. Carrega Anotações
        self.lbl_jogo_anotacao.setText(f"📌 {self.jogo_atual['nome']}")
        texto_nota = obter_anotacao(self.jogo_atual["id"])
        self.txt_anotacao.setText(texto_nota)

        # 3. Carrega Checklist
        self._atualizar_checklist_ui()

    def _salvar_anotacao_atual(self):
        if self.jogo_atual:
            texto = self.txt_anotacao.toPlainText()
            salvar_anotacao(self.jogo_atual["id"], texto)

    def _atualizar_checklist_ui(self):
        self.list_checklist.clear()
        if not self.jogo_atual:
            return

        itens = listar_checklist(self.jogo_atual["id"])
        for it in itens:
            item_widget = QWidget()
            layout_item = QHBoxLayout(item_widget)
            layout_item.setContentsMargins(4, 4, 4, 4)

            chk = QCheckBox(it["item_nome"])
            chk.setChecked(bool(it["concluido"]))
            chk.stateChanged.connect(lambda state, item_id=it["id"]: alternar_status_checklist(item_id, state == 2))

            btn_del = QPushButton("❌")
            btn_del.setFixedWidth(30)
            btn_del.setStyleSheet("background-color: #381018; color: #ff4d4d;")
            
            item_id_atual = it["id"]
            btn_del.clicked.connect(lambda checked=False, i_id=item_id_atual: self._remover_item_check(i_id))

            layout_item.addWidget(chk)
            layout_item.addWidget(btn_del)

            list_item = QListWidgetItem(self.list_checklist)
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_checklist.addItem(list_item)
            self.list_checklist.setItemWidget(list_item, item_widget)

    def _adicionar_item_check(self):
        nome_item = self.input_item_check.text().strip()
        if nome_item and self.jogo_atual:
            adicionar_item_checklist(self.jogo_atual["id"], nome_item)
            self.input_item_check.clear()
            self._atualizar_checklist_ui()

    def _remover_item_check(self, item_id):
        remover_item_checklist(item_id)
        self._atualizar_checklist_ui()