import os
import sys
import argparse
import ast
import cv2
import time
import torch
from vidgear.gears import CamGear
import numpy as np

sys.path.insert(1, os.getcwd())
from Python.hrnet_implementation.SimpleHRNet import SimpleHRNet
from Python.hrnet_implementation.misc.visualization import draw_points_and_skeleton, joints_dict
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
###

if filename is not None:
    # rotation_code = check_video_rotation(filename)
    video = cv2.VideoCapture(filename)
    assert video.isOpened()
else:
    rotation_code = None
    video = cv2.VideoCapture(camera_id)
    assert video.isOpened()

model = SimpleHRNet(
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
    prev_boxes = None
    prev_pts = None
    prev_person_ids = None
    next_person_id = 0

while True:
    t = time.time()

    if filename is not None:
        ret, frame = video.read()
        frame = frame[:, 120:840]
        if not ret:
            break
        # if rotation_code is not None:
        #     frame = cv2.rotate(frame, rotation_code)
    else:
        frame = video.read()
        if frame is None:
            break

    for _ in range(20):
        video.read()

    pts = model.predict(frame)

    if not disable_tracking:
        boxes, pts = pts

    if not disable_tracking:
        if len(pts) > 0:
            if prev_pts is None and prev_person_ids is None:
                person_ids = np.arange(next_person_id, len(pts) + next_person_id, dtype=np.int32)
                next_person_id = len(pts) + 1
            else:
                boxes, pts, person_ids = find_person_id_associations(
                    boxes=boxes, pts=pts, prev_boxes=prev_boxes, prev_pts=prev_pts, prev_person_ids=prev_person_ids,
                    next_person_id=next_person_id, pose_alpha=0.2, similarity_threshold=0.4, smoothing_alpha=0.1,
                )
                next_person_id = max(next_person_id, np.max(person_ids) + 1)
        else:
            person_ids = np.array((), dtype=np.int32)

        prev_boxes = boxes.copy()
        prev_pts = pts.copy()
        prev_person_ids = person_ids

    else:
        person_ids = np.arange(len(pts), dtype=np.int32)

    for i, (pt, pid) in enumerate(zip(pts, person_ids)):
        frame = draw_points_and_skeleton(frame, pt, joints_dict()[hrnet_joints_set]['skeleton'], person_index=pid,
                                            points_color_palette='gist_rainbow', skeleton_color_palette='jet',
                                            points_palette_samples=10)

    fps = 1. / (time.time() - t)
    print('\rframerate: %f fps' % fps, end='')

    cv2.imshow('frame.png', frame)
    k = cv2.waitKey(1)
    if k == 27:  # Esc button
        video.release()
        break

cv2.destroyAllWindows()