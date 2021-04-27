import numpy as np
import cv2
import math
from random import randint


def create_circular_mask(h, w, center=None, radius=None, in_radius=0):

    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    
    mask = (in_radius <= dist_from_center) & (dist_from_center <= radius)
    
    return mask

    
img = cv2.imread('Python/chair_axis.png')
h, w = img.shape[:2]
der = math.atan((425-356) / (310-204))
theta = math.tan(der)

waist_pos = (204, 356)
neck_pos = (190, 130)
print(f'derivative : {der:.5}, theta : {theta:.5} radian')

r = 10
tri_x = abs(r * math.cos(math.pi/6))
tri_y = abs(r * math.sin(math.pi/6))

tri_two = np.dot(np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]), np.array([-tri_x, tri_y]))
tri_three = np.dot(np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]), np.array([-tri_x, -tri_y]))
print(tri_two, tri_three)

pos_list = [(324, 431), (227, 485), (313, 558), (412, 502)]
for pos in pos_list:
    for i in range(10, 0, -1):
        circle_range = create_circular_mask(h, w, center=pos, radius=i*6, in_radius=(i-1)*6)
        img[circle_range] = np.uint8(img[circle_range] * 0.04*i)

for _ in range(100):
    overlay = img.copy()
    
    for pos in pos_list:
        cv2.circle(overlay, pos, randint(3, 60), [40, 40, 255], -1)
    alpha = 0.4
    overlayed_img = cv2.addWeighted(img, 1-alpha, overlay, alpha, 0)
    
    r = randint(10, 90)
    new_x, new_y = waist_pos[0]+abs(r * math.cos(theta)), waist_pos[1]+abs(r * math.sin(theta))
    cv2.line(overlayed_img, waist_pos, (round(new_x), round(new_y)), (255, 0, 0), 2)
    tri_pos = [round(new_x), round(new_y)]
    pts = np.array([tri_pos, np.round(tri_pos+tri_two), np.round(tri_pos+tri_three)], np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(overlayed_img, [pts], True, (255,0,0), 2)
    
    r = randint(10, 90)
    new_x, new_y = neck_pos[0]+abs(r * math.cos(theta)), neck_pos[1]+abs(r * math.sin(theta))
    cv2.line(overlayed_img, neck_pos, (round(new_x), round(new_y)), (255, 0, 0), 2)
    tri_pos = [round(new_x), round(new_y)]
    pts = np.array([tri_pos, np.round(tri_pos+tri_two), np.round(tri_pos+tri_three)], np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(overlayed_img, [pts], True, (255,0,0), 2)

    cv2.imshow('image',overlayed_img)
    # cv2.imshow('overlayimage',overlay)
    if cv2.waitKey(300) == ord('q'):
        break
cv2.destroyAllWindows()