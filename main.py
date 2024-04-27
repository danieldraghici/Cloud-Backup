import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QWidget,
    QMessageBox, QRadioButton, QButtonGroup, QHBoxLayout
)

from dropboxI import MyDropbox
from google_drive import MyDrive


def show_dialog(message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Backup Status")
    msg_box.setText(message)
    msg_box.exec_()


class BackupWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cloud-Backup Tool")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setWindowIcon(QIcon('icon.png'))
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title_label = QLabel("Cloudy")
        title_label.setStyleSheet("font-size: 40px; color: blue;margin-bottom:-100px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel("A backup tool")
        subtitle_label.setParent(title_label)
        subtitle_label.setStyleSheet("font-size: 16px; color: black;margin-top:-100px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        service_layout = QHBoxLayout()
        layout.addLayout(service_layout)

        service_label = QLabel("Select Service:")
        service_label.setStyleSheet("font-size: 20px;")
        service_layout.addWidget(service_label)

        service_container = QWidget()
        service_layout.addWidget(service_container)

        service_radio_layout = QVBoxLayout(service_container)

        self.service_group = QButtonGroup()

        self.service_google_radio = QRadioButton("Google Drive")
        self.service_google_radio.setStyleSheet("font-size: 16px;")
        self.service_group.addButton(self.service_google_radio)
        service_radio_layout.addWidget(self.service_google_radio)

        self.service_dropbox_radio = QRadioButton("Dropbox")
        self.service_dropbox_radio.setStyleSheet("font-size: 16px;")
        self.service_group.addButton(self.service_dropbox_radio)
        service_radio_layout.addWidget(self.service_dropbox_radio)

        folder_layout = QHBoxLayout()
        layout.addLayout(folder_layout)
        folder_layout.setContentsMargins(0, 0, 0, 0)

        folder_label = QLabel("Enter Folder Name:")
        folder_label.setStyleSheet("font-size: 20px;")
        folder_layout.addWidget(folder_label)

        self.folder_name_entry = QLineEdit()
        folder_layout.addWidget(self.folder_name_entry)

        directory_button = QPushButton("Backup Directory")
        directory_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 10px 20px;"
                                       "text-align: center; text-decoration: none; display: inline-block; font-size: "
                                       "16px;")
        directory_button.clicked.connect(self.handle_directory_selection)
        layout.addWidget(directory_button)

        file_button = QPushButton("Backup Single File")
        file_button.setStyleSheet("background-color: #008CBA; color: white; border: none; padding: 10px 20px;"
                                  "text-align: center; text-decoration: none; display: inline-block; font-size: 16px;")
        file_button.clicked.connect(self.handle_file_selection)
        layout.addWidget(file_button)

        layout.setSpacing(10)

        self.drive = None
        self.dropbox = None

    def handle_directory_selection(self):
        folder_name = self.folder_name_entry.text()
        if folder_name:
            if self.service_google_radio.isChecked():
                if not self.drive:
                    self.drive = MyDrive()
                directory = QFileDialog.getExistingDirectory(None, "Select Directory to Backup")
                if directory:
                    self.drive.select_directory(folder_name)
                    show_dialog("Backup Complete")
            elif self.service_dropbox_radio.isChecked():
                if not self.dropbox:
                    self.dropbox = MyDropbox("YOUR_APP_KEY", "YOUR_APP_SECRET")
                directory = QFileDialog.getExistingDirectory(None, "Select Directory to Backup")
                if directory:
                    self.dropbox.upload_directory(directory, f"/{folder_name}")
                    show_dialog("Backup Complete")

    def handle_file_selection(self):
        folder_name = self.folder_name_entry.text()
        if folder_name:
            if self.service_google_radio.isChecked():
                if not self.drive:
                    self.drive = MyDrive()
                file_path = QFileDialog.getOpenFileName(None, "Select File to Backup", "", "All Files (*.*);;")
                if file_path:
                    self.drive.select_file(folder_name)
                    show_dialog("Backup Complete")
            elif self.service_dropbox_radio.isChecked():
                if not self.dropbox:
                    self.dropbox = MyDropbox("YOUR_APP_KEY", "YOUR_APP_SECRET")
                file_path = QFileDialog.getOpenFileName(None, "Select File to Backup", "", "All Files (*.*);;")
                print(file_path)
                if file_path:
                    self.dropbox.upload_file(file_path, f"/{folder_name}/{os.path.basename(file_path)}")
                    show_dialog("Backup Complete")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BackupWindow()
    window.show()
    sys.exit(app.exec_())
