from PySide6.QtWidgets import QMainWindow, QRadioButton, QVBoxLayout, QWidget, QButtonGroup, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import pandas as pd

class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def plot_distribution_bar(self, data, selected_subject):
        self.ax.clear()  # Clear previous plot

        subject_name = selected_subject

        # Count the number of students for each grade
        grade_counts = data[subject_name].value_counts().sort_index()

        # Bar Chart
        bars = grade_counts.plot(kind='bar', ax=self.ax, color='green', edgecolor='black')

        # Annotate each bar with its count
        for bar, count in zip(bars.patches, grade_counts):
            self.ax.annotate(str(count),
                             xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                             xytext=(0, 3),  # 3 points vertical offset
                             textcoords="offset points",
                             ha='center', va='bottom')

        self.ax.set_title(f"Distribution of marks for {subject_name}")
        self.ax.set_xlabel("Mark")
        self.ax.set_ylabel("Number of students")
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_distribution_pie(self, data, selected_subject):
        self.ax.clear()  # Clear previous plot

        subject_name = selected_subject

        # Count the number of students for each grade
        grade_counts = data[subject_name].value_counts().sort_index()

        # Pie Chart
        wedges, texts, autotexts = self.ax.pie(grade_counts, autopct='%1.1f%%', textprops=dict(color="w"))

        # Add legend with colors
        unique_values = grade_counts.index
        legend_labels = [f"{value} ({grade_counts[value]})" for value in unique_values]
        self.ax.legend(wedges, legend_labels, title=subject_name, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        for text, autotext in zip(texts, autotexts):
            text.set_color("black")
            autotext.set_color("white")

        self.ax.set_title(f"Distribution of marks for {subject_name}")
        self.figure.tight_layout()
        self.canvas.draw()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Marks Visualization")
        self.setGeometry(100, 100, 800, 600)

        # Create radio buttons
        self.radio_buttons = {
            "Analysis": QRadioButton("Analysis"),
            "Algebra": QRadioButton("Algebra"),
            "Physics": QRadioButton("Physics"),
            "Chemistry": QRadioButton("Chemistry"),
            "Computer Science": QRadioButton("Computer Science"),
            "STA": QRadioButton("STA"),
            "French": QRadioButton("French"),
            "English": QRadioButton("English")
        }

        # Button group to ensure only one chart type is selected at a time
        self.chart_type_group = QButtonGroup()
        self.chart_type_group.addButton(QRadioButton("Bar Chart"))
        self.chart_type_group.addButton(QRadioButton("Pie Chart"))

        # Set up UI layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QGridLayout()
        for i, (subject, radio_button) in enumerate(self.radio_buttons.items()):
            layout.addWidget(radio_button, i // 2, i % 2)
            radio_button.clicked.connect(self.show_chart)

        chart_type_buttons = list(self.chart_type_group.buttons())
        for i, button in enumerate(chart_type_buttons):
            layout.addWidget(button, len(self.radio_buttons) // 2 + 1, i)
            button.clicked.connect(self.show_chart)

        # Set default chart type
        chart_type_buttons[0].setChecked(True)

        # Matplotlib widget for embedding plots
        self.matplotlib_widget = MatplotlibWidget()

        layout.addWidget(self.matplotlib_widget, len(self.radio_buttons) // 2 + 2, 0, 1, -1)
        central_widget.setLayout(layout)

    def show_chart(self):
        # Read data from the Notes.txt file
        file_path = "Notes.txt"
        data = pd.read_csv(file_path, delimiter=" ", header=None,
                           names=["CIN", "Analysis", "Algebra", "Physics", "Chemistry", "Computer Science", "STA", "French", "English"])

        # Get the selected subject
        selected_subject = [subject for subject, button in self.radio_buttons.items() if button.isChecked()][0]

        # Get the selected chart type
        selected_chart_type = [button.text() for button in self.chart_type_group.buttons() if button.isChecked()][0]

        # Plot the selected chart
        if selected_chart_type == "Bar Chart":
            self.matplotlib_widget.plot_distribution_bar(data, selected_subject)
        elif selected_chart_type == "Pie Chart":
            self.matplotlib_widget.plot_distribution_pie(data, selected_subject)


