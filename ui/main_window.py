import sys
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QLineEdit, QTextEdit, QLabel, QPushButton, QListWidgetItem,
    QTabWidget, QSplitter, QInputDialog, QMessageBox, QFileDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from modules.database import init_db
from modules.services import (
    listar_jogos, cadastrar_jogo, exportar_backup_db, importar_backup_db,
    obter_anotacao, salvar_anotacao, listar_checklist, adicionar_item_checklist,
    atualizar_contador_checklist, remover_item_checklist, editar_jogo, excluir_jogo
)

# QSS: Estilo Gamer Dark / Neon
GAMER_STYLE = """
QMainWindow {
    background-color: #0f1015;
}

QSplitter::handle {
    background-color: #1a1c23;
    width: 3px;
}

QWidget {
    background-color: #0f1015;
    color: #e0e6ed;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

QLabel {
    color: #00f0ff;
    font-weight: bold;
}

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

QListWidget {
    background-color: #14151b;
    border: 1px solid #232631;
    border-radius: 8px;
    outline: none;
    padding: 4px;
}

QListWidget::item {
    padding: 6px;
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

QTextEdit {
    background-color: #181a20;
    border: 1px solid #232631;
    border-radius: 6px;
    color: #e0e6ed;
    padding: 8px;
}

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

QPushButton#btn-acao {
    background-color: #1c1f2b;
    border: 1px solid #323748;
    color: #a0a7b5;
    font-size: 12px;
}

QPushButton#btn-acao:hover {
    background-color: #262b3c;
    color: #00f0ff;
    border-color: #00f0ff;
}

QPushButton#btn-toggle {
    background-color: #1a1c23;
    color: #00f0ff;
    border: 1px solid #2d313e;
    font-size: 10px;
    font-weight: bold;
    border-radius: 4px;
}

QPushButton#btn-toggle:hover {
    background-color: #7000ff;
    color: #ffffff;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hub Gamer - Central de Guias & Mapas")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet(GAMER_STYLE)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_icone = os.path.join(base_dir, "assets", "logo.ico")
        if not os.path.exists(caminho_icone):
            caminho_icone = os.path.join(base_dir, "assets", "logo.png")
            
        if os.path.exists(caminho_icone):
            self.setWindowIcon(QIcon(caminho_icone))

        init_db()
        self.todos_jogos = listar_jogos()
        self.jogo_atual = None

        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # -----------------------------------------------------------------
        # PAINEL ESQUERDO: LISTA DE JOGOS, BUSCA E GERENCIAMENTO
        # -----------------------------------------------------------------
        self.panel_left = QWidget()
        layout_left = QVBoxLayout(self.panel_left)

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

        btn_add_jogo = QPushButton("➕ Adicionar Novo Jogo")
        btn_add_jogo.clicked.connect(self._abrir_modal_adicionar_jogo)
        layout_left.addWidget(btn_add_jogo)

        # Botões de Editar e Excluir Jogo Selecionado
        layout_acoes_jogo = QHBoxLayout()
        btn_editar_jogo = QPushButton("✏️ Editar")
        btn_editar_jogo.setObjectName("btn-acao")
        btn_editar_jogo.clicked.connect(self._abrir_modal_editar_jogo)

        btn_excluir_jogo = QPushButton("🗑️ Excluir")
        btn_excluir_jogo.setObjectName("btn-acao")
        btn_excluir_jogo.clicked.connect(self._excluir_jogo_atual)

        layout_acoes_jogo.addWidget(btn_editar_jogo)
        layout_acoes_jogo.addWidget(btn_excluir_jogo)
        layout_left.addLayout(layout_acoes_jogo)

        layout_backup = QHBoxLayout()
        btn_exportar = QPushButton("💾 Exportar")
        btn_exportar.setObjectName("btn-acao")
        btn_exportar.clicked.connect(self._exportar_backup)

        btn_importar = QPushButton("📂 Importar")
        btn_importar.setObjectName("btn-acao")
        btn_importar.clicked.connect(self._importar_backup)

        layout_backup.addWidget(btn_exportar)
        layout_backup.addWidget(btn_importar)
        layout_left.addLayout(layout_backup)

        # -----------------------------------------------------------------
        # PAINEL CENTRAL: NAVEGADOR
        # -----------------------------------------------------------------
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("about:blank"))

        # -----------------------------------------------------------------
        # PAINEL DIREITO: ABAS DE ANOTAÇÕES & CHECKLIST
        # -----------------------------------------------------------------
        self.panel_right = QWidget()
        layout_right = QVBoxLayout(self.panel_right)

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
        self.input_item_check.setPlaceholderText("Nome do colecionável (ex: Tesouros)...")
        
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

        # Adicionar os painéis ao Splitter principal
        self.splitter.addWidget(self.panel_left)
        self.splitter.addWidget(self.browser)
        self.splitter.addWidget(self.panel_right)
        self.splitter.setSizes([240, 860, 300])

        # Botões colados nas abas para esconder/mostrar painéis lateralmente
        self.btn_toggle_left = QPushButton("◀")
        self.btn_toggle_left.setObjectName("btn-toggle")
        self.btn_toggle_left.setFixedWidth(20)
        self.btn_toggle_left.setToolTip("Esconder/Mostrar Painel Esquerdo")
        self.btn_toggle_left.clicked.connect(self._alternar_painel_esquerdo)

        self.btn_toggle_right = QPushButton("▶")
        self.btn_toggle_right.setObjectName("btn-toggle")
        self.btn_toggle_right.setFixedWidth(20)
        self.btn_toggle_right.setToolTip("Esconder/Mostrar Painel Direito")
        self.btn_toggle_right.clicked.connect(self._alternar_painel_direito)

        # Montagem do layout central da janela
        main_layout.addWidget(self.btn_toggle_left)
        main_layout.addWidget(self.splitter)
        main_layout.addWidget(self.btn_toggle_right)

        container_central = QWidget()
        container_central.setLayout(main_layout)
        self.setCentralWidget(container_central)

        self._carregar_lista_jogos(self.todos_jogos)
        if self.todos_jogos:
            self.list_jogos.setCurrentRow(0)
            self._ao_selecionar_jogo(self.list_jogos.item(0))

    def _alternar_painel_esquerdo(self):
        visivel = self.panel_left.isVisible()
        self.panel_left.setVisible(not visivel)
        self.btn_toggle_left.setText("▶" if visivel else "◀")

    def _alternar_painel_direito(self):
        visivel = self.panel_right.isVisible()
        self.panel_right.setVisible(not visivel)
        self.btn_toggle_right.setText("◀" if visivel else "▶")

    def _carregar_lista_jogos(self, lista):
        self.list_jogos.clear()
        for jogo in lista:
            item = QListWidgetItem(f"{jogo['nome']}")
            item.setData(Qt.ItemDataRole.UserRole, jogo)
            self.list_jogos.addItem(item)

    def _filtrar_jogos(self, texto):
        termo = texto.lower()
        filtrados = [j for j in self.todos_jogos if termo in j['nome'].lower()]
        self._carregar_lista_jogos(filtrados)

    def _abrir_modal_adicionar_jogo(self):
        nome_jogo, ok1 = QInputDialog.getText(self, "Adicionar Jogo", "Digite o nome do jogo:")
        if not ok1 or not nome_jogo.strip():
            return
        
        url_mapa, ok2 = QInputDialog.getText(self, "Adicionar Jogo", "Cole a URL do mapa ou guia:")
        if not ok2 or not url_mapa.strip():
            return

        try:
            cadastrar_jogo(nome_jogo.strip(), url_mapa.strip())
            self.todos_jogos = listar_jogos()
            self._filtrar_jogos(self.input_busca.text())
            QMessageBox.information(self, "Sucesso", f"O jogo '{nome_jogo}' foi cadastrado com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível cadastrar o jogo.\nDetalhes: {e}")

    def _abrir_modal_editar_jogo(self):
        if not self.jogo_atual:
            QMessageBox.warning(self, "Aviso", "Selecione um jogo para editar.")
            return

        novo_nome, ok1 = QInputDialog.getText(self, "Editar Jogo", "Novo nome do jogo:", text=self.jogo_atual["nome"])
        if not ok1 or not novo_nome.strip():
            return

        nova_url, ok2 = QInputDialog.getText(self, "Editar Jogo", "Nova URL do mapa ou guia:", text=self.jogo_atual["url_mapa"])
        if not ok2 or not nova_url.strip():
            return

        try:
            editar_jogo(self.jogo_atual["id"], novo_nome.strip(), nova_url.strip(), self.jogo_atual.get("categoria", "Geral"))
            self.todos_jogos = listar_jogos()
            self._filtrar_jogos(self.input_busca.text())
            
            # Atualiza o jogo selecionado atualmente
            for jogo in self.todos_jogos:
                if jogo["id"] == self.jogo_atual["id"]:
                    self.jogo_atual = jogo
                    break
            
            self.browser.setUrl(QUrl(self.jogo_atual["url_mapa"]))
            self.lbl_jogo_anotacao.setText(f"📌 {self.jogo_atual['nome']}")
            QMessageBox.information(self, "Sucesso", "Jogo atualizado com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao atualizar o jogo: {e}")

    def _excluir_jogo_atual(self):
        if not self.jogo_atual:
            QMessageBox.warning(self, "Aviso", "Selecione um jogo para excluir.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o jogo '{self.jogo_atual['nome']}'?\nTodas as anotações e checklists associadas serão apagadas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            try:
                excluir_jogo(self.jogo_atual["id"])
                self.todos_jogos = listar_jogos()
                self._filtrar_jogos(self.input_busca.text())
                
                if self.todos_jogos:
                    self.list_jogos.setCurrentRow(0)
                    self._ao_selecionar_jogo(self.list_jogos.item(0))
                else:
                    self.jogo_atual = None
                    self.browser.setUrl(QUrl("about:blank"))
                    self.lbl_jogo_anotacao.setText("Selecione um jogo")
                    self.txt_anotacao.clear()
                    self.list_checklist.clear()

                QMessageBox.information(self, "Sucesso", "Jogo excluído com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao excluir o jogo: {e}")

    def _exportar_backup(self):
        self._salvar_anotacao_atual()
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar Backup do Banco de Dados", "gamer_hub_backup.db", "Database Files (*.db)")
        if caminho:
            try:
                exportar_backup_db(caminho)
                QMessageBox.information(self, "Sucesso", "Backup exportado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao exportar backup: {e}")

    def _importar_backup(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Backup", "", "Database Files (*.db)")
        if caminho:
            try:
                importar_backup_db(caminho)
                self.todos_jogos = listar_jogos()
                self._carregar_lista_jogos(self.todos_jogos)
                if self.todos_jogos:
                    self.list_jogos.setCurrentRow(0)
                    self._ao_selecionar_jogo(self.list_jogos.item(0))
                QMessageBox.information(self, "Sucesso", "Backup importado com sucesso! Dados atualizados.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao importar backup: {e}")

    def _ao_selecionar_jogo(self, item):
        if not item:
            return
        
        self._salvar_anotacao_atual()
        self.jogo_atual = item.data(Qt.ItemDataRole.UserRole)
        
        url = QUrl(self.jogo_atual["url_mapa"])
        self.browser.setUrl(url)

        self.lbl_jogo_anotacao.setText(f"📌 {self.jogo_atual['nome']}")
        texto_nota = obter_anotacao(self.jogo_atual["id"])
        self.txt_anotacao.setText(texto_nota)

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
            layout_item.setContentsMargins(2, 2, 2, 2)

            status_cor = "#00f0ff" if it["concluido"] else "#d0d7de"
            lbl_texto = QLabel(f"{it['item_nome']}  ({it['atual']}/{it['total']})")
            lbl_texto.setStyleSheet(f"color: {status_cor}; font-size: 13px;")

            btn_menos = QPushButton("➖")
            btn_menos.setFixedSize(30, 26)
            btn_menos.setStyleSheet("background-color: #232631; color: #fff; font-size: 11px;")
            btn_menos.clicked.connect(lambda checked=False, i_id=it["id"]: self._alterar_progresso(i_id, -1))

            btn_mais = QPushButton("➕")
            btn_mais.setFixedSize(30, 26)
            btn_mais.setStyleSheet("background-color: #7000ff; color: #fff; font-size: 11px;")
            btn_mais.clicked.connect(lambda checked=False, i_id=it["id"]: self._alterar_progresso(i_id, 1))

            btn_del = QPushButton("❌")
            btn_del.setFixedSize(30, 26)
            btn_del.setStyleSheet("background-color: #381018; color: #ff4d4d; font-size: 11px;")
            btn_del.clicked.connect(lambda checked=False, i_id=it["id"]: self._remover_item_check(i_id))

            layout_item.addWidget(lbl_texto)
            layout_item.addStretch()
            layout_item.addWidget(btn_menos)
            layout_item.addWidget(btn_mais)
            layout_item.addWidget(btn_del)

            list_item = QListWidgetItem(self.list_checklist)
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_checklist.addItem(list_item)
            self.list_checklist.setItemWidget(list_item, item_widget)

    def _adicionar_item_check(self):
        nome_item = self.input_item_check.text().strip()
        if not nome_item or not self.jogo_atual:
            return

        total, ok = QInputDialog.getInt(self, "Total de Colecionáveis", f"Defina a quantidade total para '{nome_item}':", 10, 1, 10000, 1)
        if not ok:
            return

        adicionar_item_checklist(self.jogo_atual["id"], nome_item, total)
        self.input_item_check.clear()
        self._atualizar_checklist_ui()

    def _alterar_progresso(self, item_id, delta):
        atualizar_contador_checklist(item_id, delta)
        self._atualizar_checklist_ui()

    def _remover_item_check(self, item_id):
        remover_item_checklist(item_id)
        self._atualizar_checklist_ui()