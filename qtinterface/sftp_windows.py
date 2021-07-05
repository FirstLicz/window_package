from PyQt5 import QtGui, QtCore, QtWidgets
import qtawesome as qta
from pathlib import Path

import logging
import time
import os

from utils.customconfiger import CustomConfigParser
from conf.config import UNIT_TEST
from package.ssh_action import SShConnectObject
from conf import BASE_DIR

logger = logging.getLogger("package")


def get_time_now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


class SelectPackageHostWindows(QtWidgets.QWidget):
    """
        打包界面配置
    """
    login_info = QtCore.pyqtSignal(dict)

    def __init__(self, conf_file=None):
        super(SelectPackageHostWindows, self).__init__()
        self.conf_file = conf_file
        self.user_dir = os.environ.get("userprofile")
        self.init_ui()
        self.select_index = 0
        if UNIT_TEST:
            self.show()

    def init_ui(self):
        vbox = QtWidgets.QVBoxLayout()
        gbox = QtWidgets.QGridLayout()
        self.package_host_combox = QtWidgets.QComboBox()
        title_list, self.conf_list = self.load_conf()
        logger.info(f"title list = {title_list}")
        self.package_host_combox.addItems(title_list)
        self.package_host_combox.currentIndexChanged.connect(
            lambda: self.changed_index(self.package_host_combox.currentIndex()))
        gbox.addWidget(self.package_host_combox, 0, 0)
        # 项目路径列表
        self.branch_name = QtWidgets.QComboBox()
        self.branch_name.addItems(["master", "dev"])
        self.branch_name.setCurrentIndex(0)
        gbox.addWidget(self.branch_name, 0, 1)
        # 是否发布脚本文件到ssh 主机上
        self.branch_name = QtWidgets.QComboBox()
        self.branch_name.addItems(["master", "dev"])
        self.branch_name.setCurrentIndex(0)
        gbox.addWidget(self.branch_name, 0, 1)
        # 是否发布脚本文件到ssh 主机上
        self.upload_script = QtWidgets.QCheckBox("打包脚本", self)
        self.upload_script.setIcon(QtGui.QIcon(qta.icon("fa.cloud-upload", color='blue', )))
        self.upload_script.setChecked(True)
        gbox.addWidget(self.upload_script, 0, 2)
        # 开始打包
        self.package_btn = QtWidgets.QPushButton("打包", self)
        self.package_btn.setIcon(qta.icon("ei.play-alt", color="red", color_active='orange'))
        self.package_btn.clicked.connect(self.package_run)
        # 占多个列, 1 行 2 列
        gbox.addWidget(self.package_btn, 0, 3, 1, 2)
        # hbox.setAlignment(QtCore.Qt.AlignCenter) # 居中
        vbox.addLayout(gbox)
        # 增加 sftp 输出 文件路径
        hbox = QtWidgets.QHBoxLayout()
        lable = QtWidgets.QLabel("导出目录：")
        self.open_disk_dir_btn = QtWidgets.QPushButton(qta.icon("fa.folder-open", color="green"), "打开文件路径", self)
        self.open_disk_dir_btn.clicked.connect(lambda: os.startfile(self.export_path_line.text()))
        self.export_path_line = QtWidgets.QLineEdit(self.user_dir, self)
        self.export_path_line.setMinimumSize(400, 24)
        self.select_dir = QtWidgets.QPushButton(
            qta.icon('fa.folder-open', color='blue'), "选择目录",
            self)
        self.select_dir.clicked.connect(self.set_export_dir)
        hbox.addWidget(lable)
        hbox.addWidget(self.open_disk_dir_btn)
        hbox.addWidget(self.export_path_line)
        hbox.addWidget(self.select_dir)
        vbox.addLayout(hbox)
        # display area
        self.display_log = QtWidgets.QTextEdit("", self)
        self.display_log.setReadOnly(True)
        # 进度条
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setValue(0)
        vbox.addWidget(self.progress_bar)
        vbox.addWidget(self.display_log)
        self.setLayout(vbox)

    def package_run(self):
        # 调用执行命令
        if self.conf_list:
            # 禁用按钮
            self.progress_bar.setValue(0)
            self.package_host_combox.setDisabled(True)
            self.upload_script.setDisabled(True)
            self.package_btn.setEnabled(False)
            self.branch_name.setEnabled(False)
            self.export_path_line.setEnabled(False)
            self.select_dir.setEnabled(False)
            self.open_disk_dir_btn.setEnabled(False)
            conn_info = dict(self.conf_list[self.select_index])
            logger.info(f"conn_info = {conn_info}")
            self.job_thread = SshInteractiveThread(self, conn_info=conn_info,
                                                   branch_name=self.branch_name.currentText(),
                                                   export_dir=self.export_path_line.text())
            logger.debug(f"thread id = {self.job_thread.currentThread()}")
            self.job_thread.output.connect(lambda x: self.show_package_content(x))
            self.job_thread.rate_of_progress.connect(lambda x: self.show_package_progress(x))
            self.job_thread.start()
        else:
            self.display_log.append("没有配置ssh连接参数")

    def show_package_content(self, message):
        self.display_log.append(message)

    def show_package_progress(self, value):
        logger.info(f"progress value = {value}")
        if value == 100:
            self.progress_bar.setValue(100)
            self.package_host_combox.setDisabled(False)
            self.upload_script.setDisabled(False)
            self.package_btn.setEnabled(True)
            self.branch_name.setEnabled(True)
            self.export_path_line.setEnabled(True)
            self.select_dir.setEnabled(True)
            self.open_disk_dir_btn.setEnabled(True)
        else:
            self.progress_bar.setValue(value)

    def changed_index(self, x):
        logger.info(f"data = {self.conf_list[x]}")
        self.select_index = x
        # self.login_info.emit(self.conf_list[x])

    def load_conf(self):
        conf = CustomConfigParser()
        conf.read(self.conf_file)
        data_list = list()
        title_list = list()
        for section in conf.sections():
            data_list.append(conf._sections.get(section))
            if "port" in conf._sections.get(section).keys():
                conf._sections.get(section)["port"] = int(conf._sections.get(section).get("port"))
            title_list.append(conf._sections.get(section).get("host"))
        return title_list, data_list

    def set_export_dir(self):
        result = QtWidgets.QFileDialog().getExistingDirectory(self, "选取文件夹", os.getcwd())
        if result:
            self.export_path_line.setText(result)


