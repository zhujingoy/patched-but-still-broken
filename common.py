import sys
import getpass


def get_base_dir():
    user_name = getpass.getuser()
    if sys.platform == 'linux':
        base_dir = '/user_data'
    elif sys.platform == 'darwin':
        if user_name == 'zhouting':
            base_dir = '/Users/zhouting/data_for_2025_1024_game'
        else:
            base_dir = '/Users/chenyang/plot_domain_traffic_data'  # 宇飞改下
    if sys.platform.startswith('win'):
        base_dir = 'C://'  # 朱晶改下

    return base_dir
