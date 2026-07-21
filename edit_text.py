
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QWidget, QMessageBox, QFileDialog, QComboBox, QTextEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QMenu, QAction)
from PyQt5.QtGui import QFont, QTextCharFormat, QTextCursor, QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView 
import re


class EditWord(QTextEdit): # FOR INTERFACE
    word_clicked = pyqtSignal(str, int, int)  # word, start_pos, end_pos
    
    def __init__(self):
        super().__init__()
        self.misspelled_words = {}  # {word: [(start, end, suggestions)]}
        self.corrections = {}  # {orig_word: corrected_word}
        self.grammar_suggestion = {}

   
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            cursor.select(QTextCursor.WordUnderCursor)
            word = cursor.selectedText().lower().strip()
            
            print("WORD: ", word)
            
            # normalize (remove punc)
            word = re.sub(r'[^\w]', '', word)
            
            
            
            if word in self.misspelled_words:
                # get the position info for this word
                for start_pos, end_pos, suggestions in self.misspelled_words[word]:
                    if start_pos <= cursor.selectionStart() <= end_pos:
                        self.word_clicked.emit(word, start_pos, end_pos)
                        return
            elif word:
  
                for phrase_text, entries in self.grammar_suggestion.items():
                    for start_pos, end_pos, suggestions in entries:
                      
                        if start_pos <= cursor.selectionStart() <= end_pos:
                          
                            self.word_clicked.emit(phrase_text, start_pos, end_pos)
                            return

        
        super().mousePressEvent(event)

    def highlight_misspelled_words(self, misspelled_data): # highlight in red
        
        
       
        # clear previous formatting
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        format = QTextCharFormat()
        cursor.setCharFormat(format)
        
        text = self.toPlainText()
        
        for word, suggestions in misspelled_data:
            # find all occurrences of this word
            word_positions = []
            start = 0
            while True:
                # find word boundaries
                pos = text.lower().find(word.lower(), start)
                if pos == -1:
                    break
                
                # check if its a whole word (not part of another word)
                if (pos == 0 or not text[pos-1].isalnum()) and \
                   (pos + len(word) >= len(text) or not text[pos + len(word)].isalnum()):
                    word_positions.append((pos, pos + len(word)))
                
                start = pos + 1
            
            # store suggestions for this word
            self.misspelled_words[word] = [(start, end, suggestions) for start, end in word_positions]
            
            # highlight all occurrences
            for start_pos, end_pos in word_positions:
                cursor = self.textCursor()
                cursor.setPosition(start_pos)
                cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
                
                # red highlight
                format = QTextCharFormat()
                format.setBackground(QColor(255, 200, 200))  
                # format.setUnderlineColor(QColor(255, 0, 0))  
                format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
                cursor.setCharFormat(format)

    def get_corrections(self):
        print("Current corrections:", self.corrections)
        return self.corrections.copy()
    
    
    def highlight_suspicious_words(self, sus_data):
        
        
        text = self.toPlainText()
        self.grammar_suggestion = {}

        for sus in sus_data:
            phrase = sus['phrase']
            suggestions = sus['suggestions']

            # Only get the words (first element if outer tuple)
            if isinstance(phrase, tuple) and isinstance(phrase[0], tuple):
                phrase_text = ' '.join(str(w) for w in phrase[0])
            elif isinstance(phrase, tuple):
                phrase_text = ' '.join(str(w) for w in phrase)
            else:
                phrase_text = str(phrase)

            
            
            start = 0
            while True:
                pos = text.lower().find(phrase_text.lower(), start)
                if pos == -1:
                    break

                before_ok = pos == 0 or not text[pos-1].isalnum()
                after_ok = pos + len(phrase_text) >= len(text) or not text[pos + len(phrase_text)].isalnum()
                
                if before_ok and after_ok:
                    # save actual phrase positions
                    if phrase_text not in self.grammar_suggestion:
                        self.grammar_suggestion[phrase_text] = []
                    self.grammar_suggestion[phrase_text].append((pos, pos + len(phrase_text), suggestions))

                    # highlight the phrase
                    cursor = self.textCursor()
                    cursor.setPosition(pos)
                    cursor.setPosition(pos + len(phrase_text), QTextCursor.KeepAnchor)

                    format = QTextCharFormat()
                    # format.setBackground(QColor(255, 255, 150))  # yellow
                    format.setUnderlineColor(QColor(255, 180, 0))
                    format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
                    cursor.setCharFormat(format)

                start = pos + len(phrase_text)