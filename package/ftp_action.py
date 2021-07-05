from ftplib import FTP, error_perm
import os
import stat
import logging

logger = logging.getLogger("")


class FtpConnect(object):

    def __init__(self, host="", user="", passwd=""):
        super(FtpConnect, self).__init__()
        FTP.encoding = "UTF-8"
        self.ftp = FTP(host=host, user=user, passwd=passwd, timeout=3)
        self.data_list = list()

    def upload(self, local_path, remote_path):
        try:
            self.create_remote_dir(os.path.dirname(remote_path))
            base_name = os.path.basename(remote_path)
            with open(local_path, 'rb') as fp:
                self.ftp.storbinary(f'STOR {base_name}', fp)    # 文件名、切换到工作目录中
                self.ftp.set_debuglevel(0)
            return remote_path
        except error_perm:
            return

    def download(self, local_path, remote_path):
        # 从ftp下载文件
        with open(local_path, 'wb') as fp:
            self.ftp.retrbinary(f'RETR {remote_path}', fp.write)
            self.ftp.set_debuglevel(0)
        return local_path

    def repeating_remote_path(self, remote_path, fd):
        self.ftp.retrbinary(f'RETR {remote_path}', fd.write)
        self.ftp.set_debuglevel(0)

    def list_dir(self, remote_path=""):
        _list_dir = list()
        self.ftp.dir(remote_path, _list_dir.append)
        return _list_dir

    def remote_dir_list(self, remote_path=""):
        list_dir = list()
        for elem in self.list_dir(remote_path):
            data = {}
            tmp_data = elem.split(" ")
            if elem[0] == "d":
                data["is_dir"] = True
                data["size"] = None
            else:
                data["is_dir"] = False
                data["size"] = tmp_data[-5]
            data["name"] = tmp_data[-1]
            list_dir.append(data)
        return list_dir

    def create_remote_dir(self, remote_dir):
        try:
            self.ftp.cwd(remote_dir)
        except error_perm:
            self.data_list = []
            self.get_dir_list(remote_dir)
            print(self.data_list)
            for elem in self.data_list:
                try:
                    self.ftp.mkd(elem)
                except error_perm:
                    pass
                self.ftp.cwd(elem)

    def get_dir_list(self, path):
        if not path:
            return
        if os.path.dirname(path) == path:
            self.data_list.insert(0, path)
            return self.data_list
        else:
            base_name = os.path.basename(path)
            self.data_list.insert(0, base_name)
            self.get_dir_list(os.path.dirname(path))

    def __del__(self):
        self.ftp.quit()  # 关闭ftp 连接
        self.ftp.close()  # 单方面关闭


if __name__ == '__main__':
    ftp = FtpConnect(host="192.168.6.191", user="admin", passwd="123456")
    # ret = ftp.upload(r"F:\msdia80.dll", r"aaab\msdia80.dll")
    # print(ret)
    dir_list = ftp.remote_dir_list("")
    print(dir_list)
    # #
    # print(ftp.ftp.nlst())
    # ret = ftp.create_remote_dir("bwda-lcz/192.168.6.191/2021-6-19/")
    # print(ret)
    # s = '-rwxrwxrwx    1 ftp      ftp          8410 May 27 08:27 webterminal_note.txt'
    # print(s.split(" "))
