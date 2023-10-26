import sys, os, cv2

sys.path.append('/home/johannes/Dokumente/programme/image_analyses_v2')

import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage

from PyQt5.QtWidgets import QDesktopWidget, QPushButton

from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect, QByteArray

from base_functions import custom_sort

class Labeler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_var()
        self.initUI()
    def init_var(self):
        self.test_folder_URL = '/home/johannes/Dokumente/programme/image_analyses_v2/label_programm/test_folder'
        self.list_of_images = sorted(os.listdir(self.test_folder_URL), key=custom_sort) 
    def initUI(self):
        self.setWindowTitle('Label machen ist toll')

        self.screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, self.screen.width(), self.screen.height())

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.initLabler()
    def initLabler(self):
        layout = QHBoxLayout(self.central_widget)
        self.label = QLabel()
        # Set first Imaagee
        self.label.setPixmap(self.load_pixmap_from_url(self.list_of_images[0]))
        self.name_of_image = self.list_of_images[0]

        

        button_container = QWidget()
        button_container_layout = QVBoxLayout(button_container)        
        
        button_gelenk = QPushButton('Gelenk')
        button_festlager = QPushButton('Festlager')
        button_loslager = QPushButton('Loslager')
        button_biegesteife_ecke = QPushButton('Biegesteife Ecke')
        button_normalkraft_gelenk = QPushButton('Normalkraft Gelenk')
        button = [button_gelenk, button_festlager, button_loslager, button_biegesteife_ecke, button_normalkraft_gelenk]
        
        for i, but in enumerate(button):
            but.setFixedSize(150, 40)
            but.clicked.connect(lambda state, i=i: self.button_clicked(i))
            button_container_layout.addWidget(but)
        
        button_delete = QPushButton('Nothing')
        button_delete.setFixedSize(150, 40)
        button_delete.clicked.connect(lambda: self.delete_image())
        button_container_layout.addWidget(button_delete)
        
        layout.addWidget(self.label)
        layout.addWidget(button_container)
        
    def button_clicked(self, number_label):
        self.list_of_images = sorted(os.listdir(self.test_folder_URL))
        current_pixmap = self.label.pixmap()
        if not current_pixmap.isNull():
            dir_string = '/home/johannes/Dokumente/programme/image_analyses_v2/label_programm/test_label' 
            image = current_pixmap.toImage()
            match number_label:
                case 0:
                    if len(os.listdir(f"{dir_string}/0_gelenk")) < 0:
                        biggest_number = str(int(sorted(os.listdir(f"{dir_string}/0_gelenk"))[-1].split('.')[0]) + 1)
                    else:
                        biggest_number = str(0)
                    image.save(f'{dir_string}/0_gelenk/{biggest_number}.png')
                    if os.path.exists(f'{self.test_folder_URL}/{self.name_of_image}'):
                        os.remove(f'{self.test_folder_URL}/{self.name_of_image}')
                    else:
                        print(' no file ith that, name to delete')
                case 1:
                    if len(os.listdir(f"{dir_string}/1_festlager")) < 0:
                        biggest_number = str(int(sorted(os.listdir(f"{dir_string}/1_festlager"))[-1].split('.')[0]) + 1)
                    else:
                        biggest_number = str(0)
                    image.save(f'{dir_string}/1_festlager/{biggest_number}.png')
                    if os.path.exists(f'{self.test_folder_URL}/{self.name_of_image}'):
                        os.remove(f'{self.test_folder_URL}/{self.name_of_image}')
                    else:
                        print(' no file ith that, name to delete')
                case 2:
                    if len(os.listdir(f"{dir_string}/2_loslager")) < 0:
                        biggest_number = str(int(sorted(os.listdir(f"{dir_string}/2_loslager"))[-1].split('.')[0]) + 1)
                    else:
                        biggest_number = str(0)
                    image.save(f'{dir_string}/2_loslager/{biggest_number}.png')
                    if os.path.exists(f'{self.test_folder_URL}/{self.name_of_image}'):
                        os.remove(f'{self.test_folder_URL}/{self.name_of_image}')
                    else:
                        print(' no file ith that, name to delete')
                case 3:
                    if len(os.listdir(f"{dir_string}/3_biegesteife_ecke")) < 0:
                        biggest_number = str(int(sorted(os.listdir(f"{dir_string}/3_biegesteife_ecke"))[-1].split('.')[0]) + 1)
                    else:
                        biggest_number = str(0)
                    image.save(f'{dir_string}/3_biegesteife_ecke/{biggest_number}.png')
                    if os.path.exists(f'{self.test_folder_URL}/{self.name_of_image}'):
                        os.remove(f'{self.test_folder_URL}/{self.name_of_image}')
                    else:
                        print(' no file ith that, name to delete')
                case 4:
                    if len(os.listdir(f"{dir_string}/4_normalkraft_gelenk")) < 0:
                        biggest_number = str(int(sorted(os.listdir(f"{dir_string}/4_normalkraft_gelenk"))[-1].split('.')[0]) + 1)
                    else:
                        biggest_number = str(0)
                    image.save(f'{dir_string}/4_normalkraft_gelenk/{biggest_number}.png')
                    if os.path.exists(f'{self.test_folder_URL}/{self.name_of_image}'):
                        os.remove(f'{self.test_folder_URL}/{self.name_of_image}')
                    else:
                        print(' no file ith that, name to delete')
                case _:
                    print('Unknown Label')
            self.list_of_images = sorted(os.listdir(self.test_folder_URL))
            self.label.setPixmap(self.load_pixmap_from_url(self.list_of_images[0]))
            self.name_of_image = self.list_of_images[0]

    def delete_image(self):
        if os.path.exists(f'{self.test_folder_URL}/{self.name_of_image}'):
            os.remove(f'{self.test_folder_URL}/{self.name_of_image}')
            self.list_of_images = sorted(os.listdir(self.test_folder_URL))
            self.label.setPixmap(self.load_pixmap_from_url(self.list_of_images[0]))
            self.name_of_image = self.list_of_images[0]
        else:
            print(f' no file with {self.name_of_image}, as name to delete')
    
    def load_pixmap_from_url(self,URL):
        image = self.load_cv2_image(cv2.imread(f'{self.test_folder_URL}/{URL}'))
        #print(f'{image} from: {URL}')
        return image

    def load_cv2_image(self,cv_image):
        if cv_image is not None:
            height, width, channel = cv_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(bytes(cv_image.data), width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            return QPixmap.fromImage(q_image)
        else:
            return


if __name__ == '__main__':
    app = QApplication(sys.argv)

    viewer = Labeler()
    viewer.show()
    sys.exit(app.exec_())