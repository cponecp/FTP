import os
from ftp_server.lib import comm
import socketserver


class MYTCPServer(socketserver.BaseRequestHandler):
    allow_reuse_address = False
    max_packet_size = 1024
    coding = 'utf-8'
    request_queue_size = 5

    def handle(self):
        print("server is working")
        while True:
            head_dic = comm.head_dic_unpack(self)
            if head_dic == -1: break

            # 验证通过
            if comm.auth(head_dic['name'], 'password') == head_dic['password']:
                # 登录成功设置用户根目录和用户名
                self.server_dir = 'user/%s' % head_dic['name']
                self.name = head_dic['name']

                self.request.send(str(254).encode('utf-8'))
                while True:
                    try:
                        head_dic = comm.head_dic_unpack(self)
                        # print(head_dic)  # 测试通过
                        cmd = head_dic['cmd']
                        if hasattr(self, cmd):
                            func = getattr(self, cmd)
                            func(head_dic)
                    except Exception as e:
                        break
            # 验证失败发送失败信息
            else:
                self.request.send('either of  name or password is wrong'.encode('utf-8'))

    def put(self, args):
        file_path = os.path.normpath(os.path.join(
            self.server_dir,
            args['filename']
        ))

        filesize = args['fileSize']
        exits_stored = os.path.getsize(self.server_dir)
        vol = int(comm.auth(self.name, 'max_store'))
        # 判断文件是否已经存在
        is_exits = os.path.isfile(file_path)
        is_full = ((exits_stored + filesize) > vol)
        tell = None
        # 计算上一次传输的末尾位置
        # print('hello') # 通过
        if is_exits:
            with open(file_path, 'rb') as f:
                f.seek(0, 2)
                tell = f.tell()

        send_dic = {'is_full': is_full, 'is_exits': is_exits, 'recv_size': tell}
        # print(send_dic)  #未通过
        res = comm.head_dic_send(self, send_dic)

        # 判断可用空间是否足够客户端上传文件
        if not is_full:
            if not is_exits:
                recv_size = 0
                with open(file_path, 'wb') as f:
                    while recv_size < filesize:
                        recv_data = self.request.recv(self.max_packet_size)
                        f.write(recv_data)
                        recv_size += len(recv_data)
                    else:
                        rev_md = comm.hash_file(file_path, filesize)
                        if rev_md != args['md5']:
                            print('文件校验一致')
                        else:
                            print('文件有损坏')
            else:
                recv_size = tell
                with open(file_path, 'ab') as f:
                    while recv_size < filesize:
                        recv_data = self.request.recv(self.max_packet_size)
                        f.write(recv_data)
                        recv_size += len(recv_data)
                    else:
                        rev_md = comm.hash_file(file_path, filesize)
                        if rev_md != args['md5']:
                            print('文件校验一致')
                        else:
                            print('文件有损坏')

    # 实现查看客户目录下文件
    def show_list(self, agrs):
        l = os.listdir(self.server_dir)
        head_dic = {'file_list': l, 'fileSize': os.path.getsize(self.server_dir)}
        comm.head_dic_send(self, head_dic)
