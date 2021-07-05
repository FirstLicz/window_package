import os
import shutil
import tarfile
from pathlib import Path


class WebTerminal:

    def __init__(self):
        self.root_path = "/app"
        self.path = "somp-webterminal"
        self.copy_list = [
            'centos7_online_requirements.txt',
            'common',
            'elfinder',
            'fronted',
            'locale',
            'permission',
            'plugins',
            'static',
            'templates',
            'webterminal',
            'guacamole',
            'docker-entrypoint.sh',
            'nginx.conf',
            'supervisord.conf',
            'initdb.py',
            'config.ini',
            'manage.py',
            'Dockerfile',
            'centos7_install_online.sh',
            'centos7_start.sh',
            'centos7_stop.sh',
        ]
        self.target_path = "/opt"
        self.error_list = list()
        self.success_list = list()

    def copy(self):
        copy_path = os.path.join(self.root_path, self.path)
        if os.path.isdir(copy_path):
            target_path = os.path.join(self.target_path, self.path)
            # shutil.rmtree(target_path, ignore_errors=True)  # 无脑删除
            os.makedirs(target_path, exist_ok=True)  # 无脑创建
            for name in self.copy_list:
                path_name = os.path.join(copy_path, name)
                if os.path.isdir(path_name):
                    shutil.rmtree(os.path.join(target_path, name), ignore_errors=True)
                    shutil.copytree(path_name, os.path.join(target_path, name), symlinks=True,
                                    ignore=shutil.ignore_patterns("*.pyc"))
                    self.success_list.append(path_name)
                elif os.path.isfile(path_name):
                    shutil.copy2(path_name, target_path)
                    self.success_list.append(path_name)
                else:
                    print(f"unknown error name: {path_name}")
                    self.error_list.append(path_name)
            return True
        else:
            print(f"The copy path {copy_path} does not exist")
            return False

    def zip_folder(self):
        target_folder = os.path.join(self.target_path, self.path)
        target_file = os.path.join(self.target_path, f"{self.path.replace('-', '_')}.tar.gz")
        if os.path.isfile(target_file):
            os.remove(target_file)
        f = tarfile.open(target_file, 'w:gz')
        for file in Path(target_folder).rglob('*'):
            if file.name.endswith(".sh"):
                execute_flag = os.system(f"dos2unix {file}")
            f.add(file, arcname=str(file.absolute())[len(self.target_path):])
        f.close()
        return True


class WebTerminalDb(WebTerminal):

    def __init__(self):
        super(WebTerminalDb, self).__init__()
        self.path = "somp-webterminaldb"
        self.copy_list = [
            'requirements.txt',
            'OmniDB',
            'OmniDB_app',
            'utils',
            'config.ini',
            'docker-entrypoint.sh',
            'gunicorn_config.py',
            'initdb.py',
            'manage.py',
            'Dockerfile',
            'centos7_install_online.sh',
            'centos7_start.sh',
            'centos7_stop.sh',
        ]


def install_package(name):
    if name == "terminal":
        terminal = WebTerminal()
        flag = terminal.copy()
        if flag:
            print(f"copy success")
            flag = terminal.zip_folder()
            if flag:
                print(f"gzip success")
    elif name == "db":
        terminal = WebTerminalDb()
        flag = terminal.copy()
        if flag:
            flag = terminal.zip_folder()
            if flag:
                print(f"gzip success")
    else:
        print(f"parameter error")


if __name__ == '__main__':
    import sys

    install_package(name=sys.argv[1])
