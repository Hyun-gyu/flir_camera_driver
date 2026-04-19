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


BASE_CAMERA_PARAMS = {
    "debug": False,
    "compute_brightness": True,
    "dump_node_map": False,
    "adjust_timestamp": True,
    "pixel_format": "BGR8",
    "gain_auto": "Off",
    "gain": 5.0,
    "exposure_auto": "Off",
    "exposure_time": 9000.0,
    "frame_rate_auto": "Off",
    "frame_rate": 30.0,
    "frame_rate_enable": True,
    "trigger_mode": "Off",
    "chunk_mode_active": True,
    "chunk_selector_frame_id": "FrameID",
    "chunk_enable_frame_id": True,
    "chunk_selector_exposure_time": "ExposureTime",
    "chunk_enable_exposure_time": True,
    "chunk_selector_gain": "Gain",
    "chunk_enable_gain": True,
    "chunk_selector_timestamp": "Timestamp",
    "chunk_enable_timestamp": True,
}


def _parse_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _build_camera_params(context):
    params = dict(BASE_CAMERA_PARAMS)
    camera_mode = LaunchConfig("camera_mode").perform(context).strip().lower()

    params["debug"] = _parse_bool(LaunchConfig("debug").perform(context))
    params["compute_brightness"] = _parse_bool(
        LaunchConfig("compute_brightness").perform(context)
    )
    params["dump_node_map"] = _parse_bool(LaunchConfig("dump_node_map").perform(context))
    params["adjust_timestamp"] = _parse_bool(
        LaunchConfig("adjust_timestamp").perform(context)
    )
    params["pixel_format"] = LaunchConfig("pixel_format").perform(context)
    params["gain_auto"] = LaunchConfig("gain_auto").perform(context)
    params["gain"] = float(LaunchConfig("gain").perform(context))
    params["exposure_auto"] = LaunchConfig("exposure_auto").perform(context)
    params["exposure_time"] = float(LaunchConfig("exposure_time").perform(context))
    params["frame_rate_auto"] = LaunchConfig("frame_rate_auto").perform(context)
    params["frame_rate"] = float(LaunchConfig("frame_rate").perform(context))

    if camera_mode == "free_run":
        params["frame_rate_enable"] = _parse_bool(
            LaunchConfig("frame_rate_enable").perform(context)
        )
        params["trigger_mode"] = "Off"
    elif camera_mode == "hardware_trigger":
        params["frame_rate_enable"] = False
        params["trigger_mode"] = "On"
        params["trigger_source"] = LaunchConfig("trigger_source").perform(context)
        params["trigger_selector"] = LaunchConfig("trigger_selector").perform(context)
        params["trigger_activation"] = LaunchConfig("trigger_activation").perform(context)
        params["trigger_overlap"] = LaunchConfig("trigger_overlap").perform(context)
    else:
        raise RuntimeError(
            "Unsupported camera_mode '{}'. Use free_run or hardware_trigger.".format(
                camera_mode
            )
        )

    return params


def make_camera_node(name, camera_type, serial, context):
    parameter_file = PathJoinSubstitution(
        [FindPackageShare("spinnaker_camera_driver"), "config", camera_type + ".yaml"]
    )

    node = ComposableNode(
        package="spinnaker_camera_driver",
        plugin="spinnaker_camera_driver::CameraDriver",
        name=name,
        parameters=[
            _build_camera_params(context),
            {
                "parameter_file": parameter_file,
                "serial_number": serial,
                "pixel_format": LaunchConfig("pixel_format"),
            },
        ],
        remappings=[
            ("~/control", "/exposure_control/control"),
        ],
        extra_arguments=[{"use_intra_process_comms": True}],
    )
    return node


def launch_setup(context, *args, **kwargs):
    """Create multiple camera bringup with launch-configurable presets."""
    container = ComposableNodeContainer(
        name="stereo_camera_container",
        namespace="",
        package="rclcpp_components",
        executable="component_container",
        composable_node_descriptions=[
            make_camera_node(
                LaunchConfig("cam_0_name"),
                LaunchConfig("cam_0_type").perform(context),
                LaunchConfig("cam_0_serial"),
                context,
            ),
            make_camera_node(
                LaunchConfig("cam_1_name"),
                LaunchConfig("cam_1_type").perform(context),
                LaunchConfig("cam_1_serial"),
                context,
            ),
        ],
        output="screen",
    )
    return [container]


def generate_launch_description():
    """Create composable node by calling opaque function."""
    return LaunchDescription(
        [
            LaunchArg(
                "cam_0_name",
                default_value=["cam_0"],
                description="camera name (ros node name) of camera 0",
            ),
            LaunchArg(
                "cam_1_name",
                default_value=["cam_1"],
                description="camera name (ros node name) of camera 1",
            ),
            LaunchArg("cam_0_type", default_value="blackfly_s", description="type of camera 0"),
            LaunchArg("cam_1_type", default_value="blackfly_s", description="type of camera 1"),
            LaunchArg(
                "cam_0_serial",
                default_value="'23185377'",
                description="FLIR serial number of camera 0 (in quotes!!)",
            ),
            LaunchArg(
                "cam_1_serial",
                default_value="'23185376'",
                description="FLIR serial number of camera 1 (in quotes!!)",
            ),
            LaunchArg(
                "camera_mode",
                default_value="free_run",
                description="free_run or hardware_trigger",
            ),
            LaunchArg(
                "pixel_format",
                default_value="RGB8",
                description="image pixel format, e.g. RGB8, BGR8, BayerRG8, Mono8",
            ),
            LaunchArg(
                "frame_rate_auto",
                default_value="Off",
                description="camera frame rate auto mode",
            ),
            LaunchArg(
                "frame_rate",
                default_value="30.0",
                description="free-run frame rate or reference value for trigger profiles",
            ),
            LaunchArg(
                "frame_rate_enable",
                default_value="true",
                description="enable camera-side frame rate control in free_run mode",
            ),
            LaunchArg(
                "exposure_auto",
                default_value="Off",
                description="camera exposure auto mode",
            ),
            LaunchArg(
                "exposure_time",
                default_value="9000.0",
                description="manual exposure time in microseconds",
            ),
            LaunchArg(
                "gain_auto",
                default_value="Off",
                description="camera gain auto mode",
            ),
            LaunchArg(
                "gain",
                default_value="5.0",
                description="manual camera gain",
            ),
            LaunchArg(
                "compute_brightness",
                default_value="true",
                description="enable image brightness statistics",
            ),
            LaunchArg(
                "adjust_timestamp",
                default_value="true",
                description="adjust timestamps using camera metadata",
            ),
            LaunchArg(
                "debug",
                default_value="false",
                description="enable driver debug logging",
            ),
            LaunchArg(
                "dump_node_map",
                default_value="false",
                description="dump FLIR node map on startup",
            ),
            LaunchArg(
                "trigger_source",
                default_value="Line3",
                description="hardware trigger source when camera_mode=hardware_trigger",
            ),
            LaunchArg(
                "trigger_selector",
                default_value="FrameStart",
                description="hardware trigger selector when camera_mode=hardware_trigger",
            ),
            LaunchArg(
                "trigger_activation",
                default_value="RisingEdge",
                description="hardware trigger edge when camera_mode=hardware_trigger",
            ),
            LaunchArg(
                "trigger_overlap",
                default_value="ReadOut",
                description="hardware trigger overlap when camera_mode=hardware_trigger",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
