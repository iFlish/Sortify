import sys
import ctypes
from ctypes import POINTER, c_double, c_int

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QListWidget, QStackedWidget, QLabel, QHBoxLayout, QListWidgetItem,
    QFileDialog, QMessageBox, QComboBox
)

from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QComboBox


# Load the C++ library
lib = ctypes.cdll.LoadLibrary("./libsort.so")
lib.bubble_sort.argtypes = [POINTER(c_double), c_int, POINTER(c_double)]
lib.selection_sort.argtypes = [POINTER(c_double), c_int, POINTER(c_double)]


class PageOne(QWidget):
    def __init__(self, stacked_widget, data, page_two_ref=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.data = data
        self.page_two_ref = page_two_ref
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("💸 Enter Your Expenses")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Expense Name")
        self.name_input.setFont(QFont("Arial", 12))
        layout.addWidget(self.name_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.amount_input.setFont(QFont("Arial", 12))
        layout.addWidget(self.amount_input)

        btn_layout = QHBoxLayout()

        add_btn = QPushButton("➕ Add Expense")
        add_btn.clicked.connect(self.add_expense)
        btn_layout.addWidget(add_btn)

        upload_btn = QPushButton("📂 Upload File")
        upload_btn.clicked.connect(self.upload_file)
        btn_layout.addWidget(upload_btn)

        layout.addLayout(btn_layout)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        next_btn = QPushButton("➡ Next")
        next_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(next_btn)

        self.setLayout(layout)
        self.apply_styles()

    def upload_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Expense File", "", "Text Files (*.txt *.csv)")
        if not file_name:
            return

        try:
            with open(file_name, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        try:
                            amount = float(parts[-1])
                            name = ' '.join(parts[:-1])
                            self.data.append((name, amount))
                            item = QListWidgetItem(f"{name} - ${amount:.2f}")
                            self.list_widget.addItem(item)
                        except ValueError:
                            continue
        except Exception as e:
            QMessageBox.warning(self, "File Error", f"Failed to read file:\n{str(e)}")

    def add_expense(self):
        name = self.name_input.text().strip()
        amount_text = self.amount_input.text().strip()
        try:
            amount = float(amount_text)
            if name:
                self.data.append((name, amount))
                item = QListWidgetItem(f"{name} - ${amount:.2f}")
                self.list_widget.addItem(item)
                self.name_input.clear()
                self.amount_input.clear()
        except ValueError:
            pass

    def clear_list(self):
        self.list_widget.clear()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F2F2F2, stop:1 #CBCBCB);
                color: #1C1C1C;
            }
            QLineEdit {
                background-color: white;
                padding: 6px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #174D38;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1f6b50;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #aaa;
            }
        """)


class PageTwo(QWidget):
    def __init__(self, stacked_widget, data, page_one_ref=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.data = data
        self.page_one_ref = page_one_ref

        # Visualization data
        self.name_list = []
        self.amounts = []
        self.index = 0
        self.subindex = 0
        self.min_index = 0

        self.sorted_bubble = []
        self.sorted_selection = []

        self.timer = QTimer()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("📊 Sorting Results")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.sort_selector = QComboBox()
        self.sort_selector.addItems(["Bubble Sort", "Selection Sort"])
        self.sort_selector.setFont(QFont("Arial", 11))
        layout.addWidget(QLabel("📌 Animate Sort Using:"))
        layout.addWidget(self.sort_selector)

        self.bubble_label = QLabel("Bubble Sort Time: N/A")
        self.selection_label = QLabel("Selection Sort Time: N/A")
        layout.addWidget(self.bubble_label)
        layout.addWidget(self.selection_label)

        self.sorted_list = QListWidget()
        layout.addWidget(self.sorted_list)

        self.winner_label = QLabel("")
        self.winner_label.setAlignment(Qt.AlignCenter)
        self.winner_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.winner_label)

        sort_btn = QPushButton("▶ Sort & Visualize")
        sort_btn.clicked.connect(self.start_sort_visualization)
        layout.addWidget(sort_btn)

        reset_btn = QPushButton("↺ Reset All")
        reset_btn.clicked.connect(self.reset_all)
        reset_btn.setStyleSheet("background-color: #4D1717; color: white;")
        layout.addWidget(reset_btn)

        self.setLayout(layout)
        self.setMinimumHeight(600)
        self.setMinimumWidth(600)
        self.apply_styles()

    def start_sort_visualization(self):
        if not self.data:
            return

        self.name_list, self.amounts = zip(*self.data)
        self.name_list = list(self.name_list)
        self.amounts = list(self.amounts)

        self.run_cpp_timings()

        self.index = 0
        self.subindex = 0
        self.min_index = 0

        self.timer = QTimer()
        selected = self.sort_selector.currentText()

        if selected == "Bubble Sort":
            self.timer.timeout.connect(self.bubble_sort_step)
        else:
            self.timer.timeout.connect(self.selection_sort_step)

        self.timer.start(150)

    def bubble_sort_step(self):
        n = len(self.amounts)
        if self.index < n - 1:
            if self.subindex < n - self.index - 1:
                if self.amounts[self.subindex] > self.amounts[self.subindex + 1]:
                    self.amounts[self.subindex], self.amounts[self.subindex + 1] = \
                        self.amounts[self.subindex + 1], self.amounts[self.subindex]
                    self.name_list[self.subindex], self.name_list[self.subindex + 1] = \
                        self.name_list[self.subindex + 1], self.name_list[self.subindex]
                self.subindex += 1
            else:
                self.subindex = 0
                self.index += 1
            self.update_visual()
        else:
            self.timer.stop()

    def selection_sort_step(self):
        n = len(self.amounts)
        if self.index < n - 1:
            if self.subindex == self.index:
                self.min_index = self.index

            if self.subindex < n:
                if self.amounts[self.subindex] < self.amounts[self.min_index]:
                    self.min_index = self.subindex
                self.subindex += 1
            else:
                if self.min_index != self.index:
                    self.amounts[self.index], self.amounts[self.min_index] = \
                        self.amounts[self.min_index], self.amounts[self.index]
                    self.name_list[self.index], self.name_list[self.min_index] = \
                        self.name_list[self.min_index], self.name_list[self.index]
                self.index += 1
                self.subindex = self.index
            self.update_visual()
        else:
            self.timer.stop()

    def update_visual(self):
        self.sorted_list.clear()
        selected = self.sort_selector.currentText()

        for i, (name, amt) in enumerate(zip(self.name_list, self.amounts)):
            item = QListWidgetItem(f"{name} - ${amt:.2f}")

            if selected == "Bubble Sort":
                # Highlight compared pair in yellow
                if i == self.subindex or i == self.subindex + 1:
                    item.setBackground(QColor("#FFF176"))  # Yellow
            elif selected == "Selection Sort":
                # Green = current minimum, Yellow = being scanned
                if i == self.min_index:
                    item.setBackground(QColor("#81C784"))  # Green
                elif i == self.subindex:
                    item.setBackground(QColor("#FFF176"))  # Yellow

            self.sorted_list.addItem(item)

    def run_cpp_timings(self):
        n = len(self.amounts)
        arr1 = (c_double * n)(*self.amounts)
        arr2 = (c_double * n)(*self.amounts)
        time1 = c_double()
        time2 = c_double()

        lib.bubble_sort(arr1, c_int(n), ctypes.byref(time1))
        lib.selection_sort(arr2, c_int(n), ctypes.byref(time2))

        self.bubble_label.setText(f"Bubble Sort Time (C++): {time1.value:.3f} ms")
        self.selection_label.setText(f"Selection Sort Time (C++): {time2.value:.3f} ms")

        if abs(time1.value - time2.value) < 0.0001:
            self.winner_label.setText("⏱ Both algorithms performed equally fast.")
        elif time1.value < time2.value:
            self.winner_label.setText("✅ Bubble Sort is faster.")
        else:
            self.winner_label.setText("✅ Selection Sort is faster.")

        self.sorted_bubble = list(arr1)
        self.sorted_selection = list(arr2)

    def reset_all(self):
        self.data.clear()
        self.sorted_list.clear()
        self.bubble_label.setText("Bubble Sort Time: N/A")
        self.selection_label.setText("Selection Sort Time: N/A")
        self.winner_label.setText("")
        self.name_list = []
        self.amounts = []
        self.index = 0
        self.subindex = 0
        self.sorted_bubble = []
        self.sorted_selection = []
        if self.page_one_ref:
            self.page_one_ref.clear_list()
        self.stacked_widget.setCurrentIndex(0)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ECECEC, stop:1 #D6D6D6);
                color: #1C1C1C;
            }
            QPushButton {
                background-color: #174D38;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1f6b50;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #aaa;
                font-size: 13px;
            }
            QComboBox {
                padding: 6px;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
        """)




class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💰 Expense Sorter")
        self.resize(640, 640)

        self.data = []
        self.stacked_widget = QStackedWidget()

        self.page1 = PageOne(self.stacked_widget, self.data)
        self.page2 = PageTwo(self.stacked_widget, self.data)

        self.page1.page_two_ref = self.page2
        self.page2.page_one_ref = self.page1

        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
