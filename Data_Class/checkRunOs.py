import platform
import getpass



def get_os_name():
    os_name = platform.system()
    if os_name == 'Windows':
        return 'Windows'
    elif os_name == 'Darwin':
        return 'MacOS'
    elif os_name == 'Linux':
        return 'Linux'
    else:
        return 'Unknown'

def get_username()->str:
    """
    Returns the username of the current user depending on the operating system.
    """
    if platform.system() == 'Windows':
        return getpass.getuser()
    elif platform.system() == 'Darwin':  # MacOS
        return getpass.getuser()
    else:
        return None  # unsupported platform