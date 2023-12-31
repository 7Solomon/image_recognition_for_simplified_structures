from base_functions import mask_image
from base_functions import show_image_in_size

from functions import add_label
from functions import generate_templates
from functions import get_obj
from functions import custome_line_detection
from functions import add_all_centroids
from functions import check_staebe
from functions import connect_centroids
from functions import download_raw_part_images
from functions import draw_centroids_on_image
from functions import compound_images

import os
import cv2


def main():
  images_dir = os.listdir('content/raw_images')
  #for i, element in enumerate(images_dir):
  #  print((i, element))
  match_image = cv2.cvtColor(mask_image(cv2.imread(f'content/raw_images/{images_dir[12]}')), cv2.COLOR_GRAY2BGR)

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

  staebe_of_gelenke, staebe_of_gelenke_img = custome_line_detection(gelenk_centroids, match_image)
  staebe_of_festlager, staebe_of_festlager_img = custome_line_detection(festlager_centroids, match_image)
  staebe_of_loslager, staebe_of_loslager_img = custome_line_detection(loslager_centroids, match_image)
  staebe_of_biegesteife_ecke, staebe_of_biegesteife_ecke_img = custome_line_detection(biegesteife_ecke_centroids, match_image)

  centroids = add_all_centroids([staebe_of_gelenke, staebe_of_festlager, staebe_of_loslager, staebe_of_biegesteife_ecke], match_image)
  centroid_image = draw_centroids_on_image(centroids, match_image)

  #download_raw_part_images(centroids, match_image, images_dir[11])


  angles = check_staebe(gelenk_centroids)
  connection_map, connection_img = connect_centroids(angles, match_image)
  
  print(angles)
  print(connection_map)

  show_image_in_size(compound_images([centroid_image, connection_img]))
  #cv2.waitKey(0)
  #show_image_in_size(connection_img)
  cv2.waitKey(0)

  cv2.destroyAllWindows()

  #System = Visualizer(gelenk_centroids,connection_map)
  #System.draw_centroids()
  #System.show()

if __name__ == '__main__':
    main()