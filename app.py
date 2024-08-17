from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from frame_processor import process_frame
import cv2
import base64
import numpy as np
import time

app = Flask(__name__)
socketio = SocketIO(app)

# 初始化 pTime
pTime = 0


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("video_frame")
def handle_video_frame(data):
    global pTime
    # Base64 解码
    img_data = base64.b64decode(data)
    img_array = np.frombuffer(img_data, dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if frame is None:
        print("Failed to decode frame")
        return

    # 使用process_frame处理帧
    processed_frame, pTime = process_frame(frame, pTime)

    # 编码为JPEG格式并重新编码为Base64字符串
    _, buffer = cv2.imencode(".jpg", processed_frame)
    processed_data = base64.b64encode(buffer).decode("utf-8")

    emit("processed_frame", processed_data)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
