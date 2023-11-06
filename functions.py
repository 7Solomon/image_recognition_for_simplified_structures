from centroid_detection import local_template_matching_SIFT
from centroid_detection import dbscan_clustering
from centroid_detection import sort_for_center_points

from line_detection import get_borders_of_part_arround_point
from line_detection import border_check
from line_detection import iterate_through_borders
from line_detection import check_if_stab

from base_functions import draw_points_on_image
from base_functions import is_in_range
from base_functions import check_image_in_part
from base_functions import show_image_in_size
from base_functions import custom_sort
from base_functions import mask_image

from object_classification import predict_on_data
from object_classification import c_load_modell

from better_overview_GUI.GUI import ImageViewer

import os
import cv2
import numpy as np
import random
import shutil

import sys
from PyQt5.QtWidgets import QApplication

def compound_images(images):
  composite_image = images[0].copy()  # Make a copy to preserve the original
  height = composite_image.shape[0]

  for i in range(1, len(images)):
    if images[i].shape[0] != height:
      print(f'Images have different heights. Cannot stack without resizing.')
      return None

    composite_image = np.hstack((composite_image, images[i]))

  return composite_image
  

def draw_centroids_on_image(centroids, img):
  output_image = img.copy()
  output_image = draw_points_on_image([centroid[0] for centroid in centroids], output_image)
  return output_image


