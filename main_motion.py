import time
import cv2
import mediapipe as mp
# import autopy
from collections import deque


cap = cv2.VideoCapture(0)  # Камера
hands = mp.solutions.hands.Hands(max_num_hands=1)  # Объект ИИ для определения ладони
draw = mp.solutions.drawing_utils  # Для рисования ладони

prev_finger_positions = deque(maxlen=10)  # Очередь для хранения предыдущих координат указательного пальца

motion_detected_X = False  # Флаг для отслеживания движения по X
motion_detected_Y = False  # Флаг для отслеживания движения по Y
motion_threshold = 200  # Порог для определения движения

startTime = time.perf_counter()


while True:

    # Выход на ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

    _, image = cap.read()
    image = cv2.flip(image, 1)
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(imageRGB)

    if results.multi_hand_landmarks:

        for handLms in results.multi_hand_landmarks:

            for point_id, point_coordinates in enumerate(handLms.landmark):

                h, w, c = image.shape
                cx, cy = int(point_coordinates.x * w), int(point_coordinates.y * h)

                # Указательный палец
                if point_id == 8:

                    cv2.circle(image, (cx, cy), 25, (255, 0, 255), cv2.FILLED)  # Обозначение указательного пальца большой точкой

                    prev_finger_positions.append((cx, cy))

                    if len(prev_finger_positions) == prev_finger_positions.maxlen:

                        x_diff = max(prev_finger_positions, key=lambda x: x[0])[0] - min(prev_finger_positions, key=lambda x: x[0])[0]
                        y_diff = max(prev_finger_positions, key=lambda x: x[1])[1] - min(prev_finger_positions, key=lambda x: x[1])[1]

                        # Движение по X
                        if x_diff > motion_threshold:
                            motion_detected_X = True
                        else:
                            motion_detected_X = False

                        # Движение по Y
                        if y_diff > motion_threshold:
                            motion_detected_Y = True
                        else:
                            motion_detected_Y = False

            draw.draw_landmarks(image, handLms, mp.solutions.hands.HAND_CONNECTIONS)

    if motion_detected_X:
        print('Движение по X обнаружено', round(time.perf_counter() - startTime, 2))
    if motion_detected_Y:
        print('Движение по Y обнаружено', round(time.perf_counter() - startTime, 2))

    cv2.imshow("Gesture Control", image)
