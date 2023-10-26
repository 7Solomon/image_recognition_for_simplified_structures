# -*- coding: utf-8 -*-
"""image_analyses_v2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10rKuAJ9cMG-5ah8Nnmz4ZdpZ6mMu5xfn
"""

from google.colab import drive

drive.mount('/content/drive')

import cv2
import os
import numpy as np

from google.colab.patches import cv2_imshow

def mask_image(img):
  gray_img = cv2.cvtColor(img , cv2.COLOR_BGR2GRAY)
  blurred = cv2.GaussianBlur(gray_img, (13, 13), 0)
  threshold = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
  #cv2_imshow(threshold)
  #cv2.imwrite('output_threshold.png', threshold)   #<-- Für Download für Templates
  return threshold

def delete_invisible_folder(dir):
  new_dir = []
  for file_name in dir:
    if file_name != '.ipynb_checkpoints':
      new_dir.append(file_name)
  return new_dir

def show_image_in_size(processed_img):
  display_width = 600
  # Resize the image for display while maintaining the aspect ratio
  aspect_ratio = processed_img.shape[1] / processed_img.shape[0]
  display_height = int(display_width / aspect_ratio)
  display_img = cv2.resize(processed_img, (display_width, display_height))
  # Display the resized image
  cv2_imshow(display_img)

def draw_points_on_image(points, image, COLOR='RED', S_Counter=0):
    if COLOR == 'RED':
        _color = (255, 0, 0)
    elif COLOR == 'BLUE':
        _color = (0, 0, 255)
    elif COLOR == 'GREEN':
        _color = (0, 255, 0)
    else:
      _color = (255, 0, 0)

    output_img = image.copy()
    def process_point(point, S_Counter):
      if isinstance(point, tuple) and len(point) == 2:
        center = tuple(map(int, point))
        cv2.circle(output_img, center, 10, _color, 5)
      elif isinstance(point, np.ndarray) and point.shape == (2,):
        center = tuple(map(int, point.tolist()))
        cv2.circle(output_img, center, 10, _color, 5)
      elif isinstance(point, (list, np.ndarray)):
        if isinstance(point, list):
          point = np.array(point, dtype=np.int32)

        if point.shape[1] != 2:
          print('Invalid shape of array. Must be Nx2.')
          return

        S_Counter += 1
        if S_Counter > 5:
          print('COUNTER ÜBERSCHRITTEN!')
          return

        for sub_point in point:
          process_point(sub_point, S_Counter)

    for point_group in points:
      process_point(point_group, S_Counter)

    return output_img

def is_in_range(p1, p2, range_distance=70):
    p1 = np.array(p1)
    p2 = np.array(p2)

    distance = np.linalg.norm(p1 - p2)

    # Check if the distance is less than or equal to the range_distance
    return distance <= range_distance

def value_is_close_to(value1, value2, th = 10):
  if value1 - th < value2 and value1 + th > value2 or value2 - th < value1 and value2 + th > value1:
    return True
  else:
    return False


def check_image_in_part(image, point, a = 60):
  dx_plus, dx_minus, dy_plus, dy_minus = max(0 ,int(point[0]) + a), max(0 ,int(point[0]) - a), max(0 ,int(point[1])) + a, max(0 ,int(point[1]) - a)
  part_of_image = image[dy_minus:dy_plus, dx_minus:dx_plus]
  return part_of_image

def generate_templates(dir):
  template_imgs = []
  template_dir = delete_invisible_folder(os.listdir(dir))

  for template in template_dir:
    template_imgs.append(cv2.imread(f'{dir}/{template}'))
  return template_imgs

def convert_2d_array_to_image(array):
  array = np.array(array)

  min_value = np.min(array)
  max_value = np.max(array)

  if max_value - min_value == 0:
    normalized_array = np.zeros_like(array, dtype=np.uint8)
    #print('Es gibt nur schwarze pixel')
  else:
    normalized_array = ((array - min_value) / (max_value - min_value) * 255).astype(np.uint8)

  return normalized_array

def create_image_from_borders(up, down, left, right):
  image = np.zeros((len(left), len(up)))
  image[0] = up
  image[len(image)-1] = down
  for i, px in enumerate(left):
    image[i][0] = px
  for i, px in enumerate(right):
    image[i][len(down)-1] = px
  return image

