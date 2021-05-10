import os
import sys
import cv2
import time
import torch
from vidgear.gears import CamGear
import numpy as np

sys.path.insert(1, os.getcwd())
from Python.hrnet_implementation.SimpleHRNet import SimpleHRNet
from Python.hrnet_implementation.misc.utils import find_person_id_associations

###
filename = 'Python/hrnet_implementation/video_cut.mp4'
image_resolution = (384, 288)
device = torch.device('cpu')
camera_id = 0
single_person = True
disable_tracking = False
max_batch_size=16
hrnet_c = 48
hrnet_j = 17
hrnet_m = 'HRNet'
hrnet_weights = "Python/hrnet_implementation/pose_hrnet_w48_384x288.pth"
hrnet_joints_set = 'coco'

keypoints =  {
    0: "nose",
    1: "left_eye",
    2: "right_eye",
    3: "left_ear",
    4: "right_ear",
    5: "left_shoulder",
    6: "right_shoulder",
    7: "left_elbow",
    8: "right_elbow",
    9: "left_wrist",
    10: "right_wrist",
    11: "left_hip",
    12: "right_hip",
    13: "left_knee",
    14: "right_knee",
    15: "left_ankle",
    16: "right_ankle"
}
keypoints =  {
    3: "left_ear",
    4: "right_ear",
    5: "left_shoulder",
    6: "right_shoulder",
    11: "left_hip",
    12: "right_hip",
    13: "left_knee",
    14: "right_knee",
    15: "left_ankle",
    16: "right_ankle"
}
skeleton = [(3, 5), (5, 11), (11, 13), (13, 15), (4, 6), (6, 12), (12, 14), (14, 16)]
###