def check_centroid(centroid, match_image, DOWNLOAD=False):
  output_image = match_image.copy()
  part_image = check_image_in_part(output_image, centroid[0])
  # Adde schwarze pixels das input shape stimmt
  if part_image.shape[0] != 120:
    part_image = cv2.copyMakeBorder(part_image, top=0, bottom=120-part_image.shape[0], left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
  if part_image.shape[1] != 120:
    part_image = cv2.copyMakeBorder(part_image, top=0, bottom=0, left=120-part_image.shape[1], right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
  
  # For Download
  directory = os.listdir('label_programm/test_folder')
  if len(directory) > 0:
    length = int(sorted(directory, key=custom_sort)[-1].split('.')[0]) + 1
  else:
    length = 0

  if DOWNLOAD:
    cv2.imwrite(f'label_programm/test_folder/{length}.png', part_image)
  loaded_model = c_load_modell()
  predictions = predict_on_data(part_image, loaded_model)
  switch_label = ['gelenk','festlager', 'loslager', 'b_ecke', 'n_gelenk']
  #for i, predic in enumerate(predictions[0]):
  #  print(f'Es ist mit  {predic*100} %  --> {switch_label[i]}')
  
  if max(predictions[0]) > 0.1:
    idx = np.argmax(predictions[0])
    if centroid[1] == idx:  
      centroid[1] = [centroid[1], predictions[0]]
    else:
      #print(f'{ centroid[1], idx}: Found NOT Correkt')
      centroid[1] = [idx,predictions[0]]
    return centroid
  else:
    #print('No element Found')
    return None


def add_all_centroids(array, match_image, DOWNLOAD=False):
  c_load_modell()

  all_centroids_array = []
  double = False
  for centroids in array:
    for centroid in centroids:
      if len(all_centroids_array) > 0:
        for controll_centroid in all_centroids_array:
          if is_in_range(controll_centroid[0], centroid[0]):
            print(f'{(controll_centroid[0], centroid[0])}: are close, so was {centroid[0]} not added')
            double = True
        if not double:
          new_centroid = check_centroid(centroid, match_image, DOWNLOAD=DOWNLOAD)
          if new_centroid != None:
            all_centroids_array.append(centroid)
        double = False
      else:
        new_centroid = check_centroid(centroid, match_image)
        if new_centroid != None:
          all_centroids_array.append(new_centroid)
  return all_centroids_array


def generate_templates(dir):
  template_imgs = []
  template_dir = os.listdir(dir)

  for template in template_dir:
    template_imgs.append(cv2.imread(f'{dir}/{template}'))
  return template_imgs


def get_obj(template_imgs, match_image, MODE=None):
  centroids_of_all_templates = []

  for template_img in template_imgs:
    matched_points, matched_image = local_template_matching_SIFT(template_img, match_image)
    #show_image_in_size(matched_image)
    cluster_pts, cluster_label, cluster_img = dbscan_clustering(matched_points, match_image, MODE=MODE)
    #show_image_in_size(cluster_img)
    centroids_of_clusters, centroid_of_clusters_img = sort_for_center_points(cluster_pts, cluster_label, match_image)
    #show_image_in_size(centroid_of_clusters_img)

    for centroid_of_clusters in centroids_of_clusters:
      centroids_of_all_templates.append(centroid_of_clusters)

  # Um zu schauen ob welche doppelt in centroids_of_all_templates ist
  for i, centroid_1 in enumerate(centroids_of_all_templates):
    for j, centroid_2 in enumerate(centroids_of_all_templates):
      if i == j:
        continue
      else:
        if is_in_range(centroid_1, centroid_2):
          centroids_of_all_templates.remove(centroid_2)

  output_img = draw_points_on_image(centroids_of_all_templates, match_image)

  return centroids_of_all_templates, output_img

def get_angle(line1,line2):
  points1 = np.array(line1)
  points2 = np.array(line2)

  vektor1 = points1[0] - points1[1]
  vektor2 = points2[0] - points2[1]

  einheits_vektor1 = vektor1 / np.linalg.norm(vektor1)
  einheits_vektor2 = vektor2 / np.linalg.norm(vektor2)

  dot_product = np.dot(einheits_vektor1, einheits_vektor2)
  angle_radians = np.arccos(dot_product)
  angle_degrees = np.degrees(angle_radians)


  # rundung ist nur in 90° schritten!!
  if angle_degrees > 80.0 and angle_degrees < 100.0:
     angle_degrees = 90.0
  if angle_degrees > 170.0 and angle_degrees < 190.0:
    angle_degrees = 180.0
  if angle_degrees > 260.0 and angle_degrees < 280.0:
    angle_degrees = 270

  return angle_degrees

def check_staebe(staebe_centroids):
  angles = []
  for i, staebe in enumerate(staebe_centroids):
    if len(staebe[2]) > 1:
      for j in range(len(staebe[2])-1):
        angle = get_angle(staebe[2][j], staebe[2][j+1])
        angles.append(angle)
    staebe_centroids[i] = [staebe[0], staebe[1], staebe[2], angles]
    angles = []
  return staebe_centroids

def add_label(centroids, label):
  for i, centroid in enumerate(centroids):
    centroids[i] = [centroid, label]
  return centroids


def custome_line_detection(centroids, match_image):
  output_image = mask_image(match_image.copy())
  RASTER_A = 6             # Für Abstand des Blurs und neuwahl der Kords
  per_centroid_lines = []
  for i, centroid in enumerate(centroids):
    array_up, array_down, array_left, array_right, border_image, part_image = get_borders_of_part_arround_point(centroid[0], output_image, RASTER_A)
    new_kords_up, new_kords_down, new_kords_left, new_kords_right = border_check(centroid[0], part_image, array_up,array_down, array_left, array_right, RASTER_A, output_image)
    lines = iterate_through_borders(new_kords_up, new_kords_down, new_kords_left, new_kords_right, output_image, RASTER_A)
    for line in lines:
      if check_if_stab(line, output_image):
        cv2.line(output_image, (int(line[0][0]), int(line[0][1])), (int(line[1][0]), int(line[1][1])), (0, 0, 255), 3)
        per_centroid_lines.append(line)
    centroids[i] = [centroid[0],centroid[1],per_centroid_lines]
    per_centroid_lines = []
  return centroids, output_image

def download_raw_part_images(centroids, match_image, name):
  for i, centroid in enumerate(centroids):
    output_image = match_image.copy()
    part_image = check_image_in_part(output_image, centroid[0])
    success = cv2.imwrite(f'content/raw_train_data/{name.split(".")[0]}_{i}.jpg', part_image)
    if success:
      print(f'Saved image {name.split(".")[0]}_{i}.jpg successfully')
    else:
      print(f'Error saving image {i}.jpg')

def check_staebe(staebe_centroids):
  angles = []
  for i, staebe in enumerate(staebe_centroids):
    if len(staebe[2]) > 1:
      for j in range(len(staebe[2])-1):
        angle = get_angle(staebe[2][j], staebe[2][j+1])
        angles.append(angle)
    staebe_centroids[i] = [staebe[0], staebe[1], staebe[2], angles]
    angles = []
  return staebe_centroids


def check_if_centroid_between_connection(p1, p2, centroids):
  line_start = np.array(p1)
  line_end = np.array(p2)

  line_vec = line_end - line_start
  line_length = np.linalg.norm(line_vec)

  for centroid in centroids:
    point = np.array(centroid[0])

    point_vec = point - line_start
    distance = np.dot(point_vec, line_vec) / line_length

    if -10 <= distance <= line_length + 10:
      return True

  return False

def check_for_doubles_in_connection_map(map):
  new_map = []
  for e in range(len(map)):
    duplicate = False  # Flag to check for duplicates

    for a in range(len(new_map)):
      if map[e][0] == new_map[a][1] and map[e][1] == new_map[a][0]:
        duplicate = True
        break

    if not duplicate:
      new_map.append(map[e])

  return new_map


def check_if_connection(ap1,ap2,ep1,ep2):
  line_start = np.array(ap1)
  line_end = np.array(ap2)

  line_vec = line_end - line_start
  line_length = np.linalg.norm(line_vec)

  point_1 = np.array(ep1)
  point_2 = np.array(ep2)

  point_vec_1 = point_1 - line_start
  point_vec_2 = point_2 - line_start
  distance_1 = np.dot(point_vec_1, line_vec) / line_length
  distance_2 = np.dot(point_vec_2, line_vec) / line_length

  if -10 < distance_1 and -10 < distance_2:
    return True

  return False



def connect_centroids(centroids, match_image):
  output_image = match_image.copy()
  connection_map = []
  centroid_staebe_store_List = []
  for centroid in centroids:
    centroid_staebe_store_List.append(centroid[2])
    #print(centroid[2])
  for i in range(len(centroid_staebe_store_List)):
    for j in range(len(centroid_staebe_store_List)):
      if i != j : #and len(centroid_staebe_store_List[i]) and len(centroid_staebe_store_List[j])
        for n in range(len(centroid_staebe_store_List[i])):
          for a in range(len(centroid_staebe_store_List[j])):
            #if value_is_close_to(centroid_staebe_store_List[i][n][0][0], centroid_staebe_store_List[j][a][0][0]) and value_is_close_to(centroid_staebe_store_List[i][n][0][0], centroid_staebe_store_List[j][a][1][0]):
            if check_if_connection(centroid_staebe_store_List[i][n][0], centroid_staebe_store_List[i][n][1], centroid_staebe_store_List[j][a][0], centroid_staebe_store_List[j][a][1]):
              if not check_if_centroid_between_connection(centroid_staebe_store_List[i][n][0], centroid_staebe_store_List[j][a][0], centroids):
                #print(f'{(centroid_staebe_store_List[i][n][0], centroid_staebe_store_List[j][a][0])}: are close and stored in{[i,j]}')
                output_image = draw_points_on_image([centroid_staebe_store_List[i][n][0], centroid_staebe_store_List[j][a][0]], output_image, COLOR='BLUE')
                connection_map.append([(i,n), (j,a)])
            else:
              #print('Is not near any point of anything')
              pass
  connection_map = check_for_doubles_in_connection_map(connection_map)    # To clear doubles cause da kamen immer alles doppelt in connection map

  #show_image_in_size(output_image)
  return connection_map, output_image
      #else:
        #print('i!=j')

def check_directions(centroids):
  for centroid in centroids:
    direction = [0,0]
    for stab in centroid[2]:
      if centroid[0][0] > stab[1][0]:
        direction[0] = -1
      elif centroid[0][0] < stab[1][0]:
        direction[0] = 1
      if centroid[0][1] > stab[1][1]:
        direction[1] = -1
      elif centroid[0][1] < stab[1][1]:
        direction[1] = 1
      stab.append(direction)
  return centroids

def display_GUI(centroids, match_image):
  app = QApplication(sys.argv)
  GUI = ImageViewer()
  image_with_label_array = []
  for centroid in centroids:
    img = check_image_in_part(match_image, centroid[0])
    label = centroid[1]
    image_with_label_array.append((img, label))
  GUI.render_images(image_with_label_array)
  GUI.show()
  

def sort_folder_for_data_pipeline():
  destination_path = 'test_1'

  path_to_folders = ['label_programm/test_label','content/data/train','content/data/validation']
  gelenke, festlager, loslager, biegesteife_ecke, normalkraft_gelenk = [], [], [], [], []
  hirarchy = [gelenke, festlager, loslager, biegesteife_ecke, normalkraft_gelenk]

  for path in path_to_folders:
    print(sorted(os.listdir(path)))
    for i, label_path in enumerate(sorted(os.listdir(path))):
      for image_path in sorted(os.listdir(f'{path}/{label_path}')):
        #print(f'{path}/{label_path}/{image_path}')
        #if f'{path}/{label_path}/{image_path}' in hirarchy[i]:
        #  print('Stomething aint right')
        hirarchy[i].append(f'{path}/{label_path}/{image_path}')
  

  if not os.path.exists(destination_path):
    print(f'Path did not Exist I created one fore you, you little yapa: {destination_path}')
    os.mkdir(destination_path)
  if not os.path.exists(f'{destination_path}/train'):
    os.mkdir(f'{destination_path}/train')
  if not os.path.exists(f'{destination_path}/validation'):
    os.mkdir(f'{destination_path}/validation')

  for i, element in enumerate(hirarchy):
    random.shuffle(element)
    for i, image in enumerate(element[:int(len(element)//2)]):
      label_name = image.split('/')[-2]
      img_name =  image.split('/')[3]

      if not os.path.exists(f'{destination_path}/train/{label_name}'):   #nICHT OPTIMAL
        os.mkdir(f'{destination_path}/train/{label_name}')

      shutil.copy(image, f'{destination_path}/train/{label_name}/{i}.jpg')
    
    for i, image in enumerate(element[int(len(element)//2):]):
      label_name = image.split('/')[-2]
      img_name =  image.split('/')[3]

      if not os.path.exists(f'{destination_path}/validation/{label_name}'):   #nICHT OPTIMAL
        os.mkdir(f'{destination_path}/validation/{label_name}')

      shutil.copy(image, f'{destination_path}/validation/{label_name}/{i}.jpg')
    
    print(f'{i}: hat {len(element)} Elemente')
      
def handle_main_for_GUI(match_image):
  image_1, image_2 = main(match_image)
  return image_1, image_2


def save_all_part_image_with_percentage(centroids, match_image):
  array = []
  for centroid in centroids:
    part_image = check_image_in_part(match_image,centroid[0])
    array.append([part_image, centroid[1]])
  return array
