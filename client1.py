import socket
import os
from lib import comm


class MYTCPClient:
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    allow_reuse_address = False
    max_packet_size = 8192
    coding = 'utf-8'
    request_queue_size = 5

    def __init__(self, server_address, connect=True):
        self.server_address = server_address
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        self.log_status = False
        if connect:
            try:
                self.client_connect()
                self.log_in()
            except Exception:
                self.client_close()
                raise

    def log_in(self):
        user_name = input('请输入您的用户名:').strip()
        password = input('请输入您的密码:').strip()
        hash_pass = comm.hash_str(password)
        user_dic = {'name': user_name,  'password': hash_pass}
        comm.head_dic_send(self, user_dic)

        res = self.socket.recv(40)
        if len(res) == 13:
            self.log_status = True
            print(res.decode(self.coding))
        else:
            print(res.decode(self.coding))

    def client_connect(self):
        self.socket.connect(self.server_address)

    def client_close(self):
        self.socket.close()

    def run(self):
            while True:
                if self.log_status:
                    inp = input(">>: ").strip()
                    if not inp: continue
                    if inp=='q':
                        self.client_close()
                        break
                    l = inp.split()
                    cmd = l[0]
                    if hasattr(self, cmd):
                        func = getattr(self, cmd)
                        func(l)
                else:
                    self.log_in()

    def put(self, args):
        cmd = args[0]
        filename = args[1]
        if not os.path.isfile(filename):
            print('file:%s is not exists' % filename)
            return
        else:
            filesize = os.path.getsize(filename)

        md_val = comm.hash_file(filename, filesize)
        head_dic = {'cmd': cmd, 'filename': os.path.basename(filename), 'fileSize': filesize, 'md5': md_val}
        res = comm.head_dic_send(self, head_dic)  # 第一次send
        print(res) # mark
        rev_dic = comm.head_dic_unpack(self)

        if rev_dic['is_full'] :
            print('空间不足')
        elif not rev_dic['is_exits']:
            send_size = 0
            with open(filename, 'rb') as f:
                for line in f:
                    self.socket.send(line)
                    send_size += len(line)
                    # 打印进度条
                    percent = send_size / filesize  # 接收的比例
                    comm.progress(percent, width=70)  # 进度条的宽度70
                else:
                    print('upload successful')
        # 文件已经存在当大小小于完整文件则 实现断点续传
        elif rev_dic['recv_size'] < filesize:
            send_size = rev_dic['recv_size']
            with open(filename, 'rb') as f:
                f.seek(send_size, 0)
                while f.tell() < filesize:
                    res = f.read(self.max_packet_size)
                    self.socket.send(res)
                    send_size += len(res)
                    # 打印进度条
                    percent = send_size / filesize  # 接收的比例
                    comm.progress(percent, width=70)  # 进度条的宽度70
                else:
                    print('upload successful')

    def show_list(self, args):
        cmd = args[0]
        head_dic = {'cmd': cmd}
        comm.head_dic_send(self, head_dic)
        head_dic = comm.head_dic_unpack(self)
        if head_dic == -1: return
        for item in head_dic['file_list']:
            print(item)


client = MYTCPClient(('127.0.0.1', 8080))
client.run()