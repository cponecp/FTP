'''
该模块提供一系列工具方法
'''
import hashlib
import json
import struct
import configparser
import sys

STATUS_CODE = {
    250: "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251: "Invalid cmd ",
    252: "Invalid auth data",
    253: "Wrong username or password",
    254: "Passed authentication",
    255: "Filename doesn't provided",
    256: "File doesn't exist on server",
    257: "ready to send file",
    258: "md5 verification",
    800: "the file exist,but not enough ,is continue? ",
    801: "the file exist !",
    802: " ready to receive datas",
    900: "md5 valdate success"
}

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

    self.socket.send(head_struct)
    self.socket.send(head_json_bytes)

    return 1


def head_dic_unpack(self):
    head_struct = self.socket.recv(4)
    if not head_struct: return -1

    head_len = struct.unpack('i', head_struct)[0]
    head_json = self.socket.recv(head_len).decode(self.coding)

    return json.loads(head_json)


def progress(percent, width=50):
    if percent >= 1:
        percent = 1
    show_str = ('[%%-%ds]' % width) % (int(width * percent) * '#')
    print('\r%s %d%%' % (show_str, int(100 * percent)), file=sys.stdout, flush=True, end='')


if __name__ == '__main__':
    pass
