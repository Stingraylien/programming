import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTextEdit, QWidget, 
                             QFileDialog, QMessageBox)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class MacOSApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Set window properties
        self.setWindowTitle('Mac GUI Python App')
        self.setGeometry(100, 100, 600, 400)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Title Label
        title_label = QLabel('Simple Mac GUI Application')
        title_label.setFont(QFont('San Francisco', 18))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Input Section
        input_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Enter your name')
        input_button = QPushButton('Greet')
        input_button.clicked.connect(self.greet_user)
        
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(input_button)
        main_layout.addLayout(input_layout)
        
        # Output Text Area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        main_layout.addWidget(self.output_text)
        
        # File Selection Button
        file_button = QPushButton('Select File')
        file_button.clicked.connect(self.select_file)
        main_layout.addWidget(file_button)
        
        # Set the layout
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def greet_user(self):
        """Handle greeting when button is clicked"""
        name = self.name_input.text()
        if name:
            greeting = f'Hello, {name}! Welcome to the Mac GUI App.'
            self.output_text.append(greeting)
        else:
            QMessageBox.warning(self, 'Input Error', 'Please enter a name.')
    
    def select_file(self):
        """Open file dialog for file selection"""
        file_path, _ = QFileDialog.getOpenFileName(self, 
                                                   'Select a File', 
                                                   os.path.expanduser('~'), 
                                                   'All Files (*)')
        if file_path:
            self.output_text.append(f'Selected File: {file_path}')

def main():
    # Create the application
    app = QApplication(sys.argv)
    
    # Set the application name (shows in menu bar)
    app.setApplicationName('Mac GUI App')
    
    # Create and show the main window
    main_window = MacOSApp()
    main_window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
