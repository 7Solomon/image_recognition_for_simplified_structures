import sys, os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage

from PyQt5.QtWidgets import QDesktopWidget 

from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect

class ImageViewer(QMainWindow):
    def return_label(self, indx):
        label = ['Gelenk', 'Festlager', 'Loslager', 'Biegesteife Ecke', 'Normalkraft Gelenk']
        return label[indx]
    def get_max_number_of_columns(self, a=60):
        screen_width = self.screen.width()  # Replace with your screen width
        image_width = a*3
        max_columns = screen_width // image_width
        if max_columns > 8:
            return 8
        return max_columns
    def check_image_in_part(self,point, qimage, a=60):
        x, y = int(point[0] - a), int(point[1] - a)
        region_to_show = QRect(x, y, 2 * a, 2 * a)
        cropped_qimage = qimage.copy(region_to_show)
        pixmap = QPixmap.fromImage(cropped_qimage)
        return pixmap
    def convert_cv2_image_to_pixmap(self, opencv_image):
        height, width, channel = opencv_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(opencv_image.data, width, height, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)
        return pixmap

    def __init__(self,centroids, match_image_url):
        super().__init__()
        self.screen = QDesktopWidget().screenGeometry()
        self.init_var(centroids, match_image_url)
        self.initUI()
    def init_var(self, centroids, match_image_url):
        self.match_image = QImage()
        self.match_image.load(match_image_url)
        self.centroids = centroids
        self.DIV = 2
    def initUI(self):
        self.setWindowTitle('Anschauen ist toll')
        self.setGeometry(0, 0, self.screen.width(), self.screen.height())

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
    
    def load_for_check_centroids(self, part_image, predictions):
        pixmap_img = convert_cv2_image_to_pixmap()
        container_widget = QWidget()
        container_widget_2 = QWidget()

        hori_layout = QHBoxLayout(container_widget)
        verti_layout = QVBoxLayout(container_widget_2)

        img_label = self.load_image_to_label(pixmap_img)

        for i, predic in enumerate(predictions[0]):
            text_label = QLabel(f'Es ist mit  {predic*100} %  --> {switch_label[i]}')
            verti_layout.addWidget(text_label)
        
        hori_layout.addWidget(img_label)
        hori_layout.addWidget(container_widget_2)
        container_widget.setFixedWidth(200)

        return container_widget

    
    def load_centroids(self):
        layout = QGridLayout(self.central_widget)
        row, col = 0, 0
        max_col = self.get_max_number_of_columns()
        for i, centroid in enumerate(self.centroids):
            if i < 20:
                container_widget = QWidget()
                hori_layout = QHBoxLayout(container_widget)
                pixmap = self.check_image_in_part(centroid[0], self.match_image)
                img_label = self.load_image_to_label(pixmap)
                
                label = self.return_label(centroid[1])
                text_label = QLabel(f'{label}')

                hori_layout.addWidget(img_label)
                hori_layout.addWidget(text_label)
                container_widget.setFixedWidth(200)

                layout.addWidget(container_widget, col, row)

                col += 1
                if col >= max_col:
                    col = 0  
                    row += 1
            else:
                break
    def load_images(self, images):
        layout = QHBoxLayout(self.central_widget)
        for i, image in enumerate(images):
            container_widget = QWidget()
            hori_layout = QVBoxLayout(container_widget)
            pixmap = self.convert_cv2_image_to_pixmap(image)
            img_label = self.load_image_to_label(pixmap) 
            hori_layout.addWidget(img_label)

            layout.addWidget(container_widget)

    def load_image_to_label(self, pixmap):        
        desired_width = int(pixmap.width() / self.DIV)
        desired_height = int(pixmap.height() / self.DIV)
        scaled_pixmap = pixmap.scaled(desired_width, desired_height, Qt.KeepAspectRatio)
        label = QLabel()
        label.setPixmap(scaled_pixmap)
        return label
    

def main():
    centroids = [[(652.2313232421875, 1131.5631917317708), 1, [[(665.2313232421875, 1065.5631917317708), (667.2313232421875, 999.5631917317708), [0, -1]], [(718.2313232421875, 1121.5631917317708), (784.2313232421875, 1123.5631917317708), [0, -1]]], [90.0]], [(682.0310581752232, 1127.244907924107), 1, [[(748.0310581752232, 1122.244907924107), (814.0310581752232, 1124.244907924107), [0, -1]]], []], [(1042.5579659598213, 418.508553641183), 1, [[(976.5579659598213, 376.508553641183), (910.5579659598213, 376.508553641183), [-1, -1]], [(1108.5579659598213, 419.508553641183), (1174.5579659598213, 421.508553641183), [-1, -1]]], [180.0]], [(303.5849304199219, 158.00970458984375), 2, [], []], [(1975.1089274088542, 186.38629659016928), 2, [], []], [(648.8301391601562, 1481.9779663085938), 1, [], []], [(1651.353271484375, 167.8665771484375), 2, [[(1585.353271484375, 177.8665771484375), (1519.353271484375, 157.8665771484375), [-1, -1]], [(1717.353271484375, 173.8665771484375), (1783.353271484375, 167.8665771484375), [-1, -1]]], [157.94717232452695]], [(1431.3909505208333, 1169.785400390625), 1, [[(1403.3909505208333, 1103.785400390625), (1403.3909505208333, 1037.785400390625), [-1, -1]], [(1365.3909505208333, 1137.785400390625), (1299.3909505208333, 1136.785400390625), [-1, -1]]], [90.0]], [(376.30157470703125, 1456.2832438151042), 1, [], []]]
    connection_map = [[(0, 1), (1, 0)], [(2, 1), (6, 0)]]

    app = QApplication(sys.argv)

    match_image = QImage()
    match_image.load('/home/johannes/Dokumente/programme/image_analyses_v2/content/raw_images/WhatsApp Image 2023-08-12 at 14.00.07(1).jpeg')

    viewer = ImageViewer(centroids, match_image)
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