def kondense_border_max_array_to_value(max_array):
  # Muss noch geaded wer, dass wenn zwei linien am Rand sind, dass dann geclustert wird oder so
  return [int(np.median(max_array))]

import cv2
import numpy as np
from sklearn.cluster import DBSCAN
from matplotlib import pyplot as plt

from scipy.spatial import cKDTree

def local_template_matching(template_image, match_image):
  SIFT = cv2.SIFT_create()
  kp1, des1 = SIFT.detectAndCompute(template_image, None)
  kp2, des2 = SIFT.detectAndCompute(match_image, None)
  bf = cv2.BFMatcher()

  matches = bf.match(des1, des2)
  matches = sorted(matches, key=lambda x: x.distance)

  matching_result_img = cv2.drawMatches(template_image, kp1, match_image, kp2, matches[:50], None)

  # Extract keypoints that were matched
  matched_kp = [kp2[match.trainIdx] for match in matches[:50]]
  matched_pts = np.float32([kp.pt for kp in matched_kp]).reshape(-1, 2)

  return matched_pts, matching_result_img


def dbscan_clustering(points_to_cluster, image_to_overlay, MODE=None):

  if MODE == None:
    eps, min_samples = 50, 3
  elif MODE == 'gelenk':
    eps, min_samples = 50, 3
  elif MODE == 'festlager':
    eps, min_samples = 50, 5

  dbscan = DBSCAN(eps=eps, min_samples=min_samples)
  labels = dbscan.fit_predict(points_to_cluster)

  final_cluster_pts, final_cluster_label = [], []
  for label in np.unique(labels):
    if label == -1:  # Skip noise points ka wie das fkt
        continue
    cluster_pts = points_to_cluster[labels == label] # Ich glaube ist zum matchen der gelabelten und dann adden der original koordinaten
    label_array = np.full((cluster_pts.shape[0], 1), label)


    final_cluster_pts.append(cluster_pts)
    final_cluster_label.append(label_array)

  output_img = draw_points_on_image(final_cluster_pts, image_to_overlay)

  if len(final_cluster_pts) > 0:          # sonst eror, Überprüfen ob das passt muss man
    final_cluster_pts = np.concatenate(final_cluster_pts)           # ka was concatenate macht aber es hat mir das sortier problem der arrays und das behaltenn der Tuple struktur gemacht
    final_cluster_label = np.concatenate(final_cluster_label)
  return final_cluster_pts, final_cluster_label, output_img


def sort_for_center_points(points, labels, image_to_overlay):
  points_sorted, pZ = [], []
  # sort nach labels
  if len(labels) != len(points):
    print('Länge labels und points stimmen nicht überein')
  for uLabel in np.unique(labels):
    for n in range(len(labels)):
      if labels[n] == uLabel:
        pZ.append(points[n])
    points_sorted.append(pZ)
    pZ = []

  centroids = []
  for points in points_sorted:
    sum_x = sum(point[0] for point in points)
    sum_y = sum(point[1] for point in points)

    centroid_x = sum_x / len(points)
    centroid_y = sum_y / len(points)
    centroids.append((centroid_x,centroid_y))

  # Zeichne centroid ein in Bild
  output_img = image_to_overlay.copy()
  for centroid in centroids:
    cv2.circle(output_img, (int(centroid[0]),int(centroid[1])), 10, (0,255,0), 5)

  return centroids, output_img

def get_obj(template_imgs, match_image, MODE=None):
  centroids_of_all_templates = []

  for template_img in template_imgs:
    matched_points, matched_image = local_template_matching(template_img, match_image)
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

def add_label(centroids, label):
  for i, centroid in enumerate(centroids):
    centroids[i] = (centroid, label)
  return centroids

