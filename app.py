from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from frame_processor import process_frame
import cv2
import base64
import numpy as np

app = Flask(__name__)
socketio = SocketIO(app)

# 存储每个客户端的 pTime
client_times = {}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    client_times[request.sid] = 0  # 初始化每个客户端的 pTime
    print(f"Client {request.sid} connected")


@socketio.on("disconnect")
def handle_disconnect():
    client_times.pop(request.sid, None)  # 移除断开连接的客户端
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

        # 使用 process_frame 处理帧
        pTime = client_times.get(request.sid, 0)
        processed_frame, pTime = process_frame(frame, pTime)
        client_times[request.sid] = pTime

        # 编码为 JPEG 格式并重新编码为 Base64 字符串
        _, buffer = cv2.imencode(".jpg", processed_frame)
        processed_data = base64.b64encode(buffer).decode("utf-8")

        emit("processed_frame", processed_data, room=request.sid)
    except Exception as e:
        print(f"Error processing frame: {e}")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