class PoseEstimation:
    def __init__(self, filename):
        if filename is not None:
            # rotation_code = check_video_rotation(filename)
            self.video = cv2.VideoCapture(filename)
            assert self.video.isOpened()
        else:
            rotation_code = None
            self.video = cv2.VideoCapture(camera_id)
            assert self.video.isOpened()

        self.model = SimpleHRNet(
            hrnet_c,
            hrnet_j,
            hrnet_weights,
            model_name=hrnet_m,
            resolution=image_resolution,
            multiperson=not single_person,
            return_bounding_boxes=not disable_tracking,
            max_batch_size=max_batch_size,
            device=device
        )

        if not disable_tracking:
            self.prev_boxes = None
            self.prev_pts = None
            self.prev_person_ids = None
            self.next_person_id = 0

    def predict_and_draw(self, frame):
        t = time.time()
        frame = frame[:, 120:840]
        pts = self.model.predict(frame)

        if not disable_tracking:
            boxes, pts = pts

        if not disable_tracking:
            if len(pts) > 0:
                if self.prev_pts is None and self.prev_person_ids is None:
                    person_ids = np.arange(self.next_person_id, len(pts) + self.next_person_id, dtype=np.int32)
                    self.next_person_id = len(pts) + 1
                else:
                    boxes, pts, person_ids = find_person_id_associations(
                        boxes=boxes, pts=pts, prev_boxes=self.prev_boxes, prev_pts=self.prev_pts, prev_person_ids=self.prev_person_ids,
                        next_person_id=self.next_person_id, pose_alpha=0.2, similarity_threshold=0.4, smoothing_alpha=0.1,
                    )
                    self.next_person_id = max(self.next_person_id, np.max(person_ids) + 1)
            else:
                person_ids = np.array((), dtype=np.int32)

            self.prev_boxes = boxes.copy()
            self.prev_pts = pts.copy()
            self.prev_person_ids = person_ids

        else:
            person_ids = np.arange(len(pts), dtype=np.int32)

        drawed_img = frame
        points = pts[0]
        for i, pt in enumerate(points):
            if (i in keypoints.keys()) and (pt[2] > 0.5):
                if i in (3, 5, 11, 13, 15):
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 255)
                cv2.circle(drawed_img, (int(pt[1]), int(pt[0])), 5, color, -1)
                
        for pt1, pt2 in skeleton:
            if points[pt1][2] > 0.5 and points[pt2][2] > 0.5:
                if pt1%2 == 1:
                    color = (200, 0, 0)
                else:
                    color = (0, 0, 200)
                cv2.line(drawed_img, (int(points[pt1][1]), int(points[pt1][0])), (int(points[pt2][1]), int(points[pt2][0])), color, 2)
        
        v1, v2 = (points[5] - points[3])[:2], (points[5] - points[11])[:2]
        cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        rad1 = np.arccos(cos_theta) / np.pi * 180

        v1, v2 = (points[6] - points[4])[:2], (points[6] - points[12])[:2]
        cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        rad2 = np.arccos(cos_theta) / np.pi * 180
        
        fps = 1. / (time.time() - t)
        # print(f'\rframerate: {fps:.3}, rad : {rad:.5f}', end='')
        mean_rad = (rad1+rad2)/2
        cv2.putText(drawed_img, f'{max(rad1, rad2):.3f} degree', (int(points[5][1]+20), int(points[5][0])), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
        print(f'{fps:.2f}, left : {rad1:.3f}, right : {rad2:.3f}, mean : {mean_rad:.3f}')

        return drawed_img, max(rad1, rad2)


    def test(self):
        while True:
            t = time.time()

            if filename is not None:
                ret, frame = self.video.read()
                frame = frame[:, 120:840]
                if not ret:
                    break
                # if rotation_code is not None:
                #     frame = cv2.rotate(frame, rotation_code)
            else:
                frame = self.video.read()
                if frame is None:
                    break

            for _ in range(15):
                self.video.read()

            pts = self.model.predict(frame)

            if not disable_tracking:
                boxes, pts = pts

            if not disable_tracking:
                if len(pts) > 0:
                    if self.prev_pts is None and self.prev_person_ids is None:
                        person_ids = np.arange(self.next_person_id, len(pts) + self.next_person_id, dtype=np.int32)
                        self.next_person_id = len(pts) + 1
                    else:
                        boxes, pts, person_ids = find_person_id_associations(
                            boxes=boxes, pts=pts, prev_boxes=self.prev_boxes, prev_pts=self.prev_pts, prev_person_ids=self.prev_person_ids,
                            next_person_id=self.next_person_id, pose_alpha=0.2, similarity_threshold=0.4, smoothing_alpha=0.1,
                        )
                        self.next_person_id = max(self.next_person_id, np.max(person_ids) + 1)
                else:
                    person_ids = np.array((), dtype=np.int32)

                self.prev_boxes = boxes.copy()
                self.prev_pts = pts.copy()
                self.prev_person_ids = person_ids

            else:
                person_ids = np.arange(len(pts), dtype=np.int32)

            drawed_img = frame
            points = pts[0]
            for i, pt in enumerate(points):
                if (i in keypoints.keys()) and (pt[2] > 0.5):
                    if i in (3, 5, 11, 13, 15):
                        color = (255, 0, 0)
                    else:
                        color = (0, 0, 255)
                    cv2.circle(drawed_img, (int(pt[1]), int(pt[0])), 5, color, -1)
                    
            for pt1, pt2 in skeleton:
                if points[pt1][2] > 0.5 and points[pt2][2] > 0.5:
                    if pt1%2 == 1:
                        color = (200, 0, 0)
                    else:
                        color = (0, 0, 200)
                    cv2.line(drawed_img, (int(points[pt1][1]), int(points[pt1][0])), (int(points[pt2][1]), int(points[pt2][0])), color, 2)
            
            v1, v2 = (points[5] - points[3])[:2], (points[5] - points[11])[:2]
            cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            rad1 = np.arccos(cos_theta) / np.pi * 180

            v1, v2 = (points[6] - points[4])[:2], (points[6] - points[12])[:2]
            cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            rad2 = np.arccos(cos_theta) / np.pi * 180
            
            fps = 1. / (time.time() - t)
            # print(f'\rframerate: {fps:.3}, rad : {rad:.5f}', end='')
            mean_rad = (rad1+rad2)/2
            cv2.putText(drawed_img, f'{max(rad1, rad2):.3f} degree', (int(points[5][1]+20), int(points[5][0])), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
            print(f'{fps:.2f}, left : {rad1:.3f}, right : {rad2:.3f}, mean : {mean_rad:.3f}')

            cv2.imshow('frame.png', drawed_img)
            k = cv2.waitKey(1)
            if k == 27:  # Esc button
                self.video.release()
                break

        cv2.destroyAllWindows()

if __name__ == '__main__':
    pe = PoseEstimation(filename=filename)
    pe.test()