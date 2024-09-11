from queue import Queue
import threading
import cv2
import time, random
import torch
from ultralytics import YOLO
lock = threading.Lock()

frame_queue = Queue(maxsize=1)


class Producer(threading.Thread):
    """docstring for ClassName"""
    global frame_queue

    def __init__(self, cap):
        super(Producer, self).__init__()
        self.cap = cap

    def run(self):
        print('in producer')
        while self.cap.isOpened():
            ret, image = self.cap.read()
            print('get frame = ', ret)
            if ret:
                # lock.acquire()
                if frame_queue.full():
                    frame_queue.get()
                frame_queue.put(image)
                # lock.release()
            else:
                # video_path = r"E:\ADataset\datasets\videosets\72-800-1.mp4"
                # self.cap = cv2.VideoCapture(video_path)
                break


class Consumer(threading.Thread):
    """docstring for Consumer"""
    global frame_queue

    def __init__(self, model):
        super(Consumer, self).__init__()
        # self.frame_queue = frame_queue
        self.model = model

    def run(self):
        print('in consumer')
        while True:
            print('frame_queue size=', frame_queue.qsize())
            if frame_queue.qsize() > 0:
                # # lock.acquire()
                frame = frame_queue.get()
                # 裁剪并进行推理
                cropped_frame = frame[0:3000, 1275:2875]
                results = self.model.predict(source=cropped_frame, imgsz=3040)
                # 可视化结果
                annotated_frame = results[0].plot()
                # lock.release()
                # 调整帧的大小以适应显示窗口
                frame[0:3000, 1275:2875] = annotated_frame

                # # 实时检测方式（取消注释）
                # frame = frame_queue.get_nowait()
                # results = self.model.predict(source=frame, imgsz=3040)
                # frame = results[0].plot()

                resized_frame = cv2.resize(frame, (800, 600))
                cv2.imshow("V8-SCAM", resized_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                break


if __name__ == '__main__':
    print('run program')
    # 初始化模型
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLO(r'..\weights\best.pt').to(device)
    video_path = r"E:\ADataset\datasets\videosets\z600.mp4"
    cap = cv2.VideoCapture(video_path)

    # 取消注释使用默认摄像头
    # cap = cv2.VideoCapture(0)

    producer = Producer(cap)
    producer.daemon = True

    consumer = Consumer(model)
    consumer.daemon = True

    producer.start()
    consumer.start()

    producer.join()
    consumer.join()
