import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QHBoxLayout, QScrollArea
from PyQt5.QtGui import QPixmap, QImage

from PyQt5.QtWidgets import QDesktopWidget, QPushButton

from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect, QByteArray

class GUI_Centroid(QMainWindow):
    def __init__(self,centroids, match_image, image_with_centroids):
        super().__init__()
        self.centroids = centroids
        self.match_image = match_image
        self.image_with_centroids = image_with_centroids
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle('GUI for not detected Centroids')

        self.screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, self.screen.width(), self.screen.height())

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.configure_main_layout()
        
    def configure_main_layout(self):
        
        match_image_label = QLabel()
        match_image_pixmap = self.load_cv2_image(self.image_with_centroids)
        match_image_label.setPixmap(match_image_pixmap)

        self.main_layout.addWidget(match_image_label)




    def load_cv2_image(self, cv_image):
        if cv_image is not None:
            if len(cv_image.shape) == 3:
                height, width, channel = cv_image.shape
                bytes_per_line = 3 * width
                image_data = cv_image.tobytes()  # Convert NumPy array to bytes
                q_image = QImage(image_data, width, height, bytes_per_line, QImage.Format_RGB888)
            elif len(cv_image.shape) == 2:
                height, width = cv_image.shape
                bytes_per_line = width
                image_data = cv_image.tobytes()  # Convert NumPy array to bytes
                q_image = QImage(image_data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            else:
                print('Not an expected shape, search for it')
                return None
            return QPixmap.fromImage(q_image)
        else:
            return None
