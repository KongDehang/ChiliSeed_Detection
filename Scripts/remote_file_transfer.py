import socket
import struct
import json
import cv2
import threading
import time

import numpy as np

# 服务器参数
SERVER_IP = '172.20.49.89'  # 替换为 Jetson Nano 的IP
SERVER_PORT = 5001

# 定义消息类型
MSG_TYPE_IMAGE = 'IMAGE'
MSG_TYPE_VARIABLE = 'VARIABLE'

def send_image(sock, image_path):
    img = cv2.imread(image_path)
    _, img_encoded = cv2.imencode('.jpg', img)
    data = img_encoded.tobytes()
    msg_type = MSG_TYPE_IMAGE.encode()
    msg_type_len = len(msg_type)
    msg_len = len(data)
    header = struct.pack('!II', msg_type_len, msg_len)
    sock.sendall(header + msg_type + data)
    print('图片已发送')

def send_variable(sock, variable):
    var_json = json.dumps(variable).encode()
    msg_type = MSG_TYPE_VARIABLE.encode()
    msg_type_len = len(msg_type)
    msg_len = len(var_json)
    header = struct.pack('!II', msg_type_len, msg_len)
    sock.sendall(header + msg_type + var_json)
    print('变量已发送')

def receive_data(sock):
    try:
        while True:
            header = sock.recv(8)
            if not header:
                break
            msg_type_len, msg_len = struct.unpack('!II', header)
            msg_type = sock.recv(msg_type_len).decode()
            data = b''
            while len(data) < msg_len:
                packet = sock.recv(msg_len - len(data))
                if not packet:
                    break
                data += packet
            if msg_type == MSG_TYPE_IMAGE:
                nparr = np.frombuffer(data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cv2.imshow('Received Image from Server', img)
                cv2.waitKey(1)
            elif msg_type == MSG_TYPE_VARIABLE:
                var = json.loads(data.decode())
                print(f'Received Variable from Server: {var}')
            else:
                print('Unknown message type')
    except Exception as e:
        print(f'接收错误: {e}')
    finally:
        sock.close()

def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    print(f'已连接到服务器 {SERVER_IP}:{SERVER_PORT}')

    # 启动接收线程
    recv_thread = threading.Thread(target=receive_data, args=(sock,), daemon=True)
    recv_thread.start()

    try:
        while True:
            cmd = input("输入命令 (send_image/send_var/exit): ")
            if cmd == 'send_image':
                path = input("输入图片路径: ")
                send_image(sock, path)
            elif cmd == 'send_var':
                var_input = input("输入变量（JSON格式）: ")
                var = json.loads(var_input)
                send_variable(sock, var)
            elif cmd == 'exit':
                break
            else:
                print("未知命令")
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        print('已断开连接')

if __name__ == '__main__':
    client()
