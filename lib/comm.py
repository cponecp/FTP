'''
该模块提供一系列工具方法
'''
import hashlib
import json
import struct
import configparser
import sys


# 从配置文件取参数
def auth(section, thing):
    config = configparser.ConfigParser()
    config.read(r'conf/config.ini')
    val = config.get(section, thing)
    return val


def hash_str(cont):
    md = hashlib.md5()
    md.update(cont.encode('utf8'))
    return md.hexdigest()


# 针对大文件采用多点hash
def hash_file(dir_path, size):
    m = hashlib.md5()
    with open(dir_path, 'rb') as f:
        if size > 9999:
            part = size // 9
            for i in range(1, 10):
                f.seek(part * i, 0)
                m.update(f.read(5))
        else:
            m.update(f.read())
    return m.hexdigest()


def head_dic_send(self, dic):
    head_json = json.dumps(dic)
    head_json_bytes = bytes(head_json, encoding=self.coding)
    head_struct = struct.pack('i', len(head_json_bytes))

    if hasattr(self, 'request'):
        self.request.send(head_struct)
        self.request.send(head_json_bytes)
    else:
        self.socket.send(head_struct)
        self.socket.send(head_json_bytes)

    return 1


def head_dic_unpack(self):
    if hasattr(self, 'request'):
        head_struct = self.request.recv(4)
    else:
        head_struct = self.socket.recv(4)
    if not head_struct: return -1

    head_len = struct.unpack('i', head_struct)[0]
    if hasattr(self, 'request'):
        head_json = self.request.recv(head_len).decode(self.coding)
    else:
        head_json = self.socket.recv(head_len).decode(self.coding)

    return json.loads(head_json)


def progress(percent, width=50):
    if percent >= 1:
        percent = 1
    show_str = ('[%%-%ds]' % width) % (int(width * percent) * '#')
    print('\r%s %d%%' % (show_str, int(100 * percent)), file=sys.stdout, flush=True, end='')


if __name__ == '__main__':
    pass
