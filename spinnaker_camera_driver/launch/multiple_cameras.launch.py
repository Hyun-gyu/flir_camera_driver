# -----------------------------------------------------------------------------
# Copyright 2022 Bernd Pfrommer <bernd.pfrommer@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument as LaunchArg
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration as LaunchConfig
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch_ros.substitutions import FindPackageShare

camera_params = {
    # ============== 기본 설정 ==============
    'debug': False,
    'compute_brightness': True,
    'dump_node_map': False,
    'adjust_timestamp': True,
    
    # ============== 이미지 설정 ==============
    'pixel_format': 'BGR8',              # 컬러 이미지 출력. OpenCV/rqt와 맞추기 쉬움
    'gain_auto': 'Off',           # 자동 게인 (또는 'Off'로 수동)
    'gain': 5.0,
    'exposure_auto': 'Off',       # 자동 노출 (또는 'Off'로 수동)
    'exposure_time': 9000,               # exposure_auto='Off'일 때만 적용 (μs)
    
    # ╔═══════════════════════════════════════════════════════════════════════════╗
    # ║                    🔧 하드웨어 트리거 설정 (FLIR BFS)                          ║
    # ║  Teensy 동기화 보드 사용 시 아래 파라미터 수정 필수                                 ║
    # ╚═══════════════════════════════════════════════════════════════════════════╝
    #
    # ┌─────────────────────────────────────────────────────────────────────────┐
    # │ [Free-Running 모드] - 카메라 자체 타이밍으로 촬영 (현재 설정)                     │
    # └─────────────────────────────────────────────────────────────────────────┘
    'frame_rate_auto': 'Off',
    'frame_rate': 30.0,                  # 원하는 프레임 레이트
    'frame_rate_enable': True,           # ⚠️ 트리거 모드에서는 False로 변경
    'trigger_mode': 'Off',               # ⚠️ 트리거 모드에서는 'On'으로 변경
    
    # ┌─────────────────────────────────────────────────────────────────────────┐
    # │ [Hardware Trigger 모드] - Teensy 보드 사용 시 아래 주석 해제                   │   
    # │  GPIO 연결: Teensy Pin 2 → Camera 0 Line0                                │
    # │             Teensy Pin 3 → Camera 1 Line0                               │
    # └─────────────────────────────────────────────────────────────────────────┘
    # 'frame_rate_enable': False,        # 트리거 모드에서는 프레임레이트 비활성화
    # 'trigger_mode': 'On',              # 외부 트리거 모드 활성화
    # 'trigger_source': 'Line3',         # BFS GPIO Line3 (트리거 입력 핀)
    # 'trigger_selector': 'FrameStart',  # 프레임 시작 시 트리거
    # 'trigger_activation': 'RisingEdge',# 상승 엣지에서 촬영 (Teensy와 일치)
    # 'trigger_overlap': 'ReadOut',      # 고속 촬영 시 오버랩 허용
    
    # ═══════════════════════════════════════════════════════════════════════════
    
    # ============== Chunk 데이터 (메타데이터) ==============
    'chunk_mode_active': True,
    'chunk_selector_frame_id': 'FrameID',
    'chunk_enable_frame_id': True,
    'chunk_selector_exposure_time': 'ExposureTime',
    'chunk_enable_exposure_time': True,
    'chunk_selector_gain': 'Gain',
    'chunk_enable_gain': True,
    'chunk_selector_timestamp': 'Timestamp',
    'chunk_enable_timestamp': True,
}


def make_camera_node(name, camera_type, serial):
    parameter_file = PathJoinSubstitution(
        [FindPackageShare('spinnaker_camera_driver'), 'config', camera_type + '.yaml']
    )

    node = ComposableNode(
        package='spinnaker_camera_driver',
        plugin='spinnaker_camera_driver::CameraDriver',
        name=name,
        parameters=[
            camera_params,
            {
                'parameter_file': parameter_file,
                'serial_number': serial,
                'pixel_format': LaunchConfig('pixel_format'),
            },
        ],
        remappings=[
            ('~/control', '/exposure_control/control'),
        ],
        extra_arguments=[{'use_intra_process_comms': True}],
    )
    return node


def launch_setup(context, *args, **kwargs):
    """Create multiple camera."""
    container = ComposableNodeContainer(
        name='stereo_camera_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            #
            # These two camera nodes run independently from each other,
            # but in the same address space
            #
            make_camera_node(
                LaunchConfig('cam_0_name'),
                LaunchConfig('cam_0_type').perform(context),
                LaunchConfig('cam_0_serial'),
            ),
            make_camera_node(
                LaunchConfig('cam_1_name'),
                LaunchConfig('cam_1_type').perform(context),
                LaunchConfig('cam_1_serial'),
            ),
        ],
        output='screen',
    )  # end of container
    return [container]


def generate_launch_description():
    """Create composable node by calling opaque function."""
    return LaunchDescription(
        [
            LaunchArg(
                'cam_0_name',
                default_value=['cam_0'],
                description='camera name (ros node name) of camera 0',
            ),
            LaunchArg(
                'cam_1_name',
                default_value=['cam_1'],
                description='camera name (ros node name) of camera 1',
            ),
            LaunchArg('cam_0_type', default_value='blackfly_s', description='type of camera 0'),
            LaunchArg('cam_1_type', default_value='blackfly_s', description='type of camera 1'),
            LaunchArg(
                'pixel_format',
                default_value='RGB8',
                description='image pixel format, e.g. RGB8, BGR8, BayerRG8, Mono8',
            ),
            LaunchArg(
                'cam_0_serial',
                # default_value="'23287704'",
                default_value="'23185377'",
                description='FLIR serial number of camera 0 (in quotes!!)',
            ),
            LaunchArg(
                'cam_1_serial',
                # default_value="'23299086'",
                default_value="'23185376'",
                description='FLIR serial number of camera 1 (in quotes!!)',
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
