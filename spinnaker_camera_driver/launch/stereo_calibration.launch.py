from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument as LaunchArg
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration as LaunchConfig
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch_ros.substitutions import FindPackageShare


camera_params = {
    'debug': False,
    'compute_brightness': True,
    'dump_node_map': False,
    'adjust_timestamp': True,
    'pixel_format': 'BGR8',
    'gain_auto': 'Continuous',
    'gain': 0,
    'exposure_auto': 'Continuous',
    'exposure_time': 9000,
    'frame_rate_auto': 'Off',
    'frame_rate': 30.0,
    'frame_rate_enable': True,
    'trigger_mode': 'Off',
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

    return ComposableNode(
        package='spinnaker_camera_driver',
        plugin='spinnaker_camera_driver::CameraDriver',
        name=name,
        parameters=[
            camera_params,
            {
                'parameter_file': parameter_file,
                'serial_number': serial,
            },
        ],
        remappings=[
            ('~/control', '/' + name + '/control'),
            ('~/meta', '/' + name + '/meta'),
        ],
        extra_arguments=[{'use_intra_process_comms': True}],
    )


def launch_setup(context, *args, **kwargs):
    container = ComposableNodeContainer(
        name='flir_stereo_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            make_camera_node(
                LaunchConfig('left_camera_name').perform(context),
                LaunchConfig('left_camera_type').perform(context),
                LaunchConfig('left_camera_serial').perform(context),
            ),
            make_camera_node(
                LaunchConfig('right_camera_name').perform(context),
                LaunchConfig('right_camera_type').perform(context),
                LaunchConfig('right_camera_serial').perform(context),
            ),
        ],
        output='screen',
    )
    return [container]


def generate_launch_description():
    return LaunchDescription(
        [
            LaunchArg(
                'left_camera_name',
                default_value='rgb1',
                description='ROS node name and topic namespace for the left camera',
            ),
            LaunchArg(
                'right_camera_name',
                default_value='rgb2',
                description='ROS node name and topic namespace for the right camera',
            ),
            LaunchArg(
                'left_camera_type',
                default_value='blackfly_s',
                description='Camera model for the left camera',
            ),
            LaunchArg(
                'right_camera_type',
                default_value='blackfly_s',
                description='Camera model for the right camera',
            ),
            LaunchArg(
                'left_camera_serial',
                default_value="'23287704'",
                description='Serial number for the left camera (keep quotes)',
            ),
            LaunchArg(
                'right_camera_serial',
                default_value="'23299086'",
                description='Serial number for the right camera (keep quotes)',
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
