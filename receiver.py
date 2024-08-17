import socket
import struct
import cv2
import numpy as np
from frame_processor import processe_frame
import time

# Initialize the time variable
pTime = 0

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8000))
server_socket.listen(1)

while True:
    client_socket, _ = server_socket.accept()
    try:
        while True:
            data = client_socket.recv(struct.calcsize("<L"))
            if not data:
                break
            frame_size = struct.unpack("<L", data)[0]

            frame_data = b""
            while len(frame_data) < frame_size:
                packet = client_socket.recv(frame_size - len(frame_data))
                if not packet:
                    break
                frame_data += packet

            frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)

            # Process the frame and update pTime
            processed_frame, pTime = processe_frame(frame, pTime)

            _, buffer = cv2.imencode(".jpg", processed_frame)
            processed_data = buffer.tobytes()

            client_socket.sendall(
                struct.pack("<L", len(processed_data)) + processed_data
            )
    finally:
        client_socket.close()
