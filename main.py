from base_functions import mask_image
from base_functions import show_image_in_size

from functions import add_label
from functions import generate_templates
from functions import get_obj
from functions import custome_line_detection
from functions import add_all_centroids
from functions import check_staebe
from functions import check_directions
from functions import connect_centroids
from functions import download_raw_part_images
from functions import draw_centroids_on_image
from functions import compound_images
from functions import sort_folder_for_data_pipeline
from functions import handle_main_for_GUI
from functions import save_all_part_image_with_percentage

from better_overview_GUI.GUI_2 import ImageViewer
from visualize.GUI_for_main import GUI

from object_classification import train_modell

import os
import cv2
import sys
from PyQt5.QtWidgets import QApplication


def main(match_image, DOWNLOAD= False):
  

  #for i, element in enumerate(images_dir):
  #  print((i, element))

  templates_dir = os.listdir('content/templates/')
  templates, centroids_array = [], []
  
  for template_dir in templates_dir:
    templates.append(generate_templates(f'content/templates/{template_dir}'))
  for template in templates:
    centroids, image = get_obj(template, match_image)
    centroids_array.append(centroids)
  for i, centroids in enumerate(centroids_array):
    centroids_array[i] = add_label(centroids, i)


  #centroids_add_staebe_of_gelenke, staebe_of_gelenke_img = custome_line_detection(gelenk_centroids, match_image)
  #staebe_of_festlager, staebe_of_festlager_img = custome_line_detection(festlager_centroids, match_image)
  #staebe_of_loslager, staebe_of_loslager_img = custome_line_detection(loslager_centroids, match_image)
  #staebe_of_biegesteife_ecke, staebe_of_biegesteife_ecke_img = custome_line_detection(biegesteife_ecke_centroids, match_image)

  centroids = add_all_centroids(centroids_array, match_image, DOWNLOAD=DOWNLOAD)
  centroid_image = draw_centroids_on_image(centroids, match_image)
  part_image_and_percentage = save_all_part_image_with_percentage(centroids, match_image)

  centroids, staebe_img = custome_line_detection(centroids, match_image)
  centroids = check_staebe(centroids)
  centroids = check_directions(centroids)


  connection_map, connection_img = connect_centroids(centroids, match_image)
  return centroid_image, connection_img, centroids, part_image_and_percentage
  #app = QApplication(sys.argv)
  #viewer = ImageViewer(centroids, match_image_url)
  #viewer.load_images([centroid_image,staebe_img])
  #viewer.load_centroids()
  #viewer.show()
  
  #sys.exit(app.exec_())


  #display_GUI(centroids_add_directions, match_image)

  #show_image_in_size(centroid_image)
  #show_image_in_size(staebe_img)


  #System = Visualizer(centroids_add_directions,connection_map)
  #System.get_size_of_system()
  #System.show()

def test_mode():
  centroids_add_directions = [[(652.2313232421875, 1131.5631917317708), 1, [[(665.2313232421875, 1065.5631917317708), (667.2313232421875, 999.5631917317708), [0, -1]], [(718.2313232421875, 1121.5631917317708), (784.2313232421875, 1123.5631917317708), [0, -1]]], [90.0]], [(682.0310581752232, 1127.244907924107), 1, [[(748.0310581752232, 1122.244907924107), (814.0310581752232, 1124.244907924107), [0, -1]]], []], [(1042.5579659598213, 418.508553641183), 1, [[(976.5579659598213, 376.508553641183), (910.5579659598213, 376.508553641183), [-1, -1]], [(1108.5579659598213, 419.508553641183), (1174.5579659598213, 421.508553641183), [-1, -1]]], [180.0]], [(303.5849304199219, 158.00970458984375), 2, [], []], [(1975.1089274088542, 186.38629659016928), 2, [], []], [(648.8301391601562, 1481.9779663085938), 1, [], []], [(1651.353271484375, 167.8665771484375), 2, [[(1585.353271484375, 177.8665771484375), (1519.353271484375, 157.8665771484375), [-1, -1]], [(1717.353271484375, 173.8665771484375), (1783.353271484375, 167.8665771484375), [-1, -1]]], [157.94717232452695]], [(1431.3909505208333, 1169.785400390625), 1, [[(1403.3909505208333, 1103.785400390625), (1403.3909505208333, 1037.785400390625), [-1, -1]], [(1365.3909505208333, 1137.785400390625), (1299.3909505208333, 1136.785400390625), [-1, -1]]], [90.0]], [(376.30157470703125, 1456.2832438151042), 1, [], []]]
  connection_map = [[(0, 1), (1, 0)], [(2, 1), (6, 0)]]

  System = Visualizer(centroids_add_directions,connection_map)
  System.get_size_of_system()
  #System.show()


def download_all_part_images():
  images_dir = sorted(os.listdir('content/raw_images'))
  for image in images_dir:
    match_image_url = f'content/raw_images/{image}'
    #match_image = cv2.cvtColor(mask_image(cv2.imread(match_image_url)), cv2.COLOR_GRAY2BGR)
    match_image = cv2.imread(match_image_url)
    main(match_image,DOWNLOAD=True)


def open_GUI():
  images_dir = sorted(os.listdir('content/raw_images'))
  match_image_url = f'content/raw_images/{images_dir[0]}'
  match_image = cv2.imread(match_image_url)

  app = QApplication(sys.argv)
  viewer = GUI(match_image)
  
  viewer.create_and_connect_button(sort_folder_for_data_pipeline, 'Create Folder for DataPipeLine')
  viewer.create_and_connect_button(download_all_part_images, 'Download all part Images to label Programm')
  viewer.create_and_connect_button(lambda: viewer.connect_main(main), 'Get Centroids')
  viewer.create_and_connect_button(viewer.open_labler, 'Open Labler')
  viewer.create_and_connect_button(train_modell, 'Train part Image')
  
  

  viewer.show()
  sys.exit(app.exec_())
if __name__ == '__main__':
  open_GUI()
  