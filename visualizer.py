from base_functions import show_image_in_size

import numpy as np
import cv2

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

  def add_black_pixels_to_image(self, direction_vector, n):
    # Kann vieleicht optimiert werden, und smarter gelöst werden!!
    print(direction_vector)
    if direction_vector == [1,0]:
      self.output_img = cv2.copyMakeBorder(self.output_img, top=0, bottom=0, left=0, right=self.element_length*n, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    elif direction_vector == [-1,0]:
      self.output_img = cv2.copyMakeBorder(self.output_img, top=0, bottom=0, left=self.element_length*n, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    elif direction_vector == [0,-1]:
      self.output_img = cv2.copyMakeBorder(self.output_img, top=self.element_length*n, bottom=0, left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    elif direction_vector == [0,1]:
      self.output_img = cv2.copyMakeBorder(self.output_img, top=0, bottom=self.element_length*n, left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    else:
      print('Wrong, WHERE!')


  def draw_centroid(self, anknupf_pkt, centroid):
    pts_oriantation_up = np.array([(anknupf_pkt[0], anknupf_pkt[1] - self.a), (anknupf_pkt[0] + self.a, anknupf_pkt[1] + self.a), (anknupf_pkt[0] - self.a, anknupf_pkt[1] + self.a)], np.int32)
    pts = pts_oriantation_up.reshape((-1,1,2))
    cv2.polylines(self.output_img,[pts],True,(0,255,255))

    self.draw_stab(anknupf_pkt, centroid[2][1][2], 1)

  def draw_stab(self, point ,direction_vector, n):
    self.add_black_pixels_to_image(direction_vector, n)
    print(int(self.element_length*n*direction_vector[1]))
    cv2.line(self.output_img, (point , (point[0] + int((self.element_length/2 + self.element_length*n)*direction_vector[0]), point[1] + int(self.element_length*n*direction_vector[1]))),(255,0,0),1)

  def draw_centroids(self):
    centroid = self.centroids[0]
    self.draw_centroid((self.element_length/2,self.element_length/2), centroid)

  def show(self):
    show_image_in_size(self.output_img)