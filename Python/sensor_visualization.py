import numpy as np
import cv2
import math
from random import randint

class SensorVisualization:
    def __init__(self, filepath):
        # 이미지 로드 및 압력센서 원형 그리기
        self.org_img = cv2.imread(filepath)
        self.h, self.w = self.org_img.shape[:2]

        # 초음파센서 측정선 기울기 및 각도정의
        self.der = math.atan((425-356) / (310-204))
        self.theta = math.tan(self.der)

        # 허리 및 목 시작점 정의
        self.waist_pos = (204, 356)
        self.neck_pos = (190, 130)

        # 화살표(삼각형) 좌표 및 회전변환
        r = 10
        tri_x = abs(r * math.cos(math.pi/6))
        tri_y = abs(r * math.sin(math.pi/6))

        self.tri_two = np.dot(np.array([[math.cos(self.theta), -math.sin(self.theta)], [math.sin(self.theta), math.cos(self.theta)]]), np.array([-tri_x, tri_y]))
        self.tri_three = np.dot(np.array([[math.cos(self.theta), -math.sin(self.theta)], [math.sin(self.theta), math.cos(self.theta)]]), np.array([-tri_x, -tri_y]))

        # 압력센서 위치 정의
        self.pos_list = [(324, 431), (227, 485), (313, 558), (412, 502)]

    def test(self):
        self.draw_base_pressure_circles(self.org_img)

        for _ in range(600):
            overlay = self.org_img.copy()
            
            for pos in self.pos_list:
                cv2.circle(overlay, pos, randint(3, 60), [40, 40, 255], -1)
            alpha = 0.4
            overlayed_img = cv2.addWeighted(self.org_img, 1-alpha, overlay, alpha, 0)
            
            r = randint(10, 90)
            new_x, new_y = self.waist_pos[0]+abs(r * math.cos(self.theta)), self.waist_pos[1]+abs(r * math.sin(self.theta))
            cv2.line(overlayed_img, self.waist_pos, (round(new_x), round(new_y)), (255, 0, 0), 2)
            tri_pos = [round(new_x), round(new_y)]
            pts = np.array([tri_pos, np.round(tri_pos+self.tri_two), np.round(tri_pos+self.tri_three)], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(overlayed_img, [pts], True, (255,0,0), 2)
            
            r = randint(10, 90)
            new_x, new_y = self.neck_pos[0]+abs(r * math.cos(self.theta)), self.neck_pos[1]+abs(r * math.sin(self.theta))
            cv2.line(overlayed_img, self.neck_pos, (round(new_x), round(new_y)), (255, 0, 0), 2)
            tri_pos = [round(new_x), round(new_y)]
            pts = np.array([tri_pos, np.round(tri_pos+self.tri_two), np.round(tri_pos+self.tri_three)], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(overlayed_img, [pts], True, (255,0,0), 2)

            cv2.imshow('image',overlayed_img)

            if cv2.waitKey(300) == ord('q'):
                break
        cv2.destroyAllWindows()

    def draw_base_pressure_circles(self, img):
        for pos in self.pos_list:
            for i in range(10, 0, -1):
                circle_range = self.create_circular_mask(self.h, self.w, center=pos, radius=i*6, in_radius=(i-1)*6)
                img[circle_range] = np.uint8(img[circle_range] * 0.04*i)

    @staticmethod
    def create_circular_mask(h, w, center=None, radius=None, in_radius=0):  # 원형마스크 생성함수

        if center is None: # use the middle of the image
            center = (int(w/2), int(h/2))
        if radius is None: # use the smallest distance between the center and image walls
            radius = min(center[0], center[1], w-center[0], h-center[1])

        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
        
        mask = (in_radius <= dist_from_center) & (dist_from_center <= radius)
        
        return mask

if __name__ == '__main__':
    sv = SensorVisualization(filepath='Python/chair_axis.png')
    sv.test()

# img = cv2.imread('Python/chair_axis.png')
# h, w = img.shape[:2]
# der = math.atan((425-356) / (310-204))
# theta = math.tan(der)

# waist_pos = (204, 356)
# neck_pos = (190, 130)
# print(f'derivative : {der:.5}, theta : {theta:.5} radian')

# r = 10
# tri_x = abs(r * math.cos(math.pi/6))
# tri_y = abs(r * math.sin(math.pi/6))

# tri_two = np.dot(np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]), np.array([-tri_x, tri_y]))
# tri_three = np.dot(np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]), np.array([-tri_x, -tri_y]))
# print(tri_two, tri_three)

# pos_list = [(324, 431), (227, 485), (313, 558), (412, 502)]
# for pos in pos_list:
#     for i in range(10, 0, -1):
#         circle_range = create_circular_mask(h, w, center=pos, radius=i*6, in_radius=(i-1)*6)
#         img[circle_range] = np.uint8(img[circle_range] * 0.04*i)

# for _ in range(600):
#     overlay = img.copy()
    
#     for pos in pos_list:
#         cv2.circle(overlay, pos, randint(3, 60), [40, 40, 255], -1)
#     alpha = 0.4
#     overlayed_img = cv2.addWeighted(img, 1-alpha, overlay, alpha, 0)
    
#     r = randint(10, 90)
#     new_x, new_y = waist_pos[0]+abs(r * math.cos(theta)), waist_pos[1]+abs(r * math.sin(theta))
#     cv2.line(overlayed_img, waist_pos, (round(new_x), round(new_y)), (255, 0, 0), 2)
#     tri_pos = [round(new_x), round(new_y)]
#     pts = np.array([tri_pos, np.round(tri_pos+tri_two), np.round(tri_pos+tri_three)], np.int32)
#     pts = pts.reshape((-1, 1, 2))
#     cv2.polylines(overlayed_img, [pts], True, (255,0,0), 2)
    
#     r = randint(10, 90)
#     new_x, new_y = neck_pos[0]+abs(r * math.cos(theta)), neck_pos[1]+abs(r * math.sin(theta))
#     cv2.line(overlayed_img, neck_pos, (round(new_x), round(new_y)), (255, 0, 0), 2)
#     tri_pos = [round(new_x), round(new_y)]
#     pts = np.array([tri_pos, np.round(tri_pos+tri_two), np.round(tri_pos+tri_three)], np.int32)
#     pts = pts.reshape((-1, 1, 2))
#     cv2.polylines(overlayed_img, [pts], True, (255,0,0), 2)

#     cv2.imshow('image',overlayed_img)
#     # cv2.imshow('overlayimage',overlay)
#     if cv2.waitKey(300) == ord('q'):
#         break
# cv2.destroyAllWindows()