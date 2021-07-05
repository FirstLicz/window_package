from PyQt5.QtWidgets import QWidget, QDesktopWidget, QCheckBox


class BaseWindows(QWidget):

    def __init__(self):
        super(BaseWindows, self).__init__()

    def center(self):
        pass


class CustomCheckBox(QCheckBox):

    def __init__(self, *__args):
        super(CustomCheckBox, self).__init__(*__args)

    def custom_style(self):
        self.setStyleSheet("""
        
        """)
