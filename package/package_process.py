from .ssh_action import SShConnectObject
from utils.customconfiger import CustomConfigParser


class PackageProcess(object):

    def __init__(
            self, host=None, port=22, username=None, password=None, private_key_file=None,
            init_conf=None,
    ):
        pass

    def init_package_list(self):
        pass

    def git_pull(self):
        pass

    def git_checkout(self):
        pass

    def copy_file(self):
        pass

    def zip_folder(self):
        pass

    def download_file(self):
        pass




