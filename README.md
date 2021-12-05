# Capstone-Design-Chair-Master
## 2021 Capstone Design Project Repository
- 2021 캡스톤디자인 프로젝트 저장소입니다.
- 압력센서, 초음파센서, 카메라, PoseEstimation 딥러닝을 이용해 사용자의 자세를 실시간으로 측정하고 자세에 따라 안내음성 및 스트레칭을 제공하는 프로그램입니다.
- 코드는 컴퓨터에서 작동하는 파이썬과 c++로 작동하는 아두이노를 위한 코드폴더로 나누어져있습니다.

## Features
- 아두이노의 센서값들을 시리얼 통신을 이용해 제공받습니다.
- 받은 센서값들을 GUI 앱 내부에서 처리하여 사용자에게 시각화된 센서이미지를 제공합니다.
- 카메라의 실시간 영상을 PoseEstimation 모델에 입력하여 현재 거북목위험도를 측정하고 정보를 표시합니다.
- 각 자세에 따라 하체 스트레칭, 전신 스트레칭, 거북목 스트레칭 등의 유형별 스트레칭 유튜브 영상을 GUI 앱 내부에서 제공합니다.
- 스트레칭 여부와 현재의 자세가 어떤지를 음성(TTS)으로 안내합니다.

## Runtime images
![Alt text](/imgs/run1.jpg)
![Alt text](/imgs/run2.jpg)
![Alt text](/imgs/run3.jpg)
