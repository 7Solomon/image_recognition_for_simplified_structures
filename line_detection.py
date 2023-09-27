from base_functions import check_image_in_part
from base_functions import convert_2d_array_to_image
from base_functions import create_image_from_borders
from base_functions import get_max_array


import numpy as np
import cv2



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

