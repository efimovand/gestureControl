from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QFileDialog, QScrollBar
from PyQt5.QtGui import QPixmap, QCursor, QPainter
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread
import fitz
import time
import cv2
import mediapipe as mp
from collections import deque


last_gesture = time.perf_counter()  # Время последнего жеста


class GestureRecognitionThread(QThread):

    motion_detected = pyqtSignal(str)  # Распознанный жест

    def run(self):

        cap = cv2.VideoCapture(0)  # Камера
        hands = mp.solutions.hands.Hands(max_num_hands=1)  # Объект ИИ для определения ладони

        prev_finger8_positions = deque(maxlen=10)
        motion_threshold = 200

        while True:

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

                            prev_finger8_positions.append((cx, cy))  # Добавление текущих координат в очередь координат пальца

                            if len(prev_finger8_positions) == prev_finger8_positions.maxlen:  # Если очередь координат пальца заполнена

                                prev_finger8_pos = prev_finger8_positions[0]  # Предыдущая позиция
                                current_finger8_pos = prev_finger8_positions[-1]  # Текущая позиция

                                x_diff = current_finger8_pos[0] - prev_finger8_pos[0]  # Разница по X
                                y_diff = current_finger8_pos[1] - prev_finger8_pos[1]  # Разница по Y

                                if x_diff > motion_threshold:
                                    self.motion_detected.emit('right')
                                elif x_diff < -motion_threshold:
                                    self.motion_detected.emit('left')
                                if y_diff > motion_threshold:
                                    self.motion_detected.emit('down')
                                elif y_diff < -motion_threshold:
                                    self.motion_detected.emit('up')

                        # Большой палец
                        if point_id == 4:

                            current_finger4_pos = cx, cy  # Текущая позиция

                            # Определение жеста щипка
                            try:
                                if abs(current_finger4_pos[0] - current_finger8_pos[0]) < 15 and abs(current_finger4_pos[1] - current_finger8_pos[1]) < 15 and (time.perf_counter() - last_gesture > 1):
                                    self.motion_detected.emit('shipok')
                            except:
                                pass


class PDFViewerApp(QMainWindow):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("PDF Drawing App")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        self.open_pdf_button = QPushButton("Open PDF")
        self.open_pdf_button.clicked.connect(self.open_pdf)
        self.layout.addWidget(self.open_pdf_button)

        self.next_page_button = QPushButton("Next Page")
        self.next_page_button.clicked.connect(self.next_page)
        self.layout.addWidget(self.next_page_button)

        self.prev_page_button = QPushButton("Prev Page")
        self.prev_page_button.clicked.connect(self.previous_page)
        self.layout.addWidget(self.prev_page_button)

        self.change_cursor_button = QPushButton("Switch Cursor")
        self.change_cursor_button.clicked.connect(self.change_cursor)
        self.layout.addWidget(self.change_cursor_button)

        self.scene = QGraphicsView()
        self.layout.addWidget(self.scene)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.pdf_path = None
        self.pdf_doc = None
        self.pdf_pages = []
        self.current_page = 0
        self.visible_cursor = False
        self.change_cursor()

    # Открытие PDF
    def open_pdf(self):
        self.pdf_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)")
        if self.pdf_path:
            self.load_pdf()

    # Загрузка PDF
    def load_pdf(self):
        self.pdf_doc = fitz.open(self.pdf_path)
        for page_num in range(self.pdf_doc.page_count):
            pixmap = QPixmap()
            pixmap.loadFromData(self.pdf_doc[page_num].get_pixmap().tobytes())
            self.pdf_pages.append(pixmap)
        self.show_page(0)

    # Показывание определенной страницы
    def show_page(self, page_num):
        self.current_page = page_num
        pixmap = self.pdf_pages[page_num]
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.scene.setScene(scene)

    # Следующая страница
    def next_page(self):
        if self.current_page < len(self.pdf_pages) - 1:
            self.current_page += 1
            self.show_page(self.current_page)
            print(f'\r📖 Page [{self.current_page + 1}/{len(self.pdf_pages)}]', end='', flush=True)

    # Предыдущая страница
    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)
            print(f'\r📖 Page [{self.current_page + 1}/{len(self.pdf_pages)}]', end='', flush=True)

    # Смена курсора (цветной/прозрачный)
    def change_cursor(self):
        if not self.visible_cursor:
            current_color = Qt.red
            self.visible_cursor = True
            print('\r🔴 The cursor has been turned ON', end='', flush=True)
        else:
            current_color = Qt.transparent
            self.visible_cursor = False
            print('\r🚫 The cursor has been turned OFF', end='', flush=True)

        red_cursor_pixmap = QPixmap(16, 16)
        red_cursor_pixmap.fill(Qt.transparent)

        painter = QPainter(red_cursor_pixmap)
        painter.setPen(Qt.NoPen)
        painter.setBrush(current_color)
        painter.drawEllipse(0, 0, 16, 16)
        painter.end()

        red_cursor = QCursor(red_cursor_pixmap)
        self.setCursor(red_cursor)

    # Отслеживание жестов
    def handle_gesture(self, direction):

        global last_gesture

        if time.perf_counter() - last_gesture > 0.5:  # Задержка между жестами

            if direction == 'right':  # Следующая страница
                self.next_page()

            elif direction == 'left':  # Предыдущая страница
                self.previous_page()

            elif direction == 'shipok':  # Изменение курсора
                self.change_cursor()

            last_gesture = time.perf_counter()  # Сохранение времени последнего жеста


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    viewer_window = PDFViewerApp()
    viewer_window.show()

    gesture_thread = GestureRecognitionThread()
    gesture_thread.motion_detected.connect(viewer_window.handle_gesture)
    gesture_thread.start()

    sys.exit(app.exec_())