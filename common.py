import os
import sys
import getpass


def get_base_dir():
    user_name = getpass.getuser()
    if sys.platform == 'linux':
        base_dir = '/user_data'
    elif sys.platform == 'darwin':
        if user_name == 'zhouting':
            base_dir = '/Users/zhouting/data_for_2025_1024_game'
        elif user_name == 'lyf':
            base_dir = '/Users/lyf/data_for_2025_1024_game'  # 宇飞改下
    if sys.platform.startswith('win'):
        base_dir = 'C://data_for_2025_1024_game'  # 朱晶改下

    os.makedirs(base_dir, exist_ok=True)
    return base_dir
