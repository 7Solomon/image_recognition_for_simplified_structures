import sys, os
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit

class ImageViewer(QMainWindow):
    def __init__(self, path_to_images):
        super().__init__()
        self.DIV = 2
        self.img_indx = 0
        self.path_to_images = path_to_images
        self.path_to_image = f'/home/johannes/Dokumente/programme/image_analyses_v2/content/raw_images/{self.path_to_images[self.img_indx]}'
        self.img_name = self.path_to_image.split('/')[-1]
        self.all_position = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Labeln')
        self.setGeometry(0, 0, 2000, 1000)  # Set a fixed window size

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a QLabel to display the image with a fixed size
        self.image_label = ClickableLabel()  # Use a custom QLabel that captures clicks
        self.image_label.setFixedSize(int(2048 / self.DIV), int(1536 / self.DIV))  # Set a fixed size for the QLabel
        central_layout = QVBoxLayout()
        central_layout.addWidget(self.image_label)

        # Create a sidebar frame
        sidebar = QWidget()
        sidebar.setStyleSheet("background-color: #333;")
        sidebar.setFixedWidth(200)  # Set the sidebar width


        self.variable_label = QTextEdit(f'{self.all_position}')
        button_1 = QPushButton('Save to File')
        previos_button = QPushButton('Previos img')
        next_button = QPushButton('Next img')
       

        self.variable_label.setStyleSheet("color: white;")
        button_1.setStyleSheet("color: white;")
        previos_button.setStyleSheet("color: white;")
        next_button.setStyleSheet("color: white;")

        # Add buttons to the sidebar
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.variable_label)
        sidebar_layout.addWidget(button_1)
        sidebar_layout.addWidget(previos_button)
        sidebar_layout.addWidget(next_button)
        sidebar.setLayout(sidebar_layout)

        # Create a horizontal layout to arrange the sidebar and central content
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addLayout(central_layout)
        horizontal_layout.addWidget(sidebar)

        central_widget.setLayout(horizontal_layout)
        button_1.clicked.connect(self.save_label_to_file)
        previos_button.clicked.connect(self.previos_img)
        next_button.clicked.connect(self.next_img)

        # Load and display an image
        self.load_image()
        self.image_label.clicked.connect(self.click_event_handler)

    def load_image(self):
        # Load the image from the specified path using QPixmap
        pixmap = QPixmap(self.path_to_image)
        desired_width = int(pixmap.width() / self.DIV)
        desired_height = int(pixmap.height() / self.DIV)

        # Scale the image to fit within the fixed QLabel size while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(desired_width, desired_height, Qt.KeepAspectRatio)
        # Set the pixmap as the image content of the QLabel
        self.image_label.setPixmap(scaled_pixmap)

    def click_event_handler(self, pos: QPoint):
        converted_pos = (pos.x() * self.DIV, pos.y() * self.DIV)
        print(f"{self.img_name}: Clicked at {converted_pos}")
        self.all_position.append(converted_pos)

        self.variable_label.setText(f'{self.all_position}')
    def save_label_to_file(self):
        with open('label.txt', 'a') as file:
            line_to_add = f'{self.img_name}:{self.all_position}'
            file.write(line_to_add + '\n')
        self.all_position = []
        self.variable_label.setText(f'{self.all_position}')
    def next_img(self):
        self.img_indx += 1
        if self.img_indx <= len(self.path_to_images):
            self.path_to_image = f'/home/johannes/Dokumente/programme/image_analyses_v2/content/raw_images/{self.path_to_images[self.img_indx]}'
            self.load_image()
    def previos_img(self):
        self.img_indx -= 1
        if self.img_indx >= 0:
            self.path_to_image = f'/home/johannes/Dokumente/programme/image_analyses_v2/content/raw_images/{self.path_to_images[self.img_indx]}'
            self.load_image()

class ClickableLabel(QLabel):
    # Define a custom clicked signal
    clicked = pyqtSignal(QPoint)

    def mousePressEvent(self, event):
        # Emit the clicked signal with the click coordinates
        self.clicked.emit(event.pos())


def main():
    images_dir = os.listdir('/home/johannes/Dokumente/programme/image_analyses_v2/content/raw_images')

    app = QApplication(sys.argv)
    viewer = ImageViewer(images_dir)
    viewer.show()
    # sys.exit()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