def line_detection(image):
  #edges = cv2.Canny(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY), threshold1=40, threshold2=100)    # Macht die Lines zu Kurz, ist nicht hilfreich, da es schon ein binary bild ist
  output_image = image.copy()
  lines = cv2.HoughLinesP(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY), rho=7, theta=np.pi/180, threshold=150, minLineLength=120, maxLineGap=1)
  if lines is not None:
    for line in lines:
      x1, y1, x2, y2 = line[0]
      cv2.line(output_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
  return output_image, lines

def line_corner_analyses(centroids, match_image, to_draw_on_image):
  line_image, lines = line_detection(match_image)
  output_image = to_draw_on_image.copy()
  show_image_in_size(line_image)


  for i,centroid in enumerate(centroids):
    near_lines = []
    for line in lines:
      for point in line:
        if is_in_range(centroid[0], (point[0],point[1])):
          #print(f'{line} is near: {centroid}')
          cv2.line(output_image, (point[0], point[1]), (point[2], point[3]), (0, 0, 255), 2)
          near_lines.append([(point[0], point[1]), (point[2], point[3])])
        if is_in_range(centroid[0], (point[2],point[3])):
          #print(f'{line} is near: {centroid}')
          cv2.line(output_image, (point[0], point[1]), (point[2], point[3]), (0, 0, 255), 2)
          near_lines.append([(point[2], point[3]), (point[1], point[2])])
    centroids[i] = [centroid[0], centroid[1], near_lines]

  return centroids, output_image

def angle_analysis(centroids):
  for i, centroid in enumerate(centroids):
    vector_list = centroid[2]

    if len(vector_list) > 1 and len(vector_list) < 4:
      points1 = np.array(vector_list[0])
      points2 = np.array(vector_list[1])

      vector1 = points1[0] - points1[1]
      vector2 = points2[0] - points2[1]

      unit_vector1 = vector1 / np.linalg.norm(vector1)
      unit_vector2 = vector2 / np.linalg.norm(vector2)

      dot_product = np.dot(unit_vector1, unit_vector2)

      angle_radians = np.arccos(dot_product)
      angle_degrees = np.degrees(angle_radians)
      #print(f'degrees: {angle_degrees} for: {vector1}, {vector2}')

      if angle_degrees > 80 and angle_degrees < 100:
        angle_degrees = 90
      elif angle_degrees > 170 and angle_degrees < 190:
        angle_degrees = 180

      # Überarbeiten der Centroids
      centroids[i][2] = [centroid[2][0], angle_degrees]
    else:
      print('Mehr oder weniger als 2 linien bei einem Centroid, jetzt musst du dich leider darum kümmern')

  return centroids

def get_max_array(array):
  if max(array) != 0.0:
    max_indices = [i for i, x in enumerate(array) if x == max(array)]
  else:
    max_indices = [None]

  if len(max_indices) > 1:
    max_indices = kondense_border_max_array_to_value(max_indices)
  return max_indices



def check_if_stab(line, match_image):
  p1, p2 = line[0], line[1]
  if p1 != None and p2 != None:
    num_points = 100

    line_values = []
    for i in range(num_points):
      alpha = i / (num_points - 1)  # Interpolate between the two points
      x = int((1 - alpha) * p1[0] + alpha * p2[0])
      y = int((1 - alpha) * p1[1] + alpha * p2[1])
      if y < match_image.shape[0] and x < match_image.shape[1]:
        value = match_image[y, x]  # Get the pixel value at the current point
        line_values.append(value)
      else:
        pass
        #print('Point out of Bound, in "check_if_staebe"')

    line_values = np.array(line_values)
    if len(line_values) > 0:
      max_intensities = np.max(line_values, axis=1)
      max_indices = np.where(max_intensities == np.max(max_intensities))[0]
      if len(max_indices) > num_points/2:
        return True
      else:
        #print('len(max_indices) > num_points/2, nicht erfüllt')
        return False
    else:
      #print('point out of bound, bzw: len(line_values) > 0')
      return False
  else:
    #print('check_if_stab: p1 oder p2 None')
    return False



def iterate_through_borders(kords_up, kords_down, kords_left, kords_right, match_image, RASTER_A):
  output_image = match_image.copy()
  lines = []

  if kords_up != None:
    if kords_up[0] < len(match_image[0]) and kords_up[1] > 0:   # vielleciht noch linke kanten in if bedingung mit einpfelgen
      array_up, array_down, array_left, array_right, border_image, part_image = get_borders_of_part_arround_point(kords_up,match_image, RASTER_A)
      new_kords_up, new_kords_down, new_kords_left, new_kords_right = border_check(kords_up, part_image, array_up,array_down, array_left, array_right, RASTER_A, match_image)
      if new_kords_up != None:
        cv2.line(output_image, (int(kords_up[0]),int(kords_up[1])) , (int(new_kords_up[0]),int(new_kords_up[1])), (255,0,0), 3)
        lines.append([kords_up, new_kords_up])

  if kords_down != None and kords_down[0] < len(match_image[0]):
    if kords_down[1] < len(match_image):
      array_up, array_down, array_left, array_right, border_image, part_image = get_borders_of_part_arround_point(kords_down,match_image, RASTER_A)
      new_kords_up, new_kords_down, new_kords_left, new_kords_right = border_check(kords_down, part_image, array_up,array_down, array_left, array_right, RASTER_A, match_image)
      if new_kords_down != None:
        cv2.line(output_image, (int(kords_down[0]),int(kords_down[1])) , (int(new_kords_down[0]),int(new_kords_down[1])), (255,0,0), 3)
        lines.append([kords_down, new_kords_down])

  if kords_left != None:
    array_up, array_down, array_left, array_right, border_image, part_image = get_borders_of_part_arround_point(kords_left,match_image, RASTER_A)
    new_kords_up, new_kords_down, new_kords_left, new_kords_right = border_check(kords_left, part_image, array_up,array_down, array_left, array_right, RASTER_A, match_image)
    if new_kords_left != None:
      cv2.line(output_image, (int(kords_left[0]),int(kords_left[1])) , (int(new_kords_left[0]),int(new_kords_left[1])), (255,0,0), 3)
      lines.append([kords_left, new_kords_left])

  if kords_right != None:
    array_up, array_down, array_left, array_right, border_image, part_image = get_borders_of_part_arround_point(kords_right,match_image, RASTER_A)
    new_kords_up, new_kords_down, new_kords_left, new_kords_right = border_check(kords_right, part_image, array_up,array_down, array_left, array_right, RASTER_A, match_image)
    if new_kords_right != None:
      cv2.line(output_image, (int(kords_right[0]),int(kords_right[1])) , (int(new_kords_right[0]),int(new_kords_right[1])), (255,0,0), 3)
      lines.append([kords_right, new_kords_right])

  #show_image_in_size(part_image)
  #show_image_in_size(output_image)
  return lines


def get_new_kords_from_border(center_point, BORDER, max_indices, CHECK_IMAGE_IN_PART_VARIABLE, RASTER_A):
  if max_indices[0] != None:
    if BORDER == 'up':
      new_kords = (center_point[0] - CHECK_IMAGE_IN_PART_VARIABLE + max_indices[0], center_point[1] - CHECK_IMAGE_IN_PART_VARIABLE - RASTER_A)
    elif BORDER == 'down':
      new_kords = (center_point[0] - CHECK_IMAGE_IN_PART_VARIABLE + max_indices[0], center_point[1] + CHECK_IMAGE_IN_PART_VARIABLE + RASTER_A)
    elif BORDER == 'left':
      new_kords = (center_point[0] - CHECK_IMAGE_IN_PART_VARIABLE - RASTER_A, center_point[1] - CHECK_IMAGE_IN_PART_VARIABLE + max_indices[0])
    elif BORDER == 'right':
      new_kords = (center_point[0] + CHECK_IMAGE_IN_PART_VARIABLE + RASTER_A, center_point[1] - CHECK_IMAGE_IN_PART_VARIABLE + max_indices[0])
    else:
      print('Border_type is not defined!')
      new_kords = None
  else:
    #print(f'no line on: {BORDER}')
    new_kords = None
  return new_kords

def border_check(center_point, part_image, array_up, array_down, array_left, array_right, RASTER_A, match_image):

  max_indices_up = get_max_array(array_up)
  max_indices_down = get_max_array(array_down)
  max_indices_left = get_max_array(array_left)
  max_indices_right = get_max_array(array_right)


  CHECK_IMAGE_IN_PART_VARIABLE = 60           # WICHTIG!!! Fals sich sie ändert muss das geändert werden
  new_kords_up = get_new_kords_from_border(center_point, 'up', max_indices_up, CHECK_IMAGE_IN_PART_VARIABLE, RASTER_A)       # nimmt den ersten max eintrag
  new_kords_down = get_new_kords_from_border(center_point, 'down', max_indices_down, CHECK_IMAGE_IN_PART_VARIABLE, RASTER_A)
  new_kords_left = get_new_kords_from_border(center_point, 'left', max_indices_left, CHECK_IMAGE_IN_PART_VARIABLE, RASTER_A)
  new_kords_right = get_new_kords_from_border(center_point, 'right', max_indices_right, CHECK_IMAGE_IN_PART_VARIABLE, RASTER_A)

  return new_kords_up, new_kords_down, new_kords_left, new_kords_right


def get_borders_of_part_arround_point(point,match_image, RASTER_A):

  part_image = check_image_in_part(match_image, point)

  array_left, array_right = [], []
  array_up, array_down = [], []

  #print('_____________UP, DOWN:')
  for y in range(len(part_image)):

    if y + RASTER_A < len(part_image) and len(part_image[0]) > RASTER_A:

      DATA_LEFT = np.array([[part_image[y + a][0 + b] / 255.0 for a in range(RASTER_A)] for b in range(RASTER_A)])
      DATA_RIGHT = np.array([[part_image[y + a][(len(part_image[y]) - RASTER_A) + b] / 255.0 for a in range(RASTER_A)] for b in range(RASTER_A)])

      sum_left = np.sum(DATA_LEFT)
      sum_right = np.sum(DATA_RIGHT)

      array_left.append(sum_left)
      array_right.append(sum_right)

    else:  # Dafür, dass arrays die richtighe dimesion haben, bessere Lösung muss später her
      array_left.append(0)
      array_right.append(0)

  #print('_____________Left,Right:')
  for x in range(len(part_image[0])):

    if x + RASTER_A < len(part_image[0]) and len(part_image) > RASTER_A:

      DATA_UP = np.array([[part_image[0 + a][x + b] / 255.0 for a in range(RASTER_A)] for b in range(RASTER_A)])
      DATA_DOWN = np.array([[part_image[(len(part_image) - RASTER_A) + a][x + b] / 255.0 for a in range(RASTER_A)] for b in range(RASTER_A)])

      sum_up = np.sum(DATA_UP)
      sum_down = np.sum(DATA_DOWN)

      array_up.append(sum_up)                   # ARRAYS_UP und so passen, habs kontrolliert
      array_down.append(sum_down)

    else:  # Dafür, dass arrays die richtighe dimesion haben, bessere Lösung muss später her
      array_up.append(0)
      array_down.append(0)
  border_image = convert_2d_array_to_image(create_image_from_borders(array_up, array_down, array_left, array_right))
  return array_up, array_down, array_left, array_right, border_image, part_image


def custome_line_detection(centroids, match_image):
  output_image = match_image.copy()
  RASTER_A = 6             # Für Abstand des Blurs und neuwahl der Kords
  per_centroid_lines = []
  for i, centroid in enumerate(centroids):
    array_up, array_down, array_left, array_right, border_image, part_image = get_borders_of_part_arround_point(centroid[0], match_image, RASTER_A)
    new_kords_up, new_kords_down, new_kords_left, new_kords_right = border_check(centroid[0], part_image, array_up,array_down, array_left, array_right, RASTER_A, match_image)
    lines = iterate_through_borders(new_kords_up, new_kords_down, new_kords_left, new_kords_right, match_image, RASTER_A)
    for line in lines:
      if check_if_stab(line, match_image):
        cv2.line(output_image, (int(line[0][0]), int(line[0][1])), (int(line[1][0]), int(line[1][1])), (0, 0, 255), 3)
        per_centroid_lines.append(line)
    centroids[i] = [centroid[0],centroid[1],per_centroid_lines]
    per_centroid_lines = []
  return centroids, output_image

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
    direction = (0,0)
    for stab in centroid[2]:
      if centroid[0][0] > stab[0]:
        direction[0] = -1
      elif centroid[0][0] > stab[0]:
        direction[0] = 1
      if centroid[0][1] > stab[1]:
        direction[1] = -1
      elif centroid[0][1] > stab[1]:
        direction[1] = 1
      centroid.append(direction)

import math

def add_black_pixels_to_image(WHERE, element_length, n, img):
  if WHERE == 'right':
    img = cv2.copyMakeBorder(img, top=0, bottom=0, left=0, right=element_length*n, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
  elif WHERE == 'left':
    img = cv2.copyMakeBorder(img, top=0, bottom=0, left=element_length*n, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
  elif WHERE == 'top':
    img = cv2.copyMakeBorder(img, top=element_length*n, bottom=0, left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
  elif WHERE == 'bot':
    img = cv2.copyMakeBorder(img, top=0, bottom=element_length*n, left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
  else:
    print('Wrong, WHERE!')
  return img

def check_for_point_left_top(centroids):
  nearest_point = (800,800)
  indx = None
  for i, centroid in enumerate(centroids):
    if centroid[0] < nearest_point:
      nearest_point = centroid[0]
      indx = i
  return indx

def draw_stab(point, angle, n, img):


  x = math.cos(math.radians(angle))

  cv2.line(img,point,(point[0]+L*n,point[1]+L*n),(255,0,0),5)


  show_image_in_size(img)

def draw_centroid(centroid, element_length, img, mittelpunkt = None):
  a = 10  # größe des centroids
  abstand_rand = 10

  if mittelpunkt is None:
    mittelpunkt = (int(element_length / 2), int(element_length / 2))

  # Draw Lager
  pts_oriantation_up = np.array([(int(mittelpunkt[0]), int(mittelpunkt[1] - a)), (int(mittelpunkt[0] + a), int(mittelpunkt[1]) + a), (int(mittelpunkt[0] - a), int(mittelpunkt[1] + a))], np.int32)
  pts = pts_oriantation_up.reshape((-1,1,2))
  cv2.polylines(img,[pts],True,(0,255,255))

  right_kords, bot_kords, left_kords, top_kords = None, None, None, None
  n = 1   # Ist länge des stabes

  # Zeichne alle stäbe um das lager in bestimmter reinfolge
  img = add_black_pixels_to_image('right', element_length, n, img)   # Der rechte stab wird zuerst gezeichnet
  cv2.line(img,mittelpunkt,(mittelpunkt[0] + element_length*n + int(element_length/2), mittelpunkt[1]),(255,0,0),1)
  right_kords = (mittelpunkt[0] + element_length*n + int(element_length/2), mittelpunkt[1])
  for i in range(len(centroid[3])):
    if i == 0:
      img = add_black_pixels_to_image('bot', element_length, n, img)
      cv2.line(img,mittelpunkt,(mittelpunkt[0], mittelpunkt[1] + element_length*n + int(element_length/2)),(255,0,0),1)
      bot_kords = (mittelpunkt[0], mittelpunkt[1] + element_length*n + int(element_length/2))
    elif i == 1:
      img = add_black_pixels_to_image('left', element_length, n, img)
      cv2.line(img,mittelpunkt,(mittelpunkt[0], mittelpunkt[1] - element_length*n - int(element_length/2)),(255,0,0),1)
      left_kords = (mittelpunkt[0], mittelpunkt[1] - element_length*n - int(element_length/2))
    elif i == 2:
      img = add_black_pixels_to_image('top', element_length, n, img)
      cv2.line(img,mittelpunkt,(mittelpunkt[0], mittelpunkt[1] - element_length*n - int(element_length/2)),(255,0,0),1)
      top_kords = (mittelpunkt[0], mittelpunkt[1] - element_length*n - int(element_length/2))
    else:
      print('sth went wrong in draw_centroid')
    return [right_kords, bot_kords, left_kords, top_kords], img

def draw_staebe(centroids, connection_map, idx, element_length, img, kords_array):
  for connect_stab in connection_map:
    for element in connect_stab:
      if element[0] == idx:
        print(connection_map)
        print(element[0])
        print(idx)
        kords_array, img = draw_centroid(centroids[element[0]], element_length, img, mittelpunkt=kords_array[element[1]])
        #img = draw_staebe(centroids, connection_map, , element_length, img, kords_array)
  return img

def draw_system(centroids, connection_map):
  element_length = 60
  img = np.zeros((element_length,element_length,3), np.uint8)

  first_centroid_indx = check_for_point_left_top(centroids)
  kords_array, img = draw_centroid(centroids[0], element_length, img)

  img = draw_staebe(centroids, connection_map, first_centroid_indx, element_length, img, kords_array)
  cv2_imshow(img)

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.models import load_model
from sklearn.model_selection import train_test_split


def download_raw_part_images(centroids, match_image, name):
  for i, centroid in enumerate(centroids):
    output_image = match_image.copy()
    part_image = check_image_in_part(output_image, centroid[0])
    success = cv2.imwrite(f'drive/MyDrive/ocr/raw_train_data/{name.split(".")[0]}_{i}.jpg', part_image)
    if success:
      print(f'Saved image {name.split(".")[0]}_{i}.jpg successfully')
    else:
      print(f'Error saving image {i}.jpg')

def split_data(image_height, image_width):
  batch_size = 5

  train_datagen = ImageDataGenerator(
    rescale=1.0/255.0,  # Rescale pixel values to [0, 1]
    rotation_range=20,  # Randomly rotate images
    width_shift_range=0.2,  # Randomly shift images horizontally
    height_shift_range=0.2,  # Randomly shift images vertically
    shear_range=0.2,  # Shear transformation
    zoom_range=0.2,  # Random zoom
    horizontal_flip=True,  # Randomly flip images horizontally
    fill_mode='nearest'  # Fill mode for new pixels after rotation or shifting
  )

  data_dir = 'drive/MyDrive/ocr/data'
  class_names = sorted(delete_invisible_folder(os.listdir(data_dir)))

  # Split data into training and validation sets
  train_dir, validation_dir = train_test_split(
  class_names, test_size=0.2, random_state=42)

  train_generator = train_datagen.flow_from_directory(
      os.path.join(data_dir, 'train'),
      target_size=(image_height, image_width),
      batch_size=batch_size,
      class_mode='categorical'
    )

  validation_generator = train_datagen.flow_from_directory(
        os.path.join(data_dir, 'validation'),
        target_size=(image_height, image_width),
        batch_size=batch_size,
        class_mode='categorical'
    )
  return train_generator, validation_generator

def define_neural_net(image_height, image_width, num_classes):
  model = Sequential()
  model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(image_height, image_width, 3)))
  model.add(MaxPooling2D((2, 2)))
  model.add(Conv2D(128, (3, 3), activation='relu'))
  model.add(MaxPooling2D((2, 2)))
  model.add(Flatten())
  model.add(Dense(64, activation='relu'))
  model.add(Dense(num_classes, activation='softmax'))  # num classes ist len(train_data)

  model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
  return model

def train_modell():
  num_epochs = 30  # Adjust the number of epochs as needed
  image_height, image_width = 120, 120

  train_generator, validation_generator = split_data(image_height, image_width)# Ist in get Imgae in part defined
  model = define_neural_net(image_height, image_width, len(train_generator.class_indices))

  history = model.fit(train_generator, epochs=num_epochs, validation_data=validation_generator, )
  model.save('drive/MyDrive/ocr/models/model_2.h5')
  print('---------- model_2 --------')
  print("Training accuracy:", history.history['accuracy'])
  print("Validation accuracy:", history.history['val_accuracy'])
  print("Training loss:", history.history['loss'])
  print("Validation loss:", history.history['val_loss'])
  print('---------- saved_model: -------')


def predict_on_data(img):
  loaded_model = load_model('drive/MyDrive/ocr/models/model_2.h5')
  img = img / 255.0       # Normalize
  img = np.expand_dims(img, axis=0)    # Add a batch dimension to the input image
  predictions = loaded_model.predict(img)
  return predictions

def check_centroid(centroid, match_image):
  output_image = match_image.copy()
  part_image = check_image_in_part(output_image, centroid[0])
  # Adde schwarze pixels das input shape stimmt
  if part_image.shape[0] != 120:
    part_image = cv2.copyMakeBorder(part_image, top=0, bottom=120-part_image.shape[0], left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
  if part_image.shape[1] != 120:
    part_image = cv2.copyMakeBorder(part_image, top=0, bottom=0, left=120-part_image.shape[1], right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))


  show_image_in_size(part_image)
  predictions = predict_on_data(part_image)
  switch_label = ['scheiß_ipynb_checkpoint','gelenk','festlager', 'loslager', 'b_ecke', 'n_gelenk']
  for i, predic in enumerate(predictions[0]):
    print(f'Es ist mit  {predic*100} %  --> {switch_label[i]}')

  if max(predictions[0]) > 0.5:
    idx = np.argmax(predictions[0])
    if centroid[1] == idx - 1:   # -1 wegen shceiß ipynb.checkpoint
      print(f'{ centroid[1], idx}: Found Correkt save_file')
    else:
      print(f'{ centroid[1], idx}: Found NOT Correkt')
      centroid[1] = [idx-1]
    return centroid
  else:
    print('No element Found')
    return None

train_modell()

def add_all_centroids(array, match_image):
  all_centroids_array = []
  for centroids in array:
    for centroid in centroids:
      centroid = check_centroid(centroid, match_image)
      if centroid != None:
        all_centroids_array.append(centroid)
  return all_centroids_array

from numpy.matrixlib.defmatrix import mat
import os

def main():

  images_dir = delete_invisible_folder(os.listdir('drive/MyDrive/ocr/raw_images'))
  _test_ = cv2.imread(f'drive/MyDrive/ocr/images/image (2).jpeg')
  match_image = cv2.cvtColor(mask_image(cv2.imread(f'drive/MyDrive/ocr/raw_images/{images_dir[0]}')), cv2.COLOR_GRAY2BGR)


  gelenk_templates = generate_templates('drive/MyDrive/ocr/templates/gelenke')
  festlager_templates = generate_templates('drive/MyDrive/ocr/templates/festlager')
  loslager_templates = generate_templates('drive/MyDrive/ocr/templates/loslager')
  biegesteife_ecke_templates = generate_templates('drive/MyDrive/ocr/templates/biegesteife_ecke')

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

  #centroids = add_all_centroids([staebe_of_gelenke, staebe_of_festlager, staebe_of_loslager, staebe_of_biegesteife_ecke], match_image)

  #download_raw_part_images(centroids, match_image, images_dir[4])




  angles = check_staebe(gelenk_centroids)
  connection_map, connection_img = connect_centroids(angles, match_image)

  System = Visualizer(gelenk_centroids,connection_map)
  System.draw_centroids()
  System.show()




  #draw_system(angles, connection_map)
  #show_image_in_size(connection_img)
  #show_image_in_size(staebe_of_gelenke_img)
  #show_image_in_size(staebe_of_festlager_img)
  #show_image_in_size(staebe_of_loslager_img)
  #show_image_in_size(staebe_of_biegesteife_ecke_img)



main()

class Visualizer:
  def check_for_point_left_top(self):
    nearest_point = (800,800)
    indx = None
    for i, centroid in enumerate(self.centroids):
      if centroid[0] < nearest_point:
        nearest_point = centroid[0]
        indx = i
    return indx

  def __init__(self, centroids, connection_map):
    self.centroids = centroids
    self.connection_map = connection_map

    # VARIABLES for Visualization
    self.element_length = 60
    self.a = 10

    self.top_left_indx = self.check_for_point_left_top()

    self.output_img = np.zeros((self.element_length,self.element_length,3), np.uint8)

  def add_black_pixels_to_image(self, WHERE, n):
    if WHERE == 'right':
      self.output_img = cv2.copyMakeBorder(self.output_img, top=0, bottom=0, left=0, right=self.element_length*n, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    elif WHERE == 'left':
      self.output_img = cv2.copyMakeBorder(self.output_img, top=0, bottom=0, left=self.element_length*n, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    elif WHERE == 'top':
      self.output_img = cv2.copyMakeBorder(self.output_img, top=self.element_length*n, bottom=0, left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    elif WHERE == 'bot':
      self.output_img = cv2.copyMakeBorder(self.output_img, top=0, bottom=self.element_length*n, left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    else:
      print('Wrong, WHERE!')


  def draw_centroid(self, anknupf_pkt):
    print([(anknupf_pkt[0], anknupf_pkt[1] - self.a), (anknupf_pkt[0] + self.a, anknupf_pkt[1] + self.a), (anknupf_pkt[0] - self.a, anknupf_pkt[1] + self.a)])
    pts_oriantation_up = np.array([(anknupf_pkt[0], anknupf_pkt[1] - self.a), (anknupf_pkt[0] + self.a, anknupf_pkt[1] + self.a), (anknupf_pkt[0] - self.a, anknupf_pkt[1] + self.a)], np.int32)
    pts = pts_oriantation_up.reshape((-1,1,2))
    cv2.polylines(self.output_img,[pts],True,(0,255,255))

  def draw_stab(self, point ,direction_vector, n):
    self.add_black_pixels_to_image(direction_vector, n)
    cv2.line(self.output_img, (point , (point[0] + int((self.element_length/2 + self.element_length*n)*direction_vector[0]), point[1] + self.element_length*n*direction_vector[1])),(255,0,0),1)

  def draw_centroids(self):
    self.draw_centroid((self.element_length/2,self.element_length/2))

  def show(self):
    show_image_in_size(self.output_img)