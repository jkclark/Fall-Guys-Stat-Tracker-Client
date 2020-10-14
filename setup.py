from cx_Freeze import setup, Executable
setup(
    name = "FGStats_Client",
    version = "0.2.0",
    options = {
        "build_exe": {
            'packages': [
                'requests',
                'datetime',
                're',
                "os",
                "sys",
                'time',
                'typing',
                'vdf',
                'winreg',
                'requests',
            ],
            'include_msvcr': True,
        },
    },
    executables = [Executable("fgstats_client.py", base="Win32GUI")]
)
