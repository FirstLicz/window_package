import paramiko
import stat
import logging
import os
from pathlib import Path

logger = logging.getLogger("package")


class SShConnectObject:
    def __init__(self, host=None, port=22, username=None, password=None, private_key_file=None):
        self.ssh_client = paramiko.SSHClient()  # 实例化
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)  # 设置自动添加到主机信任列表
        try:
            if password:
                self.ssh_client.connect(host, port=port, username=username, password=password)
                # sftp
                # self.transport = paramiko.Transport((host, port))
                # self.transport.connect(username=username, password=password)
            elif private_key_file:
                private = paramiko.RSAKey.from_private_key_file(private_key_file)
                self.ssh_client.connect(host, port=port, username=username, password=password, pkey=private)
            else:
                raise ValueError('参数错误')
        except paramiko.AuthenticationException:
            raise ValueError('用户或密码错误')
        self.data_list = []
        self.sftp = self.ssh_client.open_sftp()

    def execute_cmd(self, cmd=None):
        # 打开一个Channel并执行命令
        # stdout 为正确输出，stderr为错误输出，同时是有1个变量有值
        if cmd and isinstance(cmd, str):
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
            # 打印执行结果
            return stderr.read().decode('utf-8') + stdout.read().decode('utf-8')
        return ""

    def upload(self, local_path, remote_path):
        logger.info(f"remote path = {remote_path}")
        try:
            self.create_remote_dir(remote_path)
            self.sftp.put(local_path, remote_path)
        except Exception as e:
            logger.exception(e)
            return False
        return True

    def create_remote_dir(self, remote_dir):
        path_list = remote_dir.split("/")
        if not path_list:
            path_list = remote_dir.split("\\")
        if not path_list:
            return
        root_path = "/"
        for index, elem in enumerate(path_list):
            if index == 0:
                if elem:
                    root_path = path_list[0]
            if index > 1:
                path = Path(root_path, Path(*path_list[1:index]).as_posix()).as_posix()
            elif index > 0:
                path = Path(root_path, path_list[1]).as_posix()
            else:
                path = root_path
            try:
                self.sftp.chdir(path)
            except FileNotFoundError:
                self.sftp.mkdir(path)

    def chdir(self, remote_path):
        try:
            self.sftp.chdir(os.path.dirname(remote_path))
        except FileNotFoundError:
            self.sftp.mkdir(os.path.dirname(remote_path))

    def exist_dir(self, remote_dir):
        try:
            self.sftp.chdir(remote_dir)
        except FileNotFoundError:
            return False
        return True

    def _open(self, remote_path):
        return self.sftp.open(remote_path, "rb")

    def download(self, remote_path, local_path):
        try:
            self.sftp.get(remote_path, local_path)
        except Exception as e:
            logger.exception(e)
            return False
        return True

    def listdir(self, remote_path):
        try:
            result = self.sftp.listdir_attr(remote_path)
        except Exception:
            return
        return result

    def dir_list(self, remote_path):
        _dir_list = list()
        for elem in self.listdir(remote_path):
            ret = stat.S_ISDIR(elem.st_mode)
            if ret:
                _dir_list.append(elem.filename)
        return _dir_list

    def close(self):
        if hasattr(self, "_sftp"):
            self.sftp.close()
        self.ssh_client.close()

    def __del__(self):
        # if hasattr(self, "_sftp"):
        #     self.sftp.close()
        self.ssh_client.close()


if __name__ == '__main__':
    ssh = SShConnectObject(
        host="192.168.1.82",
        username="root",
        password="Lcz123456",
        port=1022,
    )
    # result = ssh.execute_cmd("df -h")
    # print(result)
    print(dir(ssh.sftp))
    print(ssh.dir_list("/"))
    from conf import BASE_DIR
    # fd = ssh._open("/opt/192.168.6.191.crt")
    # local_path = os.path.join(BASE_DIR, "test", "s_io.py")
    # with open(local_path, "wb") as f:
    #     f.write(fd.read())
    # ssh.sftp.chdir("/lczd")
    # ssh.upload(local_path, "/lczd/ddd/sss/s_io.py")
    # ssh.create_remote_dir("/lcz/dad/aaa")
    while True:
        cmd = input("cmd = ")
        ret = ssh.execute_cmd(f"{cmd}")
        print(ret)
    ssh.close()


