from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QTextBrowser, QPushButton, QLineEdit, QVBoxLayout, QWidget
from PySide6.QtCore import Qt,QFile, QTextStream
from PySide6.QtGui import QFont

from PySide6.QtUiTools import QUiLoader
import admin
import student 

class LoginWindow(QMainWindow):
    def load_stylesheet(self):
        style_file = QFile("styles_login.css")
        style_file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(style_file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)
        style_file.close()
    def __init__(self):
        super(LoginWindow, self).__init__()

        # Load UI from login.ui
        loader = QUiLoader()
        ui_file = loader.load("login.ui")
        self.setCentralWidget(ui_file)

        # Accessing UI components
        self.pushButton = ui_file.findChild(QPushButton, "pushButton")
        self.label = ui_file.findChild(QLabel, "label")
        self.lineEdit = ui_file.findChild(QLineEdit, "lineEdit")
        self.textBrowser = ui_file.findChild(QTextBrowser, "textBrowser")

        # Connect login button to the login function
        self.pushButton.clicked.connect(self.login)

        # Set additional styles or modifications
        self.label.setStyleSheet("font: italic bold 20pt 'Cantarell';color: rgb(0, 0, 0);")
        self.textBrowser.setStyleSheet("font-family: 'Cantarell'; font-size: 14pt; font-weight: 400; font-style: normal;")
        self.setFixedSize(1121,886)

        # Initialize admin widget
        self.admin_widget = admin.AdminWindow()
        self.load_stylesheet()

    def login(self):
        entered_code = self.lineEdit.text()

        if self.is_admin_code(entered_code):
            self.textBrowser.setHtml("<p style='color: green;'>Admin logged in!</p>")
            self.hide()
            self.admin_widget.show()
            # Add code to open admin interface or perform admin actions
        elif self.is_student_cin(entered_code):
            self.textBrowser.setHtml("<p style='color: green;'>Student logged in!</p>")
            self.hide()

            # Create and show the StudentWindow with the correct CIN
            self.student_window = student.StudentWindow(entered_code)
            self.student_window.show()
        else:
            self.textBrowser.setHtml("<p style='color: red;'>Invalid code. Please try again.</p>")

    def is_admin_code(self, entered_code):
        try:
            with open("Admin.txt", "r") as file:
                return entered_code == file.read().strip()
        except FileNotFoundError:
            return False

    def is_student_cin(self, entered_cin):
        try:
            with open("Candidates.txt", "r") as file:
                for line in file:
                    cin = line.split()[0]  # Assuming CIN is the first item in each line
                    if cin == entered_cin:
                        return True
            return False
        except FileNotFoundError:
            return False
