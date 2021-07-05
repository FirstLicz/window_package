from PyQt5.QtWidgets import QWidget, QDialog, QHBoxLayout, QVBoxLayout, QCheckBox, QPushButton, QLineEdit, \
    QDesktopWidget, QApplication, QFileDialog, QLabel, QFormLayout, QSpinBox
from PyQt5.QtCore import QThread, pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5 import QtCore, QtGui

import qtawesome as qtaw
import os

from conf import BASE_DIR
from utils.customconfiger import CustomConfigParser


class SshLoginWindow(QDialog):
    login_info = pyqtSignal(dict)

    def __init__(self, conf=None):
        super(SshLoginWindow, self).__init__()
        # 设置菜单栏
        self.config_ini_file = conf
        if self.config_ini_file and os.path.isfile(self.config_ini_file):
            conf = CustomConfigParser()
            try:
                conf.read(self.config_ini_file)
                self.conf_dict = conf._sections.get("ssh")
            except Exception:
                self.conf_dict = dict()
        else:
            self.conf_dict = dict()
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("ssh2连接配置")
        self.setWindowIcon(QtGui.QIcon(os.path.join(BASE_DIR, "static/icon/ssh.jpeg")))
        self.setFixedSize(300, 220)
        self.init_ui()
        self.init_style()
        self.show()

    def init_ui(self):
        # vbox
        vbox = QVBoxLayout()
        form_box = QFormLayout()
        self.host_line_edit = QLineEdit("", self)
        self.host_line_edit.setPlaceholderText("连接主机名")
        self.host_line_edit.setText(self.conf_dict.get("host", "192.168.1.82"))

        form_box.addRow(QLabel("主机"), self.host_line_edit)
        self.host_username_edit = QLineEdit("", self)
        self.host_username_edit.setPlaceholderText("用户名")
        self.host_username_edit.setText(self.conf_dict.get("username", "root"))

        form_box.addRow(QLabel("用户名"), self.host_username_edit)
        self.host_password_edit = QLineEdit("", self)
        self.host_password_edit.setEchoMode(QLineEdit.Password)
        self.host_password_edit.setPlaceholderText("密码")
        self.host_password_edit.setText(self.conf_dict.get("password", "Lcz123456"))
        form_box.addRow(QLabel("密码"), self.host_password_edit)
        # 端口
        self.host_port_edit = QSpinBox(self)
        self.host_port_edit.setRange(1, 2 ** 16 - 1)
        self.host_port_edit.setValue(int(self.conf_dict.get("port", 1022)))
        form_box.addRow(QLabel("端口"), self.host_port_edit)
        # 是否使用key
        hbox = QHBoxLayout()
        self.file_name_label = QLabel(self)
        self.file_name_label.setText(self.conf_dict.get("key_file", ""))
        select_button_icon = qtaw.icon("mdi.file-key")
        self.select_button = QPushButton(select_button_icon, "keyfile", self)
        self.select_button.clicked.connect(self.select_key_file)
        hbox.addWidget(self.select_button)
        hbox.addWidget(self.file_name_label)
        form_box.addRow(QLabel("key文件"), hbox)
        vbox.addLayout(form_box)
        hbox = QHBoxLayout()
        save_button = QPushButton(qtaw.icon("mdi.content-save-cog"), "保存配置")
        save_button.clicked.connect(self.save_conf)
        cancel_button = QPushButton(qtaw.icon("mdi.file-cancel"), "取消")
        cancel_button.clicked.connect(self.close)
        hbox.addStretch()
        hbox.addWidget(save_button)
        hbox.addWidget(cancel_button)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.center()

    def select_key_file(self):
        filename, file_type = QFileDialog().getOpenFileName(self, "选择keyfile", os.getcwd())
        print(filename, file_type)
        self.file_name_label.setText(os.path.basename(filename))
        self.conf_dict["key_file"] = filename

    def save_conf(self):
        user_dir = os.environ.get("userprofile")
        # print(user_dir)
        self.conf_dict["host"] = self.host_line_edit.text()
        self.conf_dict["username"] = self.host_username_edit.text()
        self.conf_dict["password"] = self.host_password_edit.text()
        self.conf_dict["port"] = self.host_port_edit.value()
        self.login_info.emit(self.conf_dict)

    def init_style(self):
        pass

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = SshLoginWindow(conf=os.path.join(BASE_DIR, "conf.ini"))
    sys.exit(app.exec_())
