# Stereo Camera Setup Guide

두 대의 FLIR 카메라를 연결하고 소프트웨어 동기화를 설정하는 가이드입니다.

## 1. 카메라 연결

### USB 연결
- 두 카메라를 **별도의 USB 컨트롤러**에 연결하세요 (대역폭 확보)
- USB 허브 사용 시 대역폭 부족으로 프레임 드롭 발생 가능

### 시리얼 번호 확인
```bash
# Spinnaker SDK 설치 후
SpinView  # GUI로 시리얼 번호 확인

# 또는 터미널에서
ls /dev/video*
```

## 2. Launch 파일 설정

### 파일 위치
`spinnaker_camera_driver/launch/multiple_cameras.launch.py`

### 시리얼 번호 수정
```python
LaunchArg(
    'cam_0_serial',
    default_value="'YOUR_SERIAL_1'",  # 따옴표 필수!
    description='FLIR serial number of camera 0',
),
LaunchArg(
    'cam_1_serial',
    default_value="'YOUR_SERIAL_2'",
    description='FLIR serial number of camera 1',
),
```

### 프레임 레이트 (Hz) 변경
```python
camera_params = {
    # ...
    'frame_rate_auto': 'Off',
    'frame_rate': 30.0,  # 원하는 Hz로 변경 (예: 15.0, 60.0)
    'frame_rate_enable': True,
    # ...
}
```

### 해상도 변경
```python
camera_params = {
    # ...
    'image_width': 1920,   # 원하는 해상도
    'image_height': 1080,
    # ...
}
```

### 카메라 이름 변경
Launch 시 파라미터로 지정:
```bash
ros2 launch spinnaker_camera_driver multiple_cameras.launch.py \
    cam_0_name:=left \
    cam_1_name:=right
```

## 3. 카메라 실행

### 터미널 1: 카메라 드라이버 실행
```bash
cd ~/ros2_ws
source install/setup.bash
ros2 launch spinnaker_camera_driver multiple_cameras.launch.py
```

### 토픽 확인
```bash
ros2 topic list | grep image
# 예상 출력:
# /left/image_raw
# /right/image_raw
```

### 프레임 레이트 확인
```bash
ros2 topic hz /left/image_raw
```

## 4. 소프트웨어 동기화

GPIO 하드웨어 연결 없이 타임스탬프 기반으로 두 카메라 이미지를 동기화합니다.

### 터미널 2: 동기화 노드 실행
```bash
cd ~/ros2_ws/src/flir_camera_driver/spinnaker_camera_driver/scripts
python3 stereo_sync_node.py
```

### 토픽 이름이 다른 경우
```bash
python3 stereo_sync_node.py --ros-args \
    -p cam0_topic:=/cam_0/image_raw \
    -p cam1_topic:=/cam_1/image_raw
```

### 동기화 허용 오차 조정
```bash
# slop: 허용 시간 차이 (초). 기본값 0.1초 (100ms)
python3 stereo_sync_node.py --ros-args -p slop:=0.05
```

### 동기화 노드 파라미터

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| `cam0_topic` | `/left/image_raw` | 카메라 0 이미지 토픽 |
| `cam1_topic` | `/right/image_raw` | 카메라 1 이미지 토픽 |
| `slop` | `0.1` | 동기화 허용 오차 (초) |
| `queue_size` | `10` | 메시지 큐 크기 |
| `publish_synced` | `true` | 동기화된 이미지 재발행 |

### 동기화된 이미지 토픽
```bash
/synced/cam_0/image_raw
/synced/cam_1/image_raw
```

## 5. 예상 결과

```
==================================================
Stereo Sync Node Started!
  Cam0 Topic: /left/image_raw
  Cam1 Topic: /right/image_raw
  Slop: 100ms
==================================================
[   30] Synced! diff:  15.2ms (avg: 14.8ms)
[   60] Synced! diff:  12.5ms (avg: 13.2ms)
==================================================
Statistics (last 100 frames):
  Total synced: 300
  Avg diff: 14.52ms
  Min/Max: 2.31ms / 28.45ms
==================================================
```

## 6. 트러블슈팅

### "No synchronized frames received"
1. 토픽 이름 확인: `ros2 topic list | grep image`
2. slop 값 증가: `--ros-args -p slop:=1.0`

### 프레임 드롭
1. 해상도 낮추기
2. 프레임 레이트 낮추기
3. USB 허브 사용하지 않기

### 카메라 인식 안됨
```bash
# udev 규칙 설정
sudo ./scripts/linux_setup_flir
# 재부팅 또는 재연결
```

## 7. 하드웨어 동기화 (선택)

더 정밀한 동기화가 필요하면 GPIO 케이블로 연결:
- Primary 카메라 Line2 → Secondary 카메라 Line3
- `spinnaker_synchronized_camera_driver` 패키지 사용

자세한 내용: `spinnaker_synchronized_camera_driver/doc/index.rst`

