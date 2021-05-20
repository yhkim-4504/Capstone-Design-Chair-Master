import numpy as np
import cv2
import math
from random import randint
from typing import Sequence

WAIST_POS = (204, 356)
NECK_POS = (190, 130)
PRESSURE_SENSOR_POS_LIST = [(324, 431), (227, 485), (313, 558), (412, 502)]
LENGTH_OF_TRIANGLE = 10
DERIVATIVE_VALUE = (425-356) / (310-204)

class SensorVisualization:
    def __init__(self, filepath: str) -> None:
        # 이미지 로드 및 압력센서 원형 그리기
        self.org_img = cv2.imread(filepath)
        self.h, self.w = self.org_img.shape[:2]

        # 초음파센서 측정선 각도정의
        self.theta = math.atan(DERIVATIVE_VALUE)

        # 허리 및 목 시작점 정의
        self.waist_pos = WAIST_POS
        self.neck_pos = NECK_POS

        # 화살표(삼각형) 좌표 및 회전변환
        r = LENGTH_OF_TRIANGLE
        tri_x = abs(r * math.cos(math.pi/6))
        tri_y = abs(r * math.sin(math.pi/6))

        self.tri_two = np.dot(np.array([[math.cos(self.theta), -math.sin(self.theta)], [math.sin(self.theta), math.cos(self.theta)]]), np.array([-tri_x, tri_y]))
        self.tri_three = np.dot(np.array([[math.cos(self.theta), -math.sin(self.theta)], [math.sin(self.theta), math.cos(self.theta)]]), np.array([-tri_x, -tri_y]))

        # 압력센서 위치 정의
        self.pos_list = PRESSURE_SENSOR_POS_LIST

    # 테스트함수
    def test(self) -> None:
        self.draw_base_pressure_circles(self.org_img)

        for _ in range(600):
            # 센서값 정의
            pressure_sensors = [randint(3, 60), randint(3, 60), randint(3, 60), randint(3, 60)]
            waist_sonic, neck_sonic = randint(10, 90), randint(10, 90)

            # 시각화
            overlayed_img = self.visualize(self.org_img, pressure_sensors, waist_sonic, neck_sonic)

            # 이미지 표시 및 종료조건
            cv2.imshow('image', overlayed_img)
            if cv2.waitKey(300) == ord('q'):
                break

        cv2.destroyAllWindows()

    # 센서값을 받아서 시각화(draw img with sensors)
    def visualize(self, img: np.ndarray, pressure_sensors: Sequence, waist_sonic: int, neck_sonic: int) -> np.ndarray:
        overlay = img.copy()

        # 센서값에 따른 원 그리기
        for pos, sensor_value in zip(self.pos_list, pressure_sensors):
            cv2.circle(overlay, pos, sensor_value, [40, 40, 255], -1)

        # 알파채널을 이용한 블랜드합성
        alpha = 0.4
        overlayed_img = cv2.addWeighted(self.org_img, 1-alpha, overlay, alpha, 0)
        
        # 허리와 목 부분 화살표(초음파센서) 그리기
        self.draw_arrow(self.waist_pos, waist_sonic, overlayed_img)
        self.draw_arrow(self.neck_pos, neck_sonic, overlayed_img)

        return overlayed_img, pressure_sensors, waist_sonic, neck_sonic

    def draw_arrow(self, org_pos: Sequence, r: int, img: np.ndarray) -> None:  # 화살표그리기
        # 축 각도의 길이가 r인 선 그리기
        new_x, new_y = round(org_pos[0]+abs(r * math.cos(self.theta))), round(org_pos[1]+abs(r * math.sin(self.theta)))
        cv2.line(img, org_pos, (new_x, new_y), (255, 0, 0), 2)

        # 회전변환한 삼각형 좌표를 이용하여 polygon 그리기
        tri_pos = [new_x, new_y]
        pts = np.array([tri_pos, np.round(tri_pos+self.tri_two), np.round(tri_pos+self.tri_three)], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(img, [pts], True, (255,0,0), 2)

    def draw_base_pressure_circles(self, img: np.ndarray) -> None:  # 원본이미지에 압력센서 원형라인 그리기
        for pos in self.pos_list:
            for i in range(10, 0, -1):
                circle_range = self.create_circular_mask(self.h, self.w, center=pos, radius=i*6, in_radius=(i-1)*6)
                img[circle_range] = np.uint8(img[circle_range] * 0.04*i)

    @staticmethod
    def create_circular_mask(h: int, w: int, center=None, radius=None, in_radius=0) -> np.ndarray:  # 원형마스크 생성함수

        if center is None: # use the middle of the image
            center = (int(w/2), int(h/2))
        if radius is None: # use the smallest distance between the center and image walls
            radius = min(center[0], center[1], w-center[0], h-center[1])

        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
        
        mask = (in_radius <= dist_from_center) & (dist_from_center <= radius)
        
        return mask

if __name__ == '__main__':
    sv = SensorVisualization(filepath='Python/imgs/chair_axis.png')
    sv.test()
