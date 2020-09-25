import cx_Freeze
# pip install cx_freeze==6.1
# Version 6.2 crashes
# USAGE: python setup.py build
# Alternative: python setup.py bdist_msi
# The alternative also builds an installer instead of just a folder with the .exe


execs = [cx_Freeze.Executable("tutorial.py", base="Win32GUI")] # base= to not have a terminal appear

# exclude unneeded packages to trim down file size
# There might be more unneeded packages that are not excluded right now, more research might be needed
cx_Freeze.setup(
        name="Slither",
        options={
        "build_exe": {
                "packages": ["pygame"],
                "excludes": ["concurrent", "email", "html", "http", "logging", "multiprocessing", "unittest", "numpy", "test", "tkinter", "urllib"],
                "include_files": ["snakehead.png", "snaketail.png", "apple.png"]
                    }
                },
        description="Slither game tutorial",
        executables = execs
        )