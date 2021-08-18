import os
import platform

def get_refined_path(path):
    if platform.system() == 'Windows':
        refined_path = path.split('file:///')[1]
    elif platform.system() == 'Linux':
        refined_path = path.split('file://')[1]
    elif platform.system() == 'Darwin':
        refined_path = path.split('file://')[1]

    return refined_path

def set_save_folder(path, opt):
    if not os.path.exists(os.path.join(path, 'save')):
        os.mkdir(os.path.join(path, 'save'))
    save_path = os.path.join(path, 'save')

    if opt == 'stock_chart':
        if not os.path.exists(os.path.join(save_path, 'stock_chart')):
            os.mkdir(os.path.join(save_path, 'stock_chart'))
        save_path = os.path.join(save_path, 'stock_chart')
    elif opt == 'file_merge':
        if not os.path.exists(os.path.join(save_path, 'file_merge')):
            os.mkdir(os.path.join(save_path, 'file_merge'))
        save_path = os.path.join(save_path, 'file_merge')
    elif opt == 'order_create':
        if not os.path.exists(os.path.join(save_path, 'order_create')):
            os.mkdir(os.path.join(save_path, 'order_create'))
        save_path = os.path.join(save_path, 'order_create')
    elif opt == 'basic_backtest':
        if not os.path.exists(os.path.join(save_path, 'basic_backtest')):
            os.mkdir(os.path.join(save_path, 'basic_backtest'))
        save_path = os.path.join(save_path, 'basic_backtest')
    elif opt == 'label_backtest':
        if not os.path.exists(os.path.join(save_path, 'label_backtest')):
            os.mkdir(os.path.join(save_path, 'label_backtest'))
        save_path = os.path.join(save_path, 'label_backtest')
    elif opt == 'stock_filter':
        if not os.path.exists(os.path.join(save_path, 'stock_filter')):
            os.mkdir(os.path.join(save_path, 'stock_filter'))
        save_path = os.path.join(save_path, 'stock_filter')

    return save_path
