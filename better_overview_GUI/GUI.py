import sys, os, cv2
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QApplication, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QPoint, pyqtSignal

# Für Loading images
from PyQt5.QtGui import QPixmap, QImage


# Für whole screen stuff
from PyQt5.QtWidgets import QDesktopWidget 


class ImageViewer(QMainWindow):
    def get_max_number_of_vertical_obj_possible(self,screen,length):
        width, height = screen.width(), screen.height()
        return int(height/length) - 1
    def __init__(self,image_with_label_array):
        super().__init__()
        self.screen = QDesktopWidget().screenGeometry()

        self.init_var()
        self.initUI()
        #self.render_images(image_with_label_array)

    def init_var(self):
        self.img_dir = '/home/johannes/Dokumente/programme/image_analyses_v2/content/data/train/0_gelenk'
        self.images = os.listdir(self.img_dir)

        self.path_to_image_1 = '/home/johannes/Dokumente/programme/image_analyses_v2/content/data/train/0_gelenk/0.jpg'
        self.path_to_image_2 = '/home/johannes/Dokumente/programme/image_analyses_v2/content/data/train/0_gelenk/3.jpg'
        self.DIV = 1
    def initUI(self):
        self.setWindowTitle('Image Viewer')
        self.setGeometry(0, 0, self.screen.width(), self.screen.height())

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)

    def render_images(self, img_and_text_array):
        images_to_load = []            
        first_img, size = self.load_cv2_image(img_and_text_array[0][0])

        for i in range(self.get_max_number_of_vertical_obj_possible(self.screen,size[0])):
            if i < len(img_and_text_array):
                new_label = QLabel()
                img, deprecated_size = self.load_cv2_image(img_and_text_array[i][0])
                images_to_load.append((img, new_label, img_and_text_array[i][1]))
            else:
                break
        
        for image in images_to_load:
            text_label = QLabel(f'{image[2]}')

            container_widget = QWidget()  # Create a container widget
            container_layout = QHBoxLayout(container_widget)
            container_layout.addWidget(image[1])
            container_layout.addWidget(text_label)

            container_widget.setFixedWidth(200)

            self.layout.addWidget(container_widget)
            image[1].setPixmap(image[0])
    
    def load_cv2_image(self,cv_image):
        height, width, channel = cv_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(bytes(cv_image.data), width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        return QPixmap.fromImage(q_image), (height, width)
        
    def load_image(self, path_to_image):
        pixmap = QPixmap(path_to_image)
        desired_width = int(pixmap.width() / self.DIV)
        desired_height = int(pixmap.height() / self.DIV)
        scaled_pixmap = pixmap.scaled(desired_width, desired_height, Qt.KeepAspectRatio)
        return scaled_pixmap, (desired_height, desired_width)


def mask_image(img):
  gray_img = cv2.cvtColor(img , cv2.COLOR_BGR2GRAY)
  blurred = cv2.GaussianBlur(gray_img, (13, 13), 0)
  threshold = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
  #cv2_imshow(threshold)
  #cv2.imwrite('output_threshold.png', threshold)   #<-- Für Download für Templates
  return threshold

def check_image_in_part(image, point, a = 60):
  dx_plus, dx_minus, dy_plus, dy_minus = max(0 ,int(point[0]) + a), max(0 ,int(point[0]) - a), max(0 ,int(point[1])) + a, max(0 ,int(point[1]) - a)
  part_of_image = image[dy_minus:dy_plus, dx_minus:dx_plus]
  return part_of_image

def show_image_in_size(processed_img):
  display_width = 600
  # Resize the image for display while maintaining the aspect ratio
  aspect_ratio = processed_img.shape[1] / processed_img.shape[0]
  display_height = int(display_width / aspect_ratio)
  display_img = cv2.resize(processed_img, (display_width, display_height))
  # Display the resized image
  cv2.imshow('Image', display_img)
  cv2.waitKey(0)
  #cv2.destroyAllWindows()

def test():

    images_dir = os.listdir('/home/johannes/Dokumente/programme/image_analyses_v2/content/raw_images')
    match_image = cv2.cvtColor(mask_image(cv2.imread(f'/home/johannes/Dokumente/programme/image_analyses_v2/content/raw_images/{images_dir[14]}')), cv2.COLOR_GRAY2BGR)

    
    
    show_image_in_size(match_image)
    
    image_with_label_array = []
    for centroid in centroids:
        img = check_image_in_part(match_image, centroid[0])
        if img.shape[0] != 0 and img.shape[1] != 0:
            show_image_in_size(img)
            label = centroid[1]
            image_with_label_array.append((img, label))
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    obj = ImageViewer(image_with_label_array)
    obj.show()
    sys.exit(app.exec_())