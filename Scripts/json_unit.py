import json

# path = r"../Config/"
# filename = r"/settings.json"


def json_read(filepath):
    """
    json文件读取
    :param filepath: 文件位置
    :return: 返回读取字典
    """
    with open(filepath, 'r') as load_f:
        load_dict = json.load(load_f)
        # load_dict['d'] = [8200, {1: [['Python', 81], ['shirt', 300]]}]
        # print(json.dumps(load_dict, sort_keys=True, indent=4, separators=(',', ':')))
        return load_dict


def json_write(filepath, load_dict):
    """
    json文件写入
    :param filepath: 文件位置
    :param load_dict: 写入的信息
    :return:
    """
    with open(filepath, "w") as dump_f:
        json.dump(load_dict, dump_f, indent=4)
