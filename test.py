import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction, 
                            QFileDialog, QMessageBox, QStatusBar, QFontDialog,
                            QInputDialog)
from PyQt5.QtGui import QFont, QIcon, QDesktopServices, QTextCursor
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtCore import Qt, QUrl
from pathlib import Path
import platform

class SimpleEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Documentos - Lotes Rurais")
        self.setGeometry(100, 100, 800, 1000)
        
        # Configurações
        self.current_file = None
        self.cpf_mode = True
        self.cidade_padrao = "Toledo"
        
        # Inicialização da UI
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
        # Texto inicial
        self.set_initial_text()
        
    def setup_ui(self):
        self.editor = QTextEdit(self)
        self.editor.setFont(QFont("Calibri", 12))
        self.editor.setAcceptRichText(True)
        self.editor.textChanged.connect(self.update_statusbar)
        self.setCentralWidget(self.editor)
        self.editor.keyPressEvent = self.custom_key_press_event
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu Arquivo
        arquivo_menu = menubar.addMenu("&Arquivo")
        novo_action = QAction(QIcon.fromTheme("document-new"), "&Novo", self)
        novo_action.setShortcut("Ctrl+N")
        novo_action.triggered.connect(self.novo_documento)
        arquivo_menu.addAction(novo_action)
        
        abrir_action = QAction(QIcon.fromTheme("document-open"), "&Abrir", self)
        abrir_action.setShortcut("Ctrl+O")
        abrir_action.triggered.connect(self.abrir_arquivo)
        arquivo_menu.addAction(abrir_action)
        
        salvar_action = QAction(QIcon.fromTheme("document-save"), "&Salvar", self)
        salvar_action.setShortcut("Ctrl+S")
        salvar_action.triggered.connect(self.salvar_arquivo)
        arquivo_menu.addAction(salvar_action)
        
        salvar_como_action = QAction("Salvar &como...", self)
        salvar_como_action.triggered.connect(self.salvar_como)
        arquivo_menu.addAction(salvar_como_action)
        
        arquivo_menu.addSeparator()
        
        exportar_action = QAction(QIcon.fromTheme("document-export"), "&Exportar PDF", self)
        exportar_action.setShortcut("Ctrl+P")
        exportar_action.triggered.connect(self.exportar_pdf)
        arquivo_menu.addAction(exportar_action)
        
        arquivo_menu.addSeparator()
        
        sair_action = QAction(QIcon.fromTheme("application-exit"), "Sai&r", self)
        sair_action.setShortcut("Ctrl+Q")
        sair_action.triggered.connect(self.close)
        arquivo_menu.addAction(sair_action)
        
        # Menu Editar
        editar_menu = menubar.addMenu("&Editar")
        
        desfazer_action = QAction(QIcon.fromTheme("edit-undo"), "&Desfazer", self)
        desfazer_action.setShortcut("Ctrl+Z")
        desfazer_action.triggered.connect(self.editor.undo)
        editar_menu.addAction(desfazer_action)
        
        refazer_action = QAction(QIcon.fromTheme("edit-redo"), "&Refazer", self)
        refazer_action.setShortcut("Ctrl+Y")
        refazer_action.triggered.connect(self.editor.redo)
        editar_menu.addAction(refazer_action)
        
        editar_menu.addSeparator()
        
        cortar_action = QAction(QIcon.fromTheme("edit-cut"), "Cor&tar", self)
        cortar_action.setShortcut("Ctrl+X")
        cortar_action.triggered.connect(self.editor.cut)
        editar_menu.addAction(cortar_action)
        
        copiar_action = QAction(QIcon.fromTheme("edit-copy"), "&Copiar", self)
        copiar_action.setShortcut("Ctrl+C")
        copiar_action.triggered.connect(self.editor.copy)
        editar_menu.addAction(copiar_action)
        
        colar_action = QAction(QIcon.fromTheme("edit-paste"), "C&olar", self)
        colar_action.setShortcut("Ctrl+V")
        colar_action.triggered.connect(self.editor.paste)
        editar_menu.addAction(colar_action)
        
        editar_menu.addSeparator()
        
        selecionar_tudo_action = QAction("Selecionar &Tudo", self)
        selecionar_tudo_action.setShortcut("Ctrl+A")
        selecionar_tudo_action.triggered.connect(self.editor.selectAll)
        editar_menu.addAction(selecionar_tudo_action)
        
        # Menu Formatar
        formatar_menu = menubar.addMenu("F&ormatar")
        
        fonte_action = QAction("&Fonte...", self)
        fonte_action.triggered.connect(self.selecionar_fonte)
        formatar_menu.addAction(fonte_action)
        
        formatar_menu.addSeparator()
        
        toggle_action = QAction("Alternar CPF/CNPJ (Ctrl+J)", self)
        toggle_action.setShortcut("Ctrl+J")
        toggle_action.triggered.connect(self.toggle_cpf_cnpj)
        formatar_menu.addAction(toggle_action)
        
        cidade_action = QAction("Definir Cidade Padrão", self)
        cidade_action.triggered.connect(self.definir_cidade_padrao)
        formatar_menu.addAction(cidade_action)
        
        # Menu Ajuda
        ajuda_menu = menubar.addMenu("A&juda")
        sobre_action = QAction("&Sobre", self)
        sobre_action.triggered.connect(self.mostrar_sobre)
        ajuda_menu.addAction(sobre_action)
    
    def setup_toolbar(self):
        toolbar = self.addToolBar("Ferramentas")
        
        actions = [
            ("document-new", "Novo", "Ctrl+N", self.novo_documento),
            ("document-open", "Abrir", "Ctrl+O", self.abrir_arquivo),
            ("document-save", "Salvar", "Ctrl+S", self.salvar_arquivo),
            None,
            ("edit-cut", "Cortar", "Ctrl+X", self.editor.cut),
            ("edit-copy", "Copiar", "Ctrl+C", self.editor.copy),
            ("edit-paste", "Colar", "Ctrl+V", self.editor.paste),
            None,
            ("document-export", "Exportar PDF", "Ctrl+P", self.exportar_pdf)
        ]
        
        for action in actions:
            if action is None:
                toolbar.addSeparator()
            else:
                icon, text, shortcut, callback = action
                act = QAction(QIcon.fromTheme(icon), text, self)
                act.setShortcut(shortcut)
                act.triggered.connect(callback)
                toolbar.addAction(act)
    
    def setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_statusbar()
    
    def update_statusbar(self):
        cursor = self.editor.textCursor()
        text = self.editor.toPlainText()
        status_text = (f"Linha: {cursor.blockNumber()+1}, Coluna: {cursor.columnNumber()+1} | "
                      f"Caracteres: {len(text)} | Palavras: {len(text.split())}")
        if self.current_file:
            status_text += f" | Arquivo: {Path(self.current_file).name}"
        self.status_bar.showMessage(status_text)
    
    def set_initial_text(self):
        self.editor.setPlainText(
            "Lote Rural Nº — Matrícula Nº . — º Serviço de Registro de Imóveis, Toledo - Paraná\n"
            "______________________________\n"
            " — CPF Nº ..-..-..-..\n"
            "“Estou ciente de que, nos termos do §10 do artigo 213 da LRP, minha anuência supre a participação do cônjuge e de eventuais outros condôminos titulares de nosso imóvel”.\n"
        )
    
    def custom_key_press_event(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ShiftModifier:
            self.adicionar_item()
        else:
            QTextEdit.keyPressEvent(self.editor, event)
    
    def adicionar_item(self):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        cidade = self.extrair_cidade_atual()
        
        if self.cpf_mode:
            template = (
                f"\n\nLote Rural Nº — Matrícula Nº . — º Serviço de Registro de Imóveis, {cidade} - Paraná\n"
                "______________________________\n"
                " — CPF Nº ..-..-..-..\n"
                "“Estou ciente de que, nos termos do §10 do artigo 213 da LRP, minha anuência supre a participação do cônjuge e de eventuais outros condôminos titulares de nosso imóvel”.\n"
            )
        else:
            template = (
                f"\n\nLote Rural Nº — Matrícula Nº . — º Serviço de Registro de Imóveis, {cidade} - Paraná\n"
                "______________________________\n"
                " — CNPJ Nº ..-...-.../....-..\n"
                "“Estou ciente de que, nos termos do §10 do artigo 213 da LRP, minha anuência supre a participação do cônjuge e de eventuais outros condôminos titulares de nosso imóvel”.\n"
            )
        
        cursor.insertText(template)
    
    def extrair_cidade_atual(self):
        texto = self.editor.toPlainText()
        match = re.search(r"Serviço de Registro de Imóveis, (.+?) - Paraná", texto)
        return match.group(1) if match else self.cidade_padrao
    
    def toggle_cpf_cnpj(self):
        self.cpf_mode = not self.cpf_mode
        self.status_bar.showMessage(f"Modo documento: {'CPF' if self.cpf_mode else 'CNPJ'}", 2000)
    
    def definir_cidade_padrao(self):
        cidade, ok = QInputDialog.getText(
            self, "Definir Cidade", 
            "Digite a cidade padrão:", 
            text=self.cidade_padrao
        )
        if ok and cidade:
            self.cidade_padrao = cidade
            self.status_bar.showMessage(f"Cidade padrão definida para: {cidade}", 2000)
    
    def novo_documento(self):
        if self.verificar_alteracoes_nao_salvas():
            self.editor.clear()
            self.current_file = None
            self.setWindowTitle("Editor de Documentos - Lotes Rurais")
            self.set_initial_text()
    
    def abrir_arquivo(self):
        if self.verificar_alteracoes_nao_salvas():
            caminho, _ = QFileDialog.getOpenFileName(
                self, "Abrir Arquivo", "", 
                "Arquivos de Texto (*.txt);;Todos os Arquivos (*)"
            )
            
            if caminho:
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        self.editor.setPlainText(f.read())
                    self.current_file = caminho
                    self.setWindowTitle(f"Editor de Documentos - {Path(caminho).name}")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Não foi possível abrir o arquivo:\n{str(e)}")
    
    def salvar_arquivo(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.status_bar.showMessage(f"Arquivo salvo: {self.current_file}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível salvar o arquivo:\n{str(e)}")
        else:
            self.salvar_como()
    
    def salvar_como(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Arquivo", "", 
            "Arquivos de Texto (*.txt);;Todos os Arquivos (*)"
        )
        
        if caminho:
            self.current_file = caminho
            self.salvar_arquivo()
            self.setWindowTitle(f"Editor de Documentos - {Path(caminho).name}")
    
    def exportar_pdf(self):
        try:
            caminho, _ = QFileDialog.getSaveFileName(
                self, "Exportar como PDF", "", 
                "PDF Files (*.pdf)"
            )
            
            if not caminho:
                return

            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(caminho)
            printer.setPageSize(QPrinter.A4)
            printer.setFullPage(False)
            
            self.editor.document().print_(printer)
            self.abrir_pdf(caminho)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar PDF:\n{str(e)}")
    
    def abrir_pdf(self, file_path):
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Não foi possível abrir o PDF:\n{str(e)}")
    
    def selecionar_fonte(self):
        font, ok = QFontDialog.getFont(self.editor.font(), self, "Selecionar Fonte")
        if ok:
            self.editor.setFont(font)
    
    def verificar_alteracoes_nao_salvas(self):
        if not self.editor.document().isModified():
            return True
            
        resposta = QMessageBox.question(
            self, "Alterações não salvas",
            "O documento foi modificado. Deseja salvar as alterações?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        
        if resposta == QMessageBox.Save:
            self.salvar_arquivo()
            return True
        elif resposta == QMessageBox.Discard:
            return True
        else:
            return False
    
    def mostrar_sobre(self):
        sobre_texto = f"""
        <h2>Editor de Documentos - Lotes Rurais</h2>
        <p>Versão 1.0</p>
        <p>Editor especializado para documentos de lotes rurais</p>
        <p>Desenvolvido com PyQt5</p>
        <p>Sistema: {platform.system()} {platform.release()}</p>
        <p>Python: {platform.python_version()}</p>
        """
        QMessageBox.about(self, "Sobre o Editor", sobre_texto)
    
    def closeEvent(self, event):
        if self.verificar_alteracoes_nao_salvas():
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    if QIcon.themeName() == "":
        QIcon.setThemeName("Adwaita")
    window = SimpleEditor()
    window.showMaximized()
    sys.exit(app.exec_())