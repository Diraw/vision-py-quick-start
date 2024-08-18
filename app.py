from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import cv2
import base64
import numpy as np
import mediapipe as mp
import time

app = Flask(__name__)
socketio = SocketIO(app)

# 存储每个客户端的 pTime 和 Hands 实例
client_data = {}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    # 初始化每个客户端的 pTime 和 Hands 实例
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    client_data[request.sid] = {"pTime": 0, "hands": hands}
    print(f"Client {request.sid} connected")


@socketio.on("disconnect")
def handle_disconnect():
    client_data.pop(request.sid, None)  # 移除断开连接的客户端
    print(f"Client {request.sid} disconnected")


@socketio.on("video_frame")
def handle_video_frame(data):
    try:
        # Base64 解码
        img_data = base64.b64decode(data)
        img_array = np.frombuffer(img_data, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if frame is None:
            print("Failed to decode frame")
            return

        # 获取客户端的 pTime 和 Hands 实例
        client_info = client_data.get(request.sid)
        if client_info is None:
            return

        pTime = client_info["pTime"]
        hands = client_info["hands"]

        # 使用 process_frame 处理帧
        processed_frame, pTime = process_frame(frame, pTime, hands)
        client_data[request.sid]["pTime"] = pTime

        # 编码为 JPEG 格式并重新编码为 Base64 字符串
        _, buffer = cv2.imencode(".jpg", processed_frame)
        processed_data = base64.b64encode(buffer).decode("utf-8")

        emit("processed_frame", processed_data, room=request.sid)
    except Exception as e:
        print(f"Error processing frame: {e}")


def process_frame(frame, pTime, hands):
    mpDraw = mp.solutions.drawing_utils

    # 水平翻转图像
    img = cv2.flip(frame, 1)

    # 将图像从 BGR 格式转换为 RGB 格式
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 处理图像以检测手部
    results = hands.process(imgRGB)

    # 如果检测到手部
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mp.solutions.hands.HAND_CONNECTIONS)

    # 计算帧率
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # 在图像上显示帧率
    cv2.putText(
        img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3
    )

    return img, pTime


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
