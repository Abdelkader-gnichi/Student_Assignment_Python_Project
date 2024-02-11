from PySide6.QtWidgets import QMainWindow,QHeaderView, QApplication, QTableWidgetItem, QRadioButton, QPushButton,QLabel, QComboBox,QTableWidget, QLineEdit, QMessageBox
from PySide6.QtCore import Qt,QFile, QTextStream
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path
from Model.data_dict import DataDict
import login,admin
from datetime import datetime


class StudentWindow(QMainWindow):

    def load_stylesheet(self):
        style_file = QFile("styles_student.css")
        style_file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(style_file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)
        style_file.close()

    def __init__(self,student_cin):
        super(StudentWindow, self).__init__()
        self.student_info = DataDict.candidates_dict.get(student_cin,"")
        self.student_cin = student_cin
        self.choices = {}
        # DataDict.sectors_dict = self.sector_creation()
   
        # Load the UI file using QUiLoader
        loader = QUiLoader()
        ui_file = loader.load("Student.ui")
        self.setCentralWidget(ui_file)
        self.setFixedSize(1121,886)
        # Connect buttons to functions 
        ui_file.findChild(QPushButton, "pushButton").clicked.connect(self.add_student_notes) 
        ui_file.findChild(QPushButton, "pushButton_2").clicked.connect(self.logout)  
        ui_file.findChild(QPushButton, "pushButton_3").clicked.connect(self.submit_choices) 
        self.submit_application = ui_file.findChild(QPushButton, "pushButton_3")

        self.label = ui_file.findChild(QLabel, "label")

        ui_file.findChild(QLabel, "label_6").setText(self.student_cin) 
        ui_file.findChild(QLabel, "label_5").setText(self.student_info[0])
        ui_file.findChild(QLabel, "label_7").setText(self.student_info[1]) 
        ui_file.findChild(QLabel, "label_8").setText(self.student_info[2]) 
        ui_file.findChild(QLabel, "label_8").setText(self.student_info[2]) 
        self.availability_date = ui_file.findChild(QLabel, "label_21") 
        self.check_deadline()

        # filling out the choices comboBox for the student
        for key, value in DataDict.sectors_dict.items():
            ui_file.findChild(QComboBox, "comboBox").addItem(f"{key}: {value[0]} ({value[1]})")
            ui_file.findChild(QComboBox, "comboBox_2").addItem(f"{key}: {value[0]} ({value[1]})")
            ui_file.findChild(QComboBox, "comboBox_3").addItem(f"{key}: {value[0]} ({value[1]})")
  
        self.load_stylesheet()

    def check_deadline(self):

        current_datetime = datetime.now()

        # Extract the current date
        current_date = current_datetime.date()

        # Format the date in "YYYY/MM/DD"
        formatted_date = current_date.strftime("%Y/%m/%d")      

        with open("date.txt", "r") as file:
             dead_line = file.read()

        if (str(formatted_date) > dead_line  ):

          self.availability_date.setText(f"You missed the DeadLine")
          self.availability_date.setStyleSheet("color: red;")
          self.submit_application.setEnabled(False)
        else:
             self.availability_date.setText(f"Available until {dead_line}")
             self.availability_date.setStyleSheet("color: green;")
        

        
    def logout(self):
         self.hide()
         self.login_widget = login.LoginWindow()
         self.login_widget.show()
  
    def submit_choices(self):
        # Get the selected choices from the QComboBox widgets
        choice_1 = self.findChild(QComboBox, "comboBox").currentText()
        choice_2 = self.findChild(QComboBox, "comboBox_2").currentText()
        choice_3 = self.findChild(QComboBox, "comboBox_3").currentText()

        # Extract the sector code from the choices
        sector_code_1 = choice_1.split(":")[0].strip()
        sector_code_2 = choice_2.split(":")[0].strip()
        sector_code_3 = choice_3.split(":")[0].strip()


        self.choices[self.student_cin] = [sector_code_1, sector_code_2, sector_code_3]

        
        if self.student_cin and sector_code_1 and sector_code_2  and sector_code_3:
                    
                    #
                    with open("Choices.txt", "r") as file:
                        lines = file.readlines()
                    #
                    with open("Choices.txt", "w") as file:
                        for line in lines:
                            if line.startswith(self.student_cin):
                                formatted_data = f"{self.student_cin} {sector_code_1} {sector_code_2} {sector_code_3}\n"
                                file.write(formatted_data)
                            else:
                                file.write(line)
                    #
                    with open("Choices.txt", "a") as file:

                        find_it = False
                        for line in lines: 
                            if line.startswith(self.student_cin):
                                 find_it = True

                        if  find_it == False:       
                                formatted_data = f"{self.student_cin} {sector_code_1} {sector_code_2} {sector_code_3}\n"     
                                file.write(formatted_data)


    def add_student_notes(self):
                
                try:
                    analysis = float(self.findChild(QLineEdit, "lineEdit").text())
                    Algebra = float(self.findChild(QLineEdit, "lineEdit_2").text())
                    Physics = float(self.findChild(QLineEdit, "lineEdit_3").text())
                    Chemistry = float(self.findChild(QLineEdit, "lineEdit_4").text())
                    computer_science = float(self.findChild(QLineEdit, "lineEdit_5").text())
                    sta = float(self.findChild(QLineEdit, "lineEdit_6").text())
                    French = float(self.findChild(QLineEdit, "lineEdit_7").text())
                    English = float(self.findChild(QLineEdit, "lineEdit_8").text())
                except ValueError as e:
                     QMessageBox.warning(self, "Warning", "Please enter a valid Note.")
                     
                     
                 
                if self.student_cin and analysis  and Algebra  and Physics  and Chemistry and computer_science and sta   and French and English:
                    
                    if (
                    self.student_cin
                    and 0 <= analysis <= 20
                    and 0 <= Algebra <= 20
                    and 0 <= Physics <= 20
                    and 0 <= Chemistry <= 20
                    and 0 <= computer_science <= 20
                    and 0 <= sta <= 20
                    and 0 <= French <= 20
                    and 0 <= English <= 20
                    ):
                    #
                        with open("Notes.txt", "r") as file:
                            lines = file.readlines()
                        #
                        with open("Notes.txt", "w") as file:
                            for line in lines:
                                if line.startswith(self.student_cin):
                                    formatted_data = f"{self.student_cin} {analysis} {Algebra} {Physics} {Chemistry} {computer_science} {sta} {French} {English}\n"
                                    file.write(formatted_data)
                                else:
                                    file.write(line)
                        #
                        with open("Notes.txt", "a") as file:
                            
                            find_it = False
                            for line in lines: 
                                if line.startswith(self.student_cin):
                                    find_it = True

                            if  find_it == False:       
                                formatted_data = f"{self.student_cin} {analysis} {Algebra} {Physics} {Chemistry} {computer_science} {sta} {French} {English}\n"     
                                file.write(formatted_data)


                        # Clear input fields
                        self.findChild(QLineEdit, "lineEdit").clear()
                        self.findChild(QLineEdit, "lineEdit_2").clear()
                        self.findChild(QLineEdit, "lineEdit_3").clear()
                        self.findChild(QLineEdit, "lineEdit_4").clear()
                        self.findChild(QLineEdit, "lineEdit_5").clear()
                        self.findChild(QLineEdit, "lineEdit_6").clear()
                        self.findChild(QLineEdit, "lineEdit_7").clear()
                        self.findChild(QLineEdit, "lineEdit_8").clear()

                    else:
                        QMessageBox.warning(self, "Warning", "Please enter a valid Note between 0 and 20.")             
                
