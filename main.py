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

from visualizer import Visualizer

import os
import cv2


def main():
  images_dir = os.listdir('content/raw_images')
  #for i, element in enumerate(images_dir):
  #  print((i, element))
  match_image = cv2.cvtColor(mask_image(cv2.imread(f'content/raw_images/{images_dir[15]}')), cv2.COLOR_GRAY2BGR)

  gelenk_templates = generate_templates('content/templates/gelenke')
  festlager_templates = generate_templates('content/templates/festlager')
  loslager_templates = generate_templates('content/templates/loslager')
  biegesteife_ecke_templates = generate_templates('content/templates/biegesteife_ecke')

  gelenk_centroids, gelenk_centroids_img = get_obj(gelenk_templates, match_image)
  festlager_centroids, festlager_centroids_img = get_obj(festlager_templates, match_image, MODE='festlager')
  loslager_centroids, loslager_centroids_img = get_obj(loslager_templates, match_image)
  biegesteife_ecke_centroids, biegesteife_ecke_centroids_img = get_obj(biegesteife_ecke_templates, match_image)

  gelenk_centroids = add_label(gelenk_centroids, 0)
  festlager_centroids = add_label(festlager_centroids, 1)
  loslager_centroids = add_label(loslager_centroids, 2)
  biegesteife_ecke_centroids = add_label(biegesteife_ecke_centroids, 3)

  #centroids_add_staebe_of_gelenke, staebe_of_gelenke_img = custome_line_detection(gelenk_centroids, match_image)
  #staebe_of_festlager, staebe_of_festlager_img = custome_line_detection(festlager_centroids, match_image)
  #staebe_of_loslager, staebe_of_loslager_img = custome_line_detection(loslager_centroids, match_image)
  #staebe_of_biegesteife_ecke, staebe_of_biegesteife_ecke_img = custome_line_detection(biegesteife_ecke_centroids, match_image)

  centroids = add_all_centroids([gelenk_centroids, festlager_centroids, loslager_centroids, biegesteife_ecke_centroids], match_image)
  centroid_image = draw_centroids_on_image(centroids, match_image)

  #download_raw_part_images(centroids, match_image, images_dir[11])

  centroids_add_staebe, staebe_img = custome_line_detection(centroids, match_image)
  centroids_add_angles = check_staebe(centroids_add_staebe)
  centroids_add_directions = check_directions(centroids_add_angles)

  connection_map, connection_img = connect_centroids(centroids_add_directions, match_image)
  
  show_image_in_size(centroid_image)

  System = Visualizer(centroids_add_directions,connection_map)
  System.get_size_of_system()
  #System.show()

def test_mode():
  centroids_add_directions = [[(652.2313232421875, 1131.5631917317708), 1, [[(665.2313232421875, 1065.5631917317708), (667.2313232421875, 999.5631917317708), [0, -1]], [(718.2313232421875, 1121.5631917317708), (784.2313232421875, 1123.5631917317708), [0, -1]]], [90.0]], [(682.0310581752232, 1127.244907924107), 1, [[(748.0310581752232, 1122.244907924107), (814.0310581752232, 1124.244907924107), [0, -1]]], []], [(1042.5579659598213, 418.508553641183), 1, [[(976.5579659598213, 376.508553641183), (910.5579659598213, 376.508553641183), [-1, -1]], [(1108.5579659598213, 419.508553641183), (1174.5579659598213, 421.508553641183), [-1, -1]]], [180.0]], [(303.5849304199219, 158.00970458984375), 2, [], []], [(1975.1089274088542, 186.38629659016928), 2, [], []], [(648.8301391601562, 1481.9779663085938), 1, [], []], [(1651.353271484375, 167.8665771484375), 2, [[(1585.353271484375, 177.8665771484375), (1519.353271484375, 157.8665771484375), [-1, -1]], [(1717.353271484375, 173.8665771484375), (1783.353271484375, 167.8665771484375), [-1, -1]]], [157.94717232452695]], [(1431.3909505208333, 1169.785400390625), 1, [[(1403.3909505208333, 1103.785400390625), (1403.3909505208333, 1037.785400390625), [-1, -1]], [(1365.3909505208333, 1137.785400390625), (1299.3909505208333, 1136.785400390625), [-1, -1]]], [90.0]], [(376.30157470703125, 1456.2832438151042), 1, [], []]]
  connection_map = [[(0, 1), (1, 0)], [(2, 1), (6, 0)]]

  System = Visualizer(centroids_add_directions,connection_map)
  System.get_size_of_system()
  #System.show()


if __name__ == '__main__':
  #test_mode()
  
  main()