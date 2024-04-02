from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QFileDialog, QScrollBar
from PyQt5.QtGui import QPixmap, QCursor, QPainter
from PyQt5.QtCore import Qt
import fitz


class PDFViewerApp(QMainWindow):

    def __init__(self):
        super().__init__()

        # Окно
        self.setWindowTitle("PDF Drawing App")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        # Кнопка открытия PDF
        self.open_pdf_button = QPushButton("Open PDF")
        self.open_pdf_button.clicked.connect(self.open_pdf)
        self.layout.addWidget(self.open_pdf_button)

        # Кнопка перехода на следующую страницу
        self.next_page_button = QPushButton("Next Page")
        self.next_page_button.clicked.connect(self.next_page)
        self.layout.addWidget(self.next_page_button)

        # Кнопка перехода на предыдущую страницу
        self.prev_page_button = QPushButton("Prev Page")
        self.prev_page_button.clicked.connect(self.previous_page)
        self.layout.addWidget(self.prev_page_button)

        # Кнопка смены курсора
        self.change_cursor_button = QPushButton("Switch Cursor")
        self.change_cursor_button.clicked.connect(self.setup_cursor)
        self.layout.addWidget(self.change_cursor_button)

        self.scene = QGraphicsView()
        self.layout.addWidget(self.scene)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.pdf_path = None
        self.pdf_doc = None
        self.pdf_pages = []
        self.current_page = 0

        # self.pen_color = Qt.black
        # self.pen_width = 5
        # self.drawing = False
        # self.last_point = None
        # self.current_mouse_position = None

        self.visible_cursor = False
        self.setup_cursor()

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

    # Отображение конкретной страницы PDF
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

    # Настройка курсора
    def setup_cursor(self):

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

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.drawing = True
    #         self.last_point = event.pos()
    #         self.current_mouse_position = event.pos()
    #         print('pressed')
    #
    # def mouseMoveEvent(self, event):
    #     if event.buttons() & Qt.LeftButton:
    #         self.current_mouse_position = event.pos()
    #         self.scene.viewport().update()
    #         print('moved')
    #
    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.drawing = False
    #         self.last_point = None
    #         self.current_mouse_position = None
    #         print('released')
    #
    # def paintEvent(self, event):
    #     if self.drawing and self.last_point and self.current_mouse_position:
    #         painter = QPainter(self.scene.viewport())
    #         pen = QPen(self.pen_color, self.pen_width)
    #         painter.setPen(pen)
    #         painter.drawLine(self.last_point, self.current_mouse_position)


if __name__ == "__main__":
    app = QApplication([])
    window = PDFViewerApp()
    window.show()
    app.exec_()
