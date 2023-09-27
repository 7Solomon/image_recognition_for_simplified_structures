from base_functions import draw_points_on_image


import cv2
import numpy as np
from sklearn.cluster import DBSCAN
from matplotlib import pyplot as plt

from scipy.spatial import cKDTree



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