class SshInteractiveThread(QtCore.QThread):
    """
        线程交换
    """
    output = QtCore.pyqtSignal(str)
    rate_of_progress = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, conn_info: dict = None, branch_name="dev", export_dir=None):
        super(SshInteractiveThread, self).__init__(parent)
        self.conn_info = conn_info
        self.branch_name = branch_name
        self.progress_value = 0  # 100
        self.program_path = "/app/test/tarpackage"
        if not export_dir:
            self.export_dir = os.environ.get("userprofile")
        else:
            self.export_dir = export_dir
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir, exist_ok=True)

    def run(self) -> None:
        try:
            if self.conn_info:
                self.conn_obj = SShConnectObject(**self.conn_info)
                clear_cmd = "rm -rf /opt/somp*"
                self.output.emit(f"{get_time_now()}-->清理旧数据:{clear_cmd}")
                self.conn_obj.execute_cmd(clear_cmd)
                # 上传打包脚本
                upload_flag = self.conn_obj.upload(Path(BASE_DIR, "bin", "tarpackage").__str__(), self.program_path)
                logger.info(f"upload result = {upload_flag}")
                if upload_flag:
                    self.output.emit("打包程序上传成功!")
                    self.progress_value += 10
                    self.rate_of_progress.emit(self.progress_value)
                else:
                    self.output.emit("打包程序上传失败!")
                    self.rate_of_progress.emit(100)
                    return
                # 给程序赋权
                chmod_cmd = f"chmod +x {self.program_path}"
                self.output.emit(chmod_cmd)
                self.progress_value += 5
                self.rate_of_progress.emit(self.progress_value)
                ret = self.conn_obj.execute_cmd(chmod_cmd)
                logger.debug(f"ret = {ret}")
                # 更新 webterminal git 代码     15
                project_dir_list = [
                    {
                        "path": "/app/somp-webterminal",
                        "xcmd": "terminal",
                        "generate_file": "/opt/somp_webterminal.tar.gz"
                    },
                    {
                        "path": "/app/somp-webterminaldb",
                        "xcmd": "db",
                        "generate_file": "/opt/somp_webterminaldb.tar.gz"
                    }
                ]
                update_code_value = 30 // (len(project_dir_list) * 5)
                # 占比 30 分
                for elem in project_dir_list:
                    cd_cmd = f"cd {elem.get('path')}"
                    self.progress_value += update_code_value
                    self.rate_of_progress.emit(self.progress_value)
                    # 切换分支
                    checkout_dev_cmd = f"{cd_cmd};git checkout {self.branch_name}"
                    logger.debug(f"checkout branch cmd {checkout_dev_cmd}")
                    self.output.emit(f"{get_time_now()}-->{checkout_dev_cmd}")
                    self.progress_value += update_code_value
                    self.rate_of_progress.emit(self.progress_value)
                    result = self.conn_obj.execute_cmd(checkout_dev_cmd)
                    self.output.emit(f"{get_time_now()}-->{result}")
                    logger.debug(f"checkout branch cmd result = {result}")
                    self.progress_value += update_code_value
                    self.rate_of_progress.emit(self.progress_value)
                    # 更新 项目 代码       20
                    git_pull_cmd = f"{cd_cmd};git pull"
                    logger.debug(f"branch name {self.branch_name} {git_pull_cmd}")
                    self.output.emit(f"{get_time_now()}-->{git_pull_cmd}")
                    self.progress_value += update_code_value
                    self.rate_of_progress.emit(self.progress_value)
                    result = self.conn_obj.execute_cmd(git_pull_cmd)
                    logger.debug(f"branch name {self.branch_name} pull result = {result}")
                    self.output.emit(f"{get_time_now()}-->{result}")
                    self.progress_value += update_code_value
                    self.rate_of_progress.emit(self.progress_value)
                update_code_value = 30 // (len(project_dir_list) * 3)
                for elem in project_dir_list:
                    # 执行 copy webterminal 程序    40
                    # 切换分支
                    package_cmd = f"{self.program_path} {elem.get('xcmd')}"
                    logger.debug(f"package cmd {package_cmd}")
                    self.output.emit(f"{get_time_now()}-->{package_cmd}")
                    self.progress_value += update_code_value
                    self.rate_of_progress.emit(self.progress_value)
                    result = self.conn_obj.execute_cmd(package_cmd)
                    self.output.emit(f"{get_time_now()}-->{result}")
                    logger.debug(f"checkout branch cmd result = {result}")
                    # 下载文件
                    self.output.emit(f"{get_time_now()}-->download file {elem.get('generate_file')}")
                    flag = self.conn_obj.download(
                        elem.get("generate_file"),
                        os.path.join(self.export_dir, os.path.basename(elem.get("generate_file")))
                    )
                    logger.info(f"download project {elem.get('generate_file')} archive result flag = {flag}")
                    self.output.emit(
                        f"{get_time_now()}-->download file {elem.get('generate_file')} "
                        f"result {'success' if flag else 'failed'}")
                    self.progress_value += update_code_value
                    self.rate_of_progress.emit(self.progress_value)
                # 执行 copy webterminaldb 程序  60
                # 执行成功后拷贝文件到本地路劲
                # 完成
                self.rate_of_progress.emit(100)
            else:
                self.output.emit("Packaging failure:参数错误")
        except Exception as e:
            logger.exception(e)
            logger.debug(f"{str(e)}")
            self.output.emit(f"Packaging failure: {str(e)}")
            self.rate_of_progress.emit(100)


if __name__ == '__main__':
    import sys

    UNIT_TEST = True
    app = QtWidgets.QApplication(sys.argv)
    ex = SelectPackageHostWindows(conf_file=r"C:\Users\Licz\somp_package\conf.ini")
    ret = Path(BASE_DIR, "package", "tarpackage.py").__str__()
    print(ret)
    sys.exit(app.exec_())
