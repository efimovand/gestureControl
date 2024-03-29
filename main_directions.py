import time
import cv2
import mediapipe as mp
from collections import deque
from functions_pc import screenshot_save_file, screenshot_save_system, volume_up, volume_down, volume_mute, play_pause, next_track, previous_track


cap = cv2.VideoCapture(0)  # Камера
hands = mp.solutions.hands.Hands(max_num_hands=1)  # Объект ИИ для определения ладони
draw = mp.solutions.drawing_utils  # Для рисования ладони

# Указательный палец
prev_finger8_positions = deque(maxlen=10)  # Очередь для хранения предыдущих координат указательного пальца
motion_direction_X = None  # Направление движения по X
motion_direction_Y = None  # Направление движения по Y
motion_threshold = 200  # Порог для определения движения

savedGesture = 0  # Последнее время использования одного из одиночных жестов

startTime = time.perf_counter()  # Время начала работы программы


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

            # Каждый палец и его координаты
            for point_id, point_coordinates in enumerate(handLms.landmark):

                h, w, c = image.shape
                cx, cy = int(point_coordinates.x * w), int(point_coordinates.y * h)

                # Указательный палец
                if point_id == 8:

                    cv2.circle(image, (cx, cy), 20, (255, 0, 255), cv2.FILLED)  # Обозначение УКАЗАТЕЛЬНОГО пальца точкой

                    prev_finger8_positions.append((cx, cy))

                    # Если очередь координат заполнена (есть что анализировать)
                    if len(prev_finger8_positions) == prev_finger8_positions.maxlen:

                        # Получение предыдущей и текущей позиций указательного пальца
                        prev_finger8_pos = prev_finger8_positions[0]
                        current_finger8_pos = prev_finger8_positions[-1]

                        # Разница между текущей и предыдущей позициями указательного пальца
                        x_diff = current_finger8_pos[0] - prev_finger8_pos[0]
                        y_diff = current_finger8_pos[1] - prev_finger8_pos[1]

                        # Определение направления движения по X
                        if x_diff > motion_threshold:
                            motion_direction_X = 'вправо'
                        elif x_diff < -motion_threshold:
                            motion_direction_X = 'влево'
                        else:
                            motion_direction_X = None

                        # Определение направления движения по Y
                        if y_diff > motion_threshold:
                            motion_direction_Y = 'вниз'
                            volume_down()  # Громкость НИЖЕ
                        elif y_diff < -motion_threshold:
                            motion_direction_Y = 'вверх'
                            volume_up()  # Громкость ВЫШЕ
                        else:
                            motion_direction_Y = None

                # Большой палец
                if point_id == 4:

                    cv2.circle(image, (cx, cy), 20, (255, 0, 255), cv2.FILLED)  # Обозначение БОЛЬШОГО пальца точкой

                    current_finger4_pos = cx, cy

                    # Определение жеста щипка
                    try:
                        if abs(current_finger4_pos[0] - current_finger8_pos[0]) < 20 and abs(current_finger4_pos[1] - current_finger8_pos[1]) < 20 and (time.perf_counter() - savedGesture > 1):
                            print('Apple Щипок', round(time.perf_counter() - startTime, 2))
                            savedGesture = time.perf_counter()  # Задержка жеста
                            screenshot_save_system()  # Создание скриншота
                    except:
                        pass

                # Мизинец
                if point_id == 20:

                    cv2.circle(image, (cx, cy), 20, (255, 0, 255), cv2.FILLED)  # Обозначение МИЗИНЦА точкой

                    current_finger20_pos = cx, cy

                    # Определение жеста БП+М
                    try:
                        if abs(current_finger20_pos[0] - current_finger4_pos[0]) < 20 and abs(current_finger20_pos[1] - current_finger4_pos[1]) < 20 and (time.perf_counter() - savedGesture > 1):
                            print('БП+М', round(time.perf_counter() - startTime, 2))
                            savedGesture = time.perf_counter()  # Задержка жеста
                            volume_mute()  # Отключение/включение звука
                    except:
                        pass

            draw.draw_landmarks(image, handLms, mp.solutions.hands.HAND_CONNECTIONS)

    if motion_direction_X is not None:
        print(f'Движение по X обнаружено ({motion_direction_X})', round(time.perf_counter() - startTime, 2))
    if motion_direction_Y is not None:
        print(f'Движение по Y обнаружено ({motion_direction_Y})', round(time.perf_counter() - startTime, 2))

    cv2.imshow("Gesture Control", image)
