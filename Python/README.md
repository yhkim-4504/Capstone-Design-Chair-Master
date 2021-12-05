# Python

## Sensor Visualization
![Alt text](/Python/imgs/SV_sample.png)
- 아두이노에서 측정한 압력센서와 초음파센서의 값을 시리얼통신을 이용해 전송합니다.
- 전송받은 값에 따라서 압력센서값의 크기를 원형으로 시각화하며 동시에 초음파센서가 감지한 거리를 화살표모양으로 나타내게 됩니다.

## Pose Estimator
![Alt text](/Python/imgs/HRNet_sample.png)
- 카메라로 찍은 앉아있는 모습을 HRNet PoseEstimation 모델에 입력하여 각 관절의 정보와 위치를 얻습니다.
- 얻은 정보에 따라 현재 목의 각도를 측정하여 정상적인(목에 무리를 주지않는) 각도인지 판단하게 됩니다.
- Pretrained HRNet Weight Download Link : [pose_hrnet_w48_384x288.pth](https://drive.google.com/file/d/1UoJhTtjHNByZSm96W3yFTfU5upJnsKiS/view)

## GUI APP
- PyQt5를 이용해 GUI를 구현하였으며 아두이노통신 및 센서시각화, Pose Estimation, 실시간 카메라표시, 정상자세여부 측정등을 각각 쓰레드로 구현하였습니다.
- 자세측정 후 하체의 압력이 불균형할 경우 목스트레칭 유튜브 영상을 GUI 내부에서 출력할 수 있으며 현재 자세와 스트레칭 여뷰를 TTS를 이용해 안내해줍니다.
