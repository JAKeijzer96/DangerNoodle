import cx_Freeze
# pip install cx_freeze==6.1
# Version 6.2 crashes
# USAGE: python setup.py build
# Alternative: python setup.py bdist_msi
# The alternative also builds an installer instead of just a folder with the .exe


execs = [cx_Freeze.Executable("snake.py", base="Win32GUI")] # base= to not have a terminal appear
files = ["apple.png", "body.png", "Gasalt-Black.ttf", "head.png", "icon.png", "tail.png", "turn.png"]

# exclude unneeded packages to trim down file size
# There might be more unneeded packages that are not excluded right now, more research might be needed
cx_Freeze.setup(
        name="DangerNoodle",
        options={
        "build_exe": {
                "packages": ["pygame"],
                "excludes": ["concurrent", "email", "html", "http", "logging", "multiprocessing", "unittest", "numpy", "test", "tkinter", "urllib"],
                "include_files": files
                    }
                },
        description="DangerNoodle - A very original game by Jasper",
        executables = execs
        )