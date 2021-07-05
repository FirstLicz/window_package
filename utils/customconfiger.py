from configparser import ConfigParser


class CustomConfigParser(ConfigParser):

    def optionxform(self, optionstr):
        return optionstr
