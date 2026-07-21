import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QWidget, QMessageBox, QFileDialog, QComboBox, QTextEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QMenu, QAction, QProgressDialog)
from PyQt5.QtGui import QFont, QTextCharFormat, QTextCursor, QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from PyQt5.QtWebEngineWidgets import QWebEngineView 
import re



from SpellChecker.spell_checker import SpellChecker
from Grammar_Checking.grammar_checker import Grammar_Checker
from edit_text import EditWord
from pdf_processor import PDFProcessor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(700, 300, 900, 700)
        self.init_ui()
       
        self.current_translation = 'Academic Proof Reader'  # default 
        self.spell_checker = SpellChecker(n=3, filename="SpellChecker/words.txt", sentence="SpellChecker/academic_corpus.txt")  
        self.grammar_checker = Grammar_Checker()
        if self.spell_checker:
            print("spell checker initialized successfully")
            
        if self.grammar_checker:
            print("Grammar Checker initialized successfully")

        self.pdf_processor = PDFProcessor()
        self.current_misspelled_data = []  # to store current misspelled words found
        self.current_suspicious_data = []
        
        self.uploaded_file_path = None
        self.is_modified = False
        self.orig_text = ""

    def init_ui(self):
        central_widget = QWidget() # generic widget to hold other widgets
        self.setCentralWidget(central_widget)
        
        
        

        self.setWindowTitle("Academic Proof Reader")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #C8B6FF, stop:1 #BBCFFF);
            }
                           
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9966FF, stop:1 #FFA500);
                border: none;
                border-radius: 25px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                color: #9966FF;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9999FF, stop:1 #9999FF);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E6C200, stop:1 #E6941A);
            }
            
            QPushButton:disabled {
                background: #D3D3D3;
                color: #808080;
            }
            
            QPushButton#swapBtn {
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(184, 134, 11, 0.3);
                border-radius: 30px;
                min-width: 50px;
                max-width: 60px;
                min-height: 50px;
                max-height: 60px;
                font-size: 20px;
            }
            
            QPushButton#swapBtn:hover {
                background: rgba(255, 255, 255, 1.0);
                border: 2px solid #B8860B;
            }
            QLabel {
                color: #4E6BA6;
                font-size: 68px;
                font-weight: bold;
                letter-spacing: 4px;
                margin: 20px 0px;
            }
                           

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3399FF, stop:1 #9966FF);
                border: none;
                border-radius: 25px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3366FF, stop:1 #9933FF);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0000FF, stop:1 #9900CC);
            }
            
            QPushButton:disabled {
                background: #D3D3D3;
                color: #808080;
            }

            QTextEdit {
                background: white;
                border: 10px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                font-size: 24px;
                color: #333;
            }
                           
            QMessageBox {
                font-size: 16px;
                color: #2c3e50;
                min-width: 400px;
                min-height: 200px;
            }

            QMessageBox QLabel {
                background: transparent;
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                margin: 10px;
                border-radius: 8px;
                letter-spacing: 1px;
            }

            QMenu {
                background-color: #f0f0f0;
                border: 5px solid #ccc;
                border-radius: 10px;
                padding: 10px;

            }
            QMenu::item {
                padding: 8px 12px;
                font-size: 16px;
                
            }
            QMenu::item:selected {
                background-color: #d0d0d0;
            }    

        """)


        layout = QVBoxLayout(central_widget) # MAIN LAYOUT
        layout.setSpacing(30)
        layout.setContentsMargins(50, 30, 50, 30)
        
        title = QLabel("Academic Proof Reader")
        title.setObjectName('title')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        pdf_layout = QHBoxLayout()

        self.input_text = EditWord()
        self.input_text.setPlaceholderText("Enter text or upload a file...")
        pdf_layout.addWidget(self.input_text)

        # self.pdf_input_viewer = QWebEngineView()
        # self.pdf_input_viewer.setMinimumHeight(100)  # like old QTextEdit height
        # pdf_layout.addWidget(self.pdf_input_viewer, stretch=1)
        
        # self.pdf_output_viewer = QWebEngineView()
        # self.pdf_output_viewer.setMinimumHeight(400)
        # pdf_layout.addWidget(self.pdf_output_viewer, stretch=1)

        self.input_text.setMinimumHeight(400)
        self.input_text.word_clicked.connect(self.show_suggestions)

        self.input_text.textChanged.connect(self.show_exportBtn)  # check if text changed

        layout.addLayout(pdf_layout)
         
        
        
        button_layout = QHBoxLayout() # BUTTONS LAYOUT
        button_layout.setSpacing(20)

        self.upload_button = QPushButton("Upload File") # UPLOAD BUTTON
        # self.upload_button.clicked.connect(lambda: print("Upload button clicked"))  
        self.upload_button.clicked.connect(self.upload_file) 
        button_layout.addWidget(self.upload_button)

        # EXPORT BUTTON
        self.export_button = QPushButton("Export")
        self.export_button.setObjectName('exportBtn')
        self.export_button.clicked.connect(self.export_file)
        self.export_button.hide() 
        button_layout.addWidget(self.export_button)

        button_layout.addStretch()  

        # SEPARATE SPELL CHECK BUTTON
        self.spellCheck_button = QPushButton("Spell Check")
        self.spellCheck_button.clicked.connect(self.spell_check)
        button_layout.addWidget(self.spellCheck_button)

        # SEPARATE GRAMMAR CHECK BUTTON  
        self.grammarCheck_button = QPushButton("Grammar Check")
        self.grammarCheck_button.clicked.connect(self.grammar_check)
        button_layout.addWidget(self.grammarCheck_button)

        self.clear_button = QPushButton("Clear") # CLEAR BUTTON
        # self.clear_button.clicked.connect(lambda: print("Clear button clicked"))
        self.clear_button.clicked.connect(self.clear_text)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

    def upload_file(self):
        # print("Upload file")
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            'Open Text File', 
            '', 
            'Documents (*.txt *.pdf *.docx)'
        )

        if file_path:
            self.uploaded_file_path = file_path
            self.is_pdf_source = file_path.lower().endswith('.pdf')
            
            try:
                if self.is_pdf_source: # for pdf
                    content = self.pdf_processor.load_pdf(file_path)
                    self.input_text.setPlainText(content)
                    # print(f"PDF content loaded from {file_path}")
                    # print(content)
                else: # if txt file
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.input_text.setPlainText(content)

                self.orig_text = content
                self.is_modified = False
                self.export_button.hide()

            except Exception as e:
                print(f"Error reading file: {e}")
                self.input_text.setPlainText("Error reading file. Please try again.")
                self.uploaded_file_path = None
        # dito pdf extraction logic. (will use pymupdf instead for handling layout nung text)
        
    
    def export_file(self):
        print("export file")

        corrections = self.input_text.get_corrections()
        print(f'Corrections found: {corrections}')


        # FOR MANUALLY TYPING
        current_text = self.input_text.toPlainText()
        if self.orig_text and current_text != self.orig_text:
            orig_words = re.findall(r'\b\w+\b', self.orig_text)
            new_words = re.findall(r'\b\w+\b', current_text)

            for ow, nw in zip(orig_words, new_words):
                if ow != nw:
                    corrections[ow.lower()] = nw

        print(f'Corrections found: {corrections}')

        if not corrections:
            QMessageBox.information(self, "Info", "No corrections have been made")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            'Save Corrected PDF', 
            'corrected_document.pdf',
            'PDF Files (*.pdf);;All Files (*)'
        )
        
        if file_path:
            try:
                # apply changes
                success = self.pdf_processor.create_changes(corrections, file_path)
                
                if success is None or success is True:
                    QMessageBox.information(self, "Success", 
                        f"PDF exported successfully\n"
                        f"Applied {len(corrections)} corrections.")
                else:
                    QMessageBox.warning(self, "Warning", "PDF export completed but some issues may have occurred.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exporting PDF: {e}")




    def show_exportBtn(self):
        text = self.input_text.toPlainText()

        if self.uploaded_file_path and text != self.orig_text:
            self.is_modified = True
            self.export_button.show()

        elif self.uploaded_file_path and text == self.orig_text:
                self.is_modified = False
                self.export_button.hide()
                
    def show_progress(self, message="Checking text, please wait..."):
        progress = QProgressDialog(message, None, 0, 0, self)
        progress.setWindowModality(Qt.ApplicationModal)
        progress.setWindowTitle("Processing")
        progress.setMinimumDuration(0)
        progress.resize(500, 50)          
        progress.setFixedSize(500, 50)
        
        progress.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #555;
                    border-radius: 8px;
                    text-align: center;
                    height: 16px;
                    background: #eee;
                }
                QProgressBar::chunk {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2196F3,   /* Blue */
                        stop:1 #9C27B0    /* Purple */
                    );
                    border-radius: 6px;
                }
        """)
        progress.show()
        QApplication.processEvents()
        return progress

    def spell_check(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text")
            return
        
        progress = self.show_progress("Running spell check...")

        try:
            tokens = self.spell_checker.tokenize(text)
            
            errors_found = []
            
            print("\nSPELL CHECK RESULTS:")

            for i, token in enumerate(tokens):
                if token not in self.spell_checker.corpus:
                    suggestions = self.spell_checker.check_context(token, tokens, i)
                    print(suggestions)
                    if suggestions:
                        # collect only candidate words 
                        cand_list = [cand for cand, _, _, _ in suggestions]
                        errors_found.append((token, cand_list))
                        print(f"Misspelled: {token} -> Suggestions: {cand_list}")
                    # else:
                    #     print(f"Misspelled: {token} -> No suggestions found")

            # store current misspelled data
            self.current_misspelled_data = errors_found  # format: (token, [list of suggestions])
         
            self.input_text.highlight_misspelled_words(errors_found)
            self.input_text.highlight_suspicious_words([])  # Clear grammar highlights
            
            if not errors_found:
                QMessageBox.information(self, "Spell Check", "No spelling errors found!")
            else:
                QMessageBox.information(self, "Spell Check", f"Found {len(errors_found)} spelling errors. Click on highlighted words to see suggestions.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during spell checking: {str(e)}")
            print(f"Spell check error: {e}")
            
        finally:
            progress.close()

    def grammar_check(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text")
            return
        
        progress = self.show_progress("Running grammar check...")

        try:
            grammarCheck = self.grammar_checker.grammar_check(text)
            
            print("GRAMMAR CHECK", grammarCheck)
            
            self.current_suspicious_data = grammarCheck if grammarCheck else []
            print("Grammar check results:", self.current_suspicious_data)
            
            # Highlight grammar errors (clear previous highlights by passing empty spelling data)
            self.input_text.highlight_misspelled_words([])  # Clear spelling highlights
            self.input_text.highlight_suspicious_words(self.current_suspicious_data)
            
            if not self.current_suspicious_data:
                QMessageBox.information(self, "Grammar Check", "No grammar errors found (good job)!")
            else:
                QMessageBox.information(self, "Grammar Check", f"Found {len(self.current_suspicious_data)} potential grammar issues. Click on highlighted words to see suggestions.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during grammar checking: {str(e)}")
            print(f"Grammar check error: {e}")
            
        finally:
            progress.close()

    def show_suggestions(self, word, start_pos, end_pos):
        print("WENT HERE", word)
        # print(f"Word clicked: {word} at positions {start_pos}-{end_pos}")
        suggestions = None

        # SPELLING SUGGESTIONS
        for misspelled_word, word_suggestions in self.current_misspelled_data:
            # print(f"\nMisspelled word: {misspelled_word}, Suggestions: {word_suggestions}")
            if misspelled_word.lower() == word.lower():
                suggestions = word_suggestions
                break

        # GRAMMAR SUGGESTIONS
        if not suggestions and self.current_suspicious_data:
            for sus in self.current_suspicious_data:
                suggestion = sus.get('suggestions', [])
                p = sus.get('phrase', '')
                
                if isinstance(p, tuple):
                    if isinstance(p[0], tuple):
                        phrase = ' '.join(p[0])
                    else:
                        phrase = ' '.join(p)
                else:
                    phrase = str(p)
                
                print(f"Checking grammar phrase: '{phrase}' against word: '{word}'")
                
                if word.lower() == phrase.lower():
                    print("Grammar match found!")
                    suggestions = suggestion
                    break
                
        if not suggestions:
            return
            
        if isinstance(suggestions, str):  
            suggestions = [suggestions]
            
        menu = QMenu(self) # popup widget
        menu.setTitle(f"Suggestions for '{word}':")

        for suggestion in suggestions:
            action = QAction(suggestion, self)
            action.triggered.connect(lambda checked, s=suggestion: self.replace_word(word, s, start_pos, end_pos))
            menu.addAction(action) # add suggestion to popup menu

        menu.addSeparator()
        ignore_action = QAction("Ignore", self)
        ignore_action.triggered.connect(lambda: self.ignore_word(word))
        menu.addAction(ignore_action)
        
        # show menu at cursor position
        cursor = self.input_text.textCursor()
        cursor.setPosition(start_pos)
        rect = self.input_text.cursorRect(cursor)
        menu.exec_(self.input_text.mapToGlobal(rect.bottomLeft()))

    def replace_word(self, old_word, new_word, start_pos, end_pos):
        cursor = self.input_text.textCursor()
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        cursor.insertText(new_word)

        # store correction (for spelling & grammar)
        self.input_text.corrections[old_word.lower()] = new_word
        
        # for grammar corrections that involve phrases, also store individual words
        if ' ' in old_word:  # if phrase
            old_words = old_word.split()
            new_words = new_word.split()
            
            # map each old word to its corresponding new word if possible
            if len(old_words) == len(new_words):
                for i, (old_w, new_w) in enumerate(zip(old_words, new_words)):
                    if old_w.lower() != new_w.lower():  # store if they're different
                        self.input_text.corrections[old_w.lower()] = new_w
            else:
                # for different length phrases, store the whole phrase mapping
                print(f"Phrase length mismatch: '{old_word}' -> '{new_word}'")
      
        self.input_text.highlight_misspelled_words(self.current_misspelled_data)
        self.input_text.highlight_suspicious_words(self.current_suspicious_data)

    def ignore_word(self, word):
        # Remove from current misspelled data
        self.current_misspelled_data = [(w, s) for w, s in self.current_misspelled_data if w.lower() != word.lower()]
        
        # Remove from current suspicious data  
        self.current_suspicious_data = [sus for sus in self.current_suspicious_data 
                                       if not self._matches_suspicious_phrase(word, sus)]

        # Refresh highlights
        self.input_text.highlight_misspelled_words(self.current_misspelled_data)
        self.input_text.highlight_suspicious_words(self.current_suspicious_data)
        
    def _matches_suspicious_phrase(self, word, sus_item):
        p = sus_item.get('phrase', '')
        if isinstance(p, tuple):
            if isinstance(p[0], tuple):
                phrase = ' '.join(p[0])
            else:
                phrase = ' '.join(p)
        else:
            phrase = str(p)
        return word.lower() == phrase.lower()
        
    def clear_text(self):
        self.input_text.clear()
        self.current_misspelled_data = []
        self.current_suspicious_data = []
        self.export_button.hide()


#-----------------MAIN FUNCTION-----------------
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Academic Proof Reader")
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()