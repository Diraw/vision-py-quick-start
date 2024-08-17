import cv2
import mediapipe as mp
import time

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils


def process_frame(frame, pTime):
    # 水平翻转图像
    img = cv2.flip(frame, 1)

    # 将图像从 BGR 格式转换为 RGB 格式
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 处理图像以检测手部
    results = hands.process(imgRGB)

    # 如果检测到手部
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                cv2.circle(img, (cx, cy), 15, (255, 0, 255), 1)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # 计算帧率
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # 在图像上显示帧率
    cv2.putText(
        img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3
    )

    return img, pTime
