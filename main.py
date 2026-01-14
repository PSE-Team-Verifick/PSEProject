# This is a sample Python script.
import sys

from PySide6.QtWidgets import QApplication

from view.base_view.main_window import MainWindow


# Press Strg+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press F9 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()

    sys.exit(app.exec())


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
