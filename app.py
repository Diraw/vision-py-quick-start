from flask import Flask, Response, render_template
import cv2
import socket
import struct
import subprocess

app = Flask(__name__)


def send_frames():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 8000))

    cap = cv2.VideoCapture(0)  # 使用摄像头

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            _, buffer = cv2.imencode(".jpg", frame)
            frame_data = buffer.tobytes()

            client_socket.sendall(struct.pack("<L", len(frame_data)) + frame_data)

            data = client_socket.recv(struct.calcsize("<L"))
            if not data:
                break
            frame_size = struct.unpack("<L", data)[0]

            processed_data = b""
            while len(processed_data) < frame_size:
                packet = client_socket.recv(frame_size - len(processed_data))
                if not packet:
                    break
                processed_data += packet

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + processed_data + b"\r\n"
            )
    finally:
        cap.release()
        client_socket.close()


@app.route("/video_feed")
def video_feed():
    return Response(send_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/")
def index():
    subprocess.Popen(["python", "receiver.py"])
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
