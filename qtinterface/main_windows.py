from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QMainWindow, QAction, QComboBox, QHBoxLayout, \
    QVBoxLayout, QPushButton
from PyQt5 import QtGui, QtCore

import os
import logging

from conf import BASE_DIR
from qtinterface.login_windows import SshLoginWindow
from qtinterface.sftp_windows import SelectPackageHostWindows
from utils.customconfiger import CustomConfigParser

logger = logging.getLogger("package")


class MainWindows(QMainWindow):

    def __init__(self):
        super(MainWindows, self).__init__()
        self.setWindowTitle("打包客户端")
        self.setWindowIcon(QtGui.QIcon(os.path.join(BASE_DIR, "static/icon/package.jpeg")))
        self.software_dir = os.path.join(os.environ.get("userprofile"), "somp_package")
        self.conf_file = os.path.join(self.software_dir, "conf.ini")
        os.makedirs(self.software_dir, exist_ok=True)
        self.init_ui()
        self.init_style()
        self.show()

    def init_ui(self):
        self.setMinimumWidth(700)
        self.setMinimumHeight(440)
        # 菜单栏
        file_menu = self.menuBar().addMenu("文件")
        ssh_conf_action = QAction("配置ssh", self)
        file_menu.addAction(ssh_conf_action)
        ssh_conf_action.triggered.connect(self.ssh_conf)
        # 选择打包机器
        select_widget = SelectPackageHostWindows(conf_file=self.conf_file)
        self.setCentralWidget(select_widget)

    def init_style(self):
        pass

    def ssh_conf(self):
        self.ssh_interface = SshLoginWindow(conf=self.conf_file)
        self.ssh_interface.login_info.connect(lambda data: self.save_ssh_conf(data))
        self.ssh_interface.exec_()

    def save_ssh_conf(self, data):
        logger.debug(data)
        conf = CustomConfigParser()
        conf.read(self.conf_file)
        ssh_list = list(filter(lambda x: x.startswith("ssh"), conf.sections()))
        try:
            if ssh_list:
                ssh_list.sort()
                logger.debug(f"ssh list = {ssh_list}")
                try:
                    ssh_index = 0
                    for section in ssh_list:
                        tmp = conf._sections.get(section)
                        logger.debug(f"{tmp}")
                        if tmp.get("host") == data.get("host"):
                            ssh_index = section[3:]
                            if ssh_index != "":
                                ssh_index = int(ssh_index)
                            break
                        if ssh_index != 0:
                            break
                    logger.info(f"ssh index {ssh_index}")
                    if ssh_index == 0:
                        ssh_index = int(ssh_list[-1][3:])
                        ssh_index += 1
                except ValueError:
                    ssh_index = 1
            else:
                ssh_index = ""
            logger.info(f"ssh conf {ssh_index}")
            if f"ssh{ssh_index}" not in conf.sections():
                conf.add_section(f"ssh{ssh_index}")
            for k, v in data.items():
                conf.set(f"ssh{ssh_index}", k, value=str(v))
            with open(self.conf_file, 'w') as f:
                conf.write(f)
            self.ssh_interface.close()
        except Exception as e:
            logger.exception(e)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = MainWindows()
    sys.exit(app.exec_())
