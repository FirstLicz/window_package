import os
import sys
from pathlib import Path


def rename(path=None):
    if path and os.path.isdir(path):
        for elem in Path(path).rglob("*.py"):
            if os.path.basename(elem) == "__init__.py" or \
                    elem.name == os.path.basename(__file__) or \
                    elem.name == "manager.py" or elem.parent == "test":
                continue
            # 将.py文件重命名为.pyx'
            old_name = Path(os.getcwd(), elem.absolute()).absolute()
            new_name = f"{old_name}x"
            if os.path.isfile(new_name):
                os.remove(new_name)
            if os.path.isfile(f"{old_name}d"):
                os.remove(f"{old_name}d")
            os.rename(old_name, new_name)
            # 执行 easycython *.pyx
            print(f"cd {old_name.parent} && easycython {new_name}")
            os.system(f"cd {old_name.parent} && easycython {new_name}")
            if os.path.isfile(f"{old_name.__str__()[:-3]}.cp36-win32.pyd"):
                os.rename(f"{old_name.__str__()[:-3]}.cp36-win32.pyd", f"{old_name.__str__()[:-3]}.pyd")
                os.remove(f"{old_name.__str__()[:-3]}.c")
                os.remove(f"{old_name.__str__()[:-3]}.html")
                os.remove(f"{old_name.__str__()[:-3]}.pyx")
        return True
    return False


def test():
    for elem in Path(".").rglob("*.py"):
        if elem.name == "config.py":
            old_name = Path(os.getcwd(), elem.as_posix()).absolute()
            print(old_name, old_name.parent)


if __name__ == '__main__':
    rename(".")
