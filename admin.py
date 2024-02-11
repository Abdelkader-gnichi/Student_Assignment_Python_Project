from PySide6.QtWidgets import QMainWindow,QHeaderView, QApplication, QTableWidgetItem, QRadioButton, QPushButton, QTableWidget, QLineEdit, QMessageBox, QCalendarWidget
from PySide6.QtCore import Qt,QFile, QTextStream
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path
from Model.data_dict import DataDict
import login
from datetime import datetime
import visualisation
import sys


class AdminWindow(QMainWindow):
   
    def load_stylesheet(self):
        style_file = QFile("styles.css")
        style_file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(style_file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)
        style_file.close()
    def __init__(self):
        super(AdminWindow, self).__init__()
        
        # Initialise Sector Dict
        DataDict.sectors_dict = self.sector_creation()
   
        # Load the UI file using QUiLoader
        loader = QUiLoader()
        ui_file = loader.load("Admin.ui")
        self.setCentralWidget(ui_file)
        self.setFixedSize(1121,886)
        self.choices_rank_dict = {}
        
            # Load the CSS stylesheet
        self.load_stylesheet()

        # Connect buttons to functions
        ui_file.findChild(QPushButton, "pushButton").clicked.connect(self.add_candidate)
        ui_file.findChild(QPushButton, "pushButton_2").clicked.connect(self.edit_candidate)
        ui_file.findChild(QPushButton, "pushButton_3").clicked.connect(self.delete_candidate)
        ui_file.findChild(QPushButton, "pushButton_4").clicked.connect(self.logout)
        self.assign_bnt = ui_file.findChild(QPushButton, "pushButton_5")
        self.assign_bnt.clicked.connect(self.assign_students)
        self.dead_line_widget = ui_file.findChild(QCalendarWidget, "calendarWidget_2")
        ui_file.findChild(QPushButton, "pushButton_6").clicked.connect(self.show_plot)


        # Connect the selectionChanged signal to a slot (function)
        self.dead_line_widget.selectionChanged.connect(self.handle_date_selection)
    
        # Initialize table
        self.tableWidget = ui_file.findChild(QTableWidget, "tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["CIN", "First Name", "Last Name", "Field"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        # Load candidates from file
        self.load_candidates()

        # Connect item selection to function
        self.tableWidget.itemSelectionChanged.connect(self.update_fields_from_table)
        
        

    # Initialize tableWidget_2 for notes
        self.tableWidget_2 = ui_file.findChild(QTableWidget, "tableWidget_2")
        self.tableWidget_2.setColumnCount(9)
        self.tableWidget_2.setHorizontalHeaderLabels(["CIN", "Analysis", "Algebra", "Physics", "Chemistry", "Computer Science", "STA", "French", "English"])
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # Initialize tableWidget_4 for choices, scores, and ranks
        self.tableWidget_4 = ui_file.findChild(QTableWidget, "tableWidget_4")
        self.tableWidget_4.setColumnCount(6)
        self.tableWidget_4.setHorizontalHeaderLabels(["CIN", "Choice 1", "Choice 2", "Choice 3", "Score", "Rank"])
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Load data from files and populate tableWidget_4


        # Load notes from file and populate tableWidget_2
        self.load_notes()
        #
        self.creation_rang()
        self.load_rank_and_choices()
        self.check_deadline()

    def show_plot(self):
        
        self.window = visualisation.MainWindow()
        self.window.show()
        
    def check_deadline(self):

        current_datetime = datetime.now()

        # Extract the current date
        current_date = current_datetime.date()

        # Format the date in "YYYY/MM/DD"
        formatted_date = current_date.strftime("%Y/%m/%d")      

        with open("date.txt", "r") as file:
             dead_line = file.read()

        if (str(formatted_date) <= dead_line):
          self.assign_bnt.setEnabled(False)
        else:
            self.assign_bnt.setEnabled(True)

        
             

    def assign_students(self):
        # Create Results.txt file and initialize it
        open("Results.txt", "w").close()

        # Iterate through students starting from the top rank
        for cin, choices in self.choices_rank_dict.items():
            # Iterate through the choices of the candidate
            for choice in choices[:3]:
                sector_code = choice
                available_places = DataDict.sectors_dict[sector_code][1]

                # Check if there are available places in the sector
                if available_places > 0:
                    # Assign the student to the sector
                    self.assign_student_to_sector(cin, sector_code)
                    break  # Stop checking other choices if assigned
                else:
                    # Move to the next choice if places are not available
                    continue

        # Save the updated sectors_dict to the file or update it in memory
        self.save_sectors_dict_to_file()

        QMessageBox.information(self, "Result Creation Completed", "Results have been successfully created.")
        
    def assign_student_to_sector(self, cin, sector_code):
        # Decrement the available places in the sector
        DataDict.sectors_dict[sector_code][1] -= 1

        # Save the assignment to Resultats.txt
        with open("Results.txt", "a") as resultats_file:
            resultats_file.write(f"{cin} {sector_code}\n")

    def save_sectors_dict_to_file(self):
        # Save the updated sectors_dict to the file
        with open("Sectors.txt", "w") as sectors_file:
            for code, (school, places) in DataDict.sectors_dict.items():
                sectors_file.write(f"{code} {school} {places}\n")

##############
    def load_rank_and_choices(self):
        # Load data from Rank.txt
        rank_dict = self.load_data_from_file("Rank.txt")

        # Load data from Choices.txt
        choices_dict = self.load_data_from_file("Choices.txt")

        # Update the tableWidget_4 with the loaded data
        self.update_table_with_rank_and_choices(rank_dict, choices_dict)

    def load_data_from_file(self, file_name):
        # Load data from the specified file and return it as a dictionary
        data_dict = {}

        if Path(file_name).exists():
            with open(file_name, "r") as file:
                lines = file.readlines()
                for line in lines:
                    data = line.strip().split()
                    cin = data[0]
                    data_dict[cin] = data[1:]

        return data_dict

    def update_table_with_rank_and_choices(self, rank_dict, choices_dict):
        # Clear the existing tableWidget_4
        self.tableWidget_4.setRowCount(0)

        # Find common CINs in both dictionaries
        common_cins = set(rank_dict.keys()) & set(choices_dict.keys())

        # Add rows for each common CIN
        for cin in common_cins:
            # Extract data from rank_dict and choices_dict
            rank_data = rank_dict[cin]
            choices_data = choices_dict[cin]

            # Merge data into a single list for table display
            display_data = [cin, choices_data[0], choices_data[1], choices_data[2], rank_data[0], rank_data[1]]
            self.choices_rank_dict[cin] = display_data[1:]
            # Add a row to tableWidget_4
            

        self.choices_rank_dict =dict(sorted(self.choices_rank_dict.items(), key= lambda x: int(x[1][4])))

        for cin in self.choices_rank_dict:
            self.add_row_to_table([cin, self.choices_rank_dict[cin][0], self.choices_rank_dict[cin][1], self.choices_rank_dict[cin][2], self.choices_rank_dict[cin][3], self.choices_rank_dict[cin][4]], self.tableWidget_4)
            
    def add_row_to_table(self, data, table_widget):
        # Add a row to the specified table widget
        row_position = table_widget.rowCount()
        table_widget.insertRow(row_position)
        for col, value in enumerate(data):
            item = QTableWidgetItem(value)
            table_widget.setItem(row_position, col, item)

    def handle_date_selection(self):
        # This function will be called when the user selects a date
        selected_date = self.dead_line_widget.selectedDate()
        formatted_date = selected_date.toString("yyyy/MM/dd")  
        with open("date.txt" , "w") as file:
            file.write(formatted_date)
        self.check_deadline()
     

  
    def creation_rang(self):
        # Clear existing content of Rang.txt
        open("Rank.txt", "w").close()
        rank_dict = {}
        
        # Iterate through students and calculate FG
        for cin, notes in self.load_notes().items():
            # Extracting individual note values
            analysis, algebra, physics, chemistry, computer_science, sta, french, english = map(float, notes)

            # Calculating FG
            fg = analysis * 8 + algebra * 6 + physics * 8 + chemistry * 6 + computer_science * 6 + sta * 4 + french * 3 + english * 3

            rank_dict[cin] = fg


        # sorting the Rank.txt content
        for rang, items  in enumerate(sorted(rank_dict.items(), key = lambda x: int(x[1]), reverse= True)):
             
               
            # Save CIN and rang to Rang.txt
            with open("Rank.txt", "a") as rang_file:
                rang_file.write(f"{items[0]} {items[1]} {rang+1}\n")
                
    def load_notes(self):
        # Clear the existing tableWidget_2
        self.tableWidget_2.setRowCount(0)
        notes_dict = {}

        # Read notes from file and populate tableWidget_2
        if Path("Notes.txt").exists():
            with open("Notes.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    data = line.strip().split()
                    notes_dict[data[0]] = data[1:]
                    self.add_row_to_notes(data)
            return notes_dict
        
    def add_row_to_notes(self, data):
        # Add a row to tableWidget_2
        row_position = self.tableWidget_2.rowCount()
        self.tableWidget_2.insertRow(row_position)
        for col, value in enumerate(data):
            item = QTableWidgetItem(value)
            self.tableWidget_2.setItem(row_position, col, item)

    def logout(self):
        self.hide()
        self.login_widget = login.LoginWindow()
        self.login_widget.show()

    def sector_creation(self):
        sector = {
            'SAI_GE': ['SAI', 60],
            'SAI_GM': ['SAI', 60],
            'SAI_GI': ['SAI', 64],
            'SAI_GC': ['SAI', 55],
            'SAI_MIS': ['SAI', 27],
            'SAI_GHE': ['SAI', 16],
            'SAI_TA': ['SAI', 18],
            'SAI_TC': ['SAI', 51],
            'SAI_INFO': ['SAI', 51],
            'ENIB_GI': ['ENIB', 40],
            'ENIB_GM': ['ENIB', 27],
            'ENIB_GC': ['ENIB', 16],
            # Add more sectors as needed
        }

        return sector

    
    def edit_candidate(self):
        selected_row = self.tableWidget.currentRow()

        if selected_row != -1:
            cin = self.findChild(QLineEdit, "lineEdit").text()
            first_name = self.findChild(QLineEdit, "lineEdit_2").text()
            last_name = self.findChild(QLineEdit, "lineEdit_3").text()
            field = "MP" if self.findChild(QRadioButton, "radioButton").isChecked() else "PC"

            if cin and first_name and last_name: 
                if len(cin) == 8:
                    # Update the selected row in the table
                    for col, value in enumerate([cin, first_name, last_name, field]):
                        item = QTableWidgetItem(value)
                        self.tableWidget.setItem(selected_row, col, item)

                    # Update the candidate in the file
                    with open("Candidates.txt", "r") as file:
                        lines = file.readlines()

                    with open("Candidates.txt", "w") as file:
                        for i, line in enumerate(lines):
                            if i == selected_row:
                                formatted_data = f"{cin} {first_name} {last_name} {field}\n"
                                file.write(formatted_data)
                            else:
                                file.write(line)

                    # Clear input fields
                    self.findChild(QLineEdit, "lineEdit").clear()
                    self.findChild(QLineEdit, "lineEdit_2").clear()
                    self.findChild(QLineEdit, "lineEdit_3").clear()
                    self.findChild(QRadioButton, "radioButton").setChecked(True)

                    # Reload candidates into the table
                    self.load_candidates()
                else: 
                 QMessageBox.warning(self, "Warning", "CIN must have 8 digits.")
            else:
                QMessageBox.warning(self, "Warning", "Please enter all candidate details.")

    def delete_candidate(self):
        selected_row = self.tableWidget.currentRow()

        if selected_row != -1:
            # Remove the selected row from the table
            self.tableWidget.removeRow(selected_row)

            # Remove the selected candidate from the file
            with open("Candidates.txt", "r") as file:
                lines = file.readlines()

            with open("Candidates.txt", "w") as file:
                for i, line in enumerate(lines):
                    if i != selected_row:
                        file.write(line)

            # Clear input fields
            self.findChild(QLineEdit, "lineEdit").clear()
            self.findChild(QLineEdit, "lineEdit_2").clear()
            self.findChild(QLineEdit, "lineEdit_3").clear()
            self.findChild(QRadioButton, "radioButton").setChecked(True)
        else:
            QMessageBox.warning(self, "Warning", "Please select a candidate to delete.")

    def load_candidates(self):
        # Clear the existing table
        self.tableWidget.setRowCount(0)
        
        # Read candidates from file and populate the table
        if Path("Candidates.txt").exists():
            with open("Candidates.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    data = line.strip().split()
                    DataDict.candidates_dict[data[0]] = data[1:]
                    self.add_row(data)
            

    def add_row(self, data):
        # Add a row to the table
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        for col, value in enumerate(data):
            item = QTableWidgetItem(value)
            self.tableWidget.setItem(row_position, col, item)

    def update_fields_from_table(self):
        selected_row = self.tableWidget.currentRow()

        if selected_row != -1:
            cin = self.tableWidget.item(selected_row, 0).text()
            first_name = self.tableWidget.item(selected_row, 1).text()
            last_name = self.tableWidget.item(selected_row, 2).text()
            field = self.tableWidget.item(selected_row, 3).text()

            # Update the fields in the UI
            self.findChild(QLineEdit, "lineEdit").setText(cin)
            self.findChild(QLineEdit, "lineEdit_2").setText(first_name)
            self.findChild(QLineEdit, "lineEdit_3").setText(last_name)

            if field == "MP":
                self.findChild(QRadioButton, "radioButton").setChecked(True)
            elif field == "PC":
                self.findChild(QRadioButton, "radioButton_2").setChecked(True)


    def add_row(self, data):
        # Add a row to the table
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        for col, value in enumerate(data):
            item = QTableWidgetItem(value)
            self.tableWidget.setItem(row_position, col, item)

    def add_candidate(self):
        # Add a candidate to the table and save to file
        cin = self.findChild(QLineEdit, "lineEdit").text()
        first_name = self.findChild(QLineEdit, "lineEdit_2").text()
        last_name = self.findChild(QLineEdit, "lineEdit_3").text()
        field = "MP" if self.findChild(QRadioButton, "radioButton").isChecked() else "PC"

        if cin and first_name and last_name:
            if len(cin) == 8:
                data = [cin, first_name, last_name, field]

                # Add the candidate to the table
                self.add_row(data)

                # Save the candidate to file
                with open("Candidates.txt", "a") as file:
                    formatted_data = f"{cin} {first_name} {last_name} {field}\n"
                    file.write(formatted_data)

                # Clear input fields
                self.findChild(QLineEdit, "lineEdit").clear()
                self.findChild(QLineEdit, "lineEdit_2").clear()
                self.findChild(QLineEdit, "lineEdit_3").clear()
                self.findChild(QRadioButton, "radioButton").setChecked(True)

                # Reload candidates into the table
                self.load_candidates()
            else: 
                 QMessageBox.warning(self, "Warning", "CIN must have 8 digits.")
        else:
            QMessageBox.warning(self, "Warning", "Please enter all candidate details.")
