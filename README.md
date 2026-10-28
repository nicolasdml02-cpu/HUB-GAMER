[readme_md.md](https://github.com/user-attachments/files/34104819/readme_md.md)
# 🎮 Hub Gamer — Central de Guias & Mapas Interativos

Aplicação Desktop desenvolvida em Python e PyQt6 para centralizar mapas interativos, guias de jogos, anotações personalizadas e acompanhamento progressivo de colecionáveis/checklists em tempo real.

O projeto conta com navegação web integrada, armazenamento local em **SQLite**, gerência completa de biblioteca (cadastro, edição e exclusão de jogos), painéis laterais retráteis (toggleable) e sistema de backup dedicado para exportação e importação de dados.

---

## 👥 Autor

* **Nicolas Santana de Melo**

---

## 🚀 Funcionalidades Principais

* **🗺️ Navegação & Mapas Interativos:**
  * Renderização nativa de mapas interativos e guias (MapGenie, ShackMaps, GTAWeb, etc.) usando o motor de navegação **PyQt6 WebEngine**.
  * Pré-carregamento de uma lista diversificada de jogos populares (GTA 5, RDR2, Spider-Man, God of War Ragnarok, Hogwarts Legacy, etc.).
  * Cadastro simplificado de novos jogos e guias via URLs customizadas.

* **🎮 Gerenciamento Completo de Jogos:**
  * **Adicionar, Editar e Excluir:** Adicione novos títulos, atualize nomes/URLs de mapas existentes ou remova jogos da sua biblioteca com confirmação de segurança e exclusão em cascata de notas/checklists.
  * Sem limites físicos de cadastros — suporte para centenas de jogos gerenciados localmente no SQLite.

* **🔍 Busca & Organização Dinâmica:**
  * Campo de busca dinâmica para filtragem instantânea de jogos da biblioteca local.
  * Organização intuitiva por categorias e seleção rápida com preservação de estado da tela.

* **↔️ Painéis Retráteis (Toggle Sidebars):**
  * Botões laterais integrados (`◀` / `▶`) para ocultar ou exibir rapidamente os painéis esquerdo (lista de jogos) e direito (anotações/checklist), expandindo a área visível do mapa interativo.

* **📝 Anotações por Jogo:**
  * Bloco de notas integrado com salvamento individualizado no banco de dados para cada jogo selecionado.
  * Preservação automática de notas ao alternar entre títulos.

* **✅ Checklist Progressivo de Colecionáveis:**
  * Criação de colecionáveis com quantidade total customizável definida pelo usuário (ex: Tesouros `0/20`).
  * Botões interativos de incremento (`+`) e decremento (`-`) para controle de progresso em tempo real durante a jogatina.
  * Indicador visual de conclusão e mudança de cor quando a meta do colecionável é atingida.

* **💾 Gestão de Backup Local:**
  * **Exportar Backup:** Criação de cópia de segurança completa do banco de dados local (`.db`) em qualquer diretório do sistema.
  * **Importar Backup:** Restauração rápida do histórico de jogos, anotações e progresso de checklists a partir de backups prévios.

---

## 📂 Estrutura do Projeto

| Arquivo / Pasta | Descrição |
| :--- | :--- |
| `main.py` | Ponto de entrada da aplicação que desativa GPU conflituosa e inicializa o ciclo do PyQt6. |
| `ui/main_window.py` | Interface gráfica principal (GUI) com layout splitter, botões retráteis, abas e estilo QSS Dark/Neon. |
| `modules/database.py` | Módulo de configuração, inicialização, migração e operações CRUD de baixo nível no SQLite (`gamer_hub.db`). |
| `modules/services.py` | Camada de serviço intermediária responsável pelas regras de negócio (jogos, notas, checklists e backup). |
| `assets/logo.ico` | Ícone visual utilizado na janela e no executável compilado. |
| `data/gamer_hub.db` | Arquivo do banco de dados relacional SQLite (gerado automaticamente no primeiro arranque). |
| `requirements.txt` | Lista de dependências e bibliotecas Python necessárias para o projeto. |

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.12+ / 3.x
* **Interface Gráfica (GUI):** PyQt6
* **Motor Web:** PyQt6-WebEngine (Chromium-based)
* **Banco de Dados:** SQLite 3
* **Empacotamento Executável:** PyInstaller

---

## 📦 Como Executar o Projeto

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.10+** (recomendado Python 3.12) instalado em sua máquina.

### 2. Instalação das Dependências
Instale as bibliotecas necessárias no ambiente do sistema ou ambiente de desenvolvimento através do `pip`:

```bash
pip install -r requirements.txt
```

*(Ou manualmente: `pip install PyQt6 PyQt6-WebEngine pyinstaller`)*

---

### 3. Executando em Modo de Desenvolvimento

Para rodar a aplicação via código-fonte Python:

```bash
python main.py
```

---

### 4. Gerando o Executável (.EXE)

Para compilar e gerar a versão executável autônoma para Windows (com suporte completo a ícone e empacotamento de dependências nativas do PyQt6):

```bash
python -m PyInstaller --noconsole --onedir --icon=assets/logo.ico --collect-all PyQt6 main.py
```

O aplicativo final compilado e pronto para uso estará disponível dentro do diretório **`dist/main/`** (executável `main.exe`).

---

## 💾 Banco de Dados & Backup

* **`data/gamer_hub.db`**: Armazena localmente todas as listas de jogos, URLs salvas, anotações e status dos contadores de colecionáveis.
* **Backups (.db)**: Podem ser gerados e restaurados diretamente através dos botões **"💾 Exportar"** e **"📂 Importar"** localizados no painel lateral esquerdo do sistema.
