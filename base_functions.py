import cv2
import numpy as np

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
  cv2.imshow('Image', display_img)


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

def get_max_array(array):
  if max(array) != 0.0:
    max_indices = [i for i, x in enumerate(array) if x == max(array)]
  else:
    max_indices = [None]

  if len(max_indices) > 1:
    max_indices = kondense_border_max_array_to_value(max_indices)
  return max_indices

