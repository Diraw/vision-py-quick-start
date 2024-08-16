import cv2
import socket
import struct
import numpy as np
from frame_processor import processe_frame  # Import the function
import time

# 初始化时间变量
pTime = 0

# 创建服务器 socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8000))
server_socket.listen(1)
connection, client_address = server_socket.accept()

try:
    while True:
        # 读取帧大小
        data = connection.recv(struct.calcsize("<L"))
        if not data:
            break
        frame_size = struct.unpack("<L", data)[0]

        # 读取帧数据
        frame_data = b""
        while len(frame_data) < frame_size:
            packet = connection.recv(frame_size - len(frame_data))
            if not packet:
                break
            frame_data += packet

        frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        # 对帧进行处理
        processed_frame, pTime = processe_frame(frame, pTime)

        # 编码处理后的帧
        _, buffer = cv2.imencode(".jpg", processed_frame)
        processed_data = buffer.tobytes()

        # 发送处理后的帧大小和数据
        connection.sendall(struct.pack("<L", len(processed_data)) + processed_data)

finally:
    connection.close()
    server_socket.close()
