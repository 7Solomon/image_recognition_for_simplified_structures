import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QHBoxLayout, QScrollArea
from PyQt5.QtGui import QPixmap, QImage

from PyQt5.QtWidgets import QDesktopWidget, QPushButton

from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect, QByteArray



from label_programm.GUI_for_label_of_part_image import Labeler

class GUI(QMainWindow):
    def __init__(self, match_image):
        super().__init__()
        self.match_image = match_image
        self.initUI()
    def initUI(self):
        self.setWindowTitle('GUI')

        self.screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, self.screen.width(), self.screen.height())

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.configure_main_layout()

    def configure_main_layout(self):
        container_widget_for_buttons =  QWidget()
        self.button_layout = QVBoxLayout(container_widget_for_buttons)
        
        match_image_label = QLabel()
        image_pixmap = self.load_cv2_image(self.match_image)
        match_image_label.setPixmap(image_pixmap.scaled(400, 400, aspectRatioMode=1, transformMode=0))

        container_widget_for_right_side_layout = QWidget()
        self.right_side_layout = QVBoxLayout(container_widget_for_right_side_layout)
        
        image_overview_container = QWidget()
        image_overview_container.setStyleSheet("background-color: grey;")
        self.image_overvie_layout = QHBoxLayout(image_overview_container)
        self.image_overvie_layout.addWidget(match_image_label)

        self.right_side_layout.addWidget(image_overview_container)
        self.create_part_image_overview()

        self.main_layout.addWidget(container_widget_for_buttons)
        self.main_layout.addWidget(container_widget_for_right_side_layout)
        
    def create_part_image_overview(self):
        container_widget_for_part_image = QScrollArea()
        container_widget_for_part_image.setWidgetResizable(True)
        self.part_image_layout = QHBoxLayout(container_widget_for_part_image)

        self.right_side_layout.addWidget(container_widget_for_part_image) 
        

    def create_and_connect_button(self, connectted_function, display_name):
        button = QPushButton(display_name)
        button.clicked.connect(connectted_function)
        button.setFixedSize(400,40)
        self.button_layout.addWidget(button)
    
    def connect_main(self, main_f):
        image_1, image_2, centroid_data, part_image_and_percentage = main_f(self.match_image)
        image_pixmap_1 = self.load_cv2_image(image_1)
        image_pixmap_2 = self.load_cv2_image(image_2)

        image_label_1, image_label_2 = QLabel(), QLabel()
        image_label_1.setPixmap(image_pixmap_1.scaled(400, 400, aspectRatioMode=1, transformMode=0))
        image_label_2.setPixmap(image_pixmap_2.scaled(400, 400, aspectRatioMode=1, transformMode=0))

        for centroid in part_image_and_percentage:
            container_widget = QWidget()
            container_layout = QVBoxLayout(container_widget)
            
            image = QLabel()
            image.setPixmap(self.load_cv2_image(centroid[0]))

            label_string = []
            switch_label = ['Gelenk','Festlager', 'Loslager', 'b_ecke', 'n_gelenk']
            #print(type(centroid[1]))
            for i, predic in enumerate(centroid[1][1]):
                label_string.append(f'{int(predic*100)}% --> {switch_label[i]}')
            
            label_string_widget = QWidget()
            label_string_layout = QVBoxLayout(label_string_widget)
            for a_string in label_string:
                label = QLabel(a_string)
                label_string_layout.addWidget(label)


            container_layout.addWidget(image)
            container_layout.addWidget(label_string_widget)


            self.part_image_layout.addWidget(container_widget)

        self.image_overvie_layout.addWidget(image_label_1)  
        self.image_overvie_layout.addWidget(image_label_2)  

    def open_labler(self):
        viewer = Labeler()
        viewer.show()
    

   

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



if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = GUI()
    viewer.show()
    sys.exit(app.exec_())

    