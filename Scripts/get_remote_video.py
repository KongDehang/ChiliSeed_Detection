# 视频接收端
import cv2
import zmq
import base64
import numpy as np

# 初始化 ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.SUB)
# socket.connect("tcp://172.20.49.47:5555")
socket.connect("tcp://172.20.49.89:5555")
socket.subscribe("")

# 创建窗口
cv2.namedWindow("Receiver")

while True:
    # 接收帧数据
    encoded_image = socket.recv()

    # 解码图像数据
    buffer = base64.b64decode(encoded_image)
    np_array = np.frombuffer(buffer, dtype=np.uint8)
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # 在窗口中显示帧
    cv2.imshow("Receiver", frame)

    # 按下 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cv2.destroyAllWindows()