================================
ROS Teledyne FLIR camera drivers
================================


.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. image:: doc/flir.png
   :target: https://www.flir.com/browse/industrial/machine-vision-cameras/

This repository contains ROS2 packages for machine vision cameras made by
Teledyne FLIR (formerly known as PointGrey). Note: this software is *not
supported* by Teleydyne FLIR.

Quick Start (Stereo Camera Setup)
=================================

Installation
------------

.. code-block:: bash

   # 1. Create workspace
   mkdir -p ~/ros2_ws/src
   cd ~/ros2_ws/src

   # 2. Clone repository
   git clone https://github.com/Hyun-gyu/flir_camera_driver.git
   cd flir_camera_driver
   git checkout humble-devel

   # 3. Install Spinnaker SDK (download from FLIR website)
   # https://www.flir.com/products/spinnaker-sdk/

   # 4. Install dependencies
   cd ~/ros2_ws
   rosdep install --from-paths src --ignore-src -r -y

   # 5. Build
   colcon build --symlink-install

   # 6. Setup udev rules (for USB cameras)
   sudo ~/ros2_ws/src/flir_camera_driver/spinnaker_camera_driver/scripts/linux_setup_flir

Camera Configuration
--------------------

Edit ``spinnaker_camera_driver/launch/multiple_cameras.launch.py``:

.. code-block:: python

   # Update serial numbers (find with SpinView)
   LaunchArg('cam_0_serial', default_value="'YOUR_SERIAL_1'", ...),
   LaunchArg('cam_1_serial', default_value="'YOUR_SERIAL_2'", ...),

   # Adjust frame rate
   camera_params = {
       'frame_rate': 30.0,  # Change to 15.0, 60.0, etc.
       ...
   }

Run Cameras
-----------

.. code-block:: bash

   # Terminal 1: Start cameras
   source ~/ros2_ws/install/setup.bash
   ros2 launch spinnaker_camera_driver multiple_cameras.launch.py

   # Terminal 2: Check topics
   ros2 topic list | grep image

Software Synchronization
------------------------

For stereo cameras without GPIO hardware connection:

.. code-block:: bash

   # Terminal 2: Run sync node
   cd ~/ros2_ws/src/flir_camera_driver/spinnaker_camera_driver/scripts
   python3 stereo_sync_node.py

   # With custom topics
   python3 stereo_sync_node.py --ros-args \
       -p cam0_topic:=/cam_0/image_raw \
       -p cam1_topic:=/cam_1/image_raw \
       -p slop:=0.1

Synchronized images are published to ``/synced/cam_0/image_raw`` and ``/synced/cam_1/image_raw``.

For detailed setup guide, see `STEREO_CAMERA_SETUP.md <spinnaker_camera_driver/doc/STEREO_CAMERA_SETUP.md>`__.

Packages
========

Spinnaker camera driver
-----------------------

| A camera driver supporting USB3 and GIGE cameras that has been
  successfully used for Blackfly, Blackfly S, Chameleon, and Grasshopper
  cameras. It should work with any FLIR camera that supports the
  Spinnaker SDK. See the
  `spinnaker_camera_driver <spinnaker_camera_driver/doc/index.rst>`__ for
  more.

|driver_humble| |driver_kilted| |driver_jazzy| |driver_rolling|

.. |driver_humble| image:: https://build.ros2.org/buildStatus/icon?job=Hbin_uJ64__spinnaker_camera_driver__ubuntu_jammy_amd64__binary&subject=Humble
   :target: https://build.ros2.org/job/Hbin_uJ64__spinnaker_camera_driver__ubuntu_jammy_amd64__binary/
.. |driver_jazzy| image:: https://build.ros2.org/buildStatus/icon?job=Jbin_uN64__spinnaker_camera_driver__ubuntu_noble_amd64__binary&subject=Jazzy
   :target: https://build.ros2.org/job/Jbin_uN64__spinnaker_camera_driver__ubuntu_noble_amd64__binary/
.. |driver_kilted| image:: https://build.ros2.org/buildStatus/icon?job=Kbin_uN64__spinnaker_camera_driver__ubuntu_noble_amd64__binary&subject=Kilted
   :target: https://build.ros2.org/job/Kbin_uN64__spinnaker_camera_driver__ubuntu_noble_amd64__binary/
.. |driver_rolling| image:: https://build.ros2.org/buildStatus/icon?job=Rbin_uN64__spinnaker_camera_driver__ubuntu_noble_amd64__binary&subject=Rolling
   :target: https://build.ros2.org/job/Rbin_uN64__spinnaker_camera_driver__ubuntu_noble_amd64__binary/



Spinnaker synchronized camera driver
------------------------------------

| Based on the spinnaker_camera_driver package, this driver is
  specifically designed for cameras that are hardware triggered by an external
  pulse. Images triggered by the same external pulse will have identical ROS header time stamps. See the
  `spinnaker_synchronized_camera_driver <spinnaker_synchronized_camera_driver/doc/index.rst>`__
  for more.

|sync_humble| |sync_kilted| |sync_jazzy| |sync_rolling|

.. |sync_humble| image:: https://build.ros2.org/buildStatus/icon?job=Hbin_uJ64__spinnaker_synchronized_camera_driver__ubuntu_jammy_amd64__binary&subject=Humble
   :target: https://build.ros2.org/job/Hbin_uJ64__spinnaker_synchronized_camera_driver__ubuntu_jammy_amd64__binary/
.. |sync_jazzy| image:: https://build.ros2.org/buildStatus/icon?job=Jbin_uN64__spinnaker_synchronized_camera_driver__ubuntu_noble_amd64__binary&subject=Jazzy
   :target: https://build.ros2.org/job/Jbin_uN64__spinnaker_synchronized_camera_driver__ubuntu_noble_amd64__binary/
.. |sync_kilted| image:: https://build.ros2.org/buildStatus/icon?job=Kbin_uN64__spinnaker_synchronized_camera_driver__ubuntu_noble_amd64__binary&subject=Kilted
   :target: https://build.ros2.org/job/Kbin_uN64__spinnaker_synchronized_camera_driver__ubuntu_noble_amd64__binary/
.. |sync_rolling| image:: https://build.ros2.org/buildStatus/icon?job=Rbin_uN64__spinnaker_synchronized_camera_driver__ubuntu_noble_amd64__binary&subject=Rolling
   :target: https://build.ros2.org/job/Rbin_uN64__spinnaker_synchronized_camera_driver__ubuntu_noble_amd64__binary/
            
FLIR camera description
-----------------------

| Package with `meshes and urdf <flir_camera_description/README.md>`__
  files.

|desc_humble| |desc_kilted| |desc_jazzy| |desc_rolling|

.. |desc_humble| image:: https://build.ros2.org/buildStatus/icon?job=Hbin_uJ64__flir_camera_description__ubuntu_jammy_amd64__binary&subject=Humble
   :target: https://build.ros2.org/job/Hbin_uJ64__flir_camera_description__ubuntu_jammy_amd64__binary/
.. |desc_jazzy| image:: https://build.ros2.org/buildStatus/icon?job=Jbin_uN64__flir_camera_description__ubuntu_noble_amd64__binary&subject=Jazzy
   :target: https://build.ros2.org/job/Jbin_uN64__flir_camera_description__ubuntu_noble_amd64__binary/
.. |desc_kilted| image:: https://build.ros2.org/buildStatus/icon?job=Kbin_uN64__flir_camera_description__ubuntu_noble_amd64__binary&subject=Kilted
   :target: https://build.ros2.org/job/Kbin_uN64__flir_camera_description__ubuntu_noble_amd64__binary/
.. |desc_rolling| image:: https://build.ros2.org/buildStatus/icon?job=Rbin_uN64__flir_camera_description__ubuntu_noble_amd64__binary&subject=Rolling
   :target: https://build.ros2.org/job/Rbin_uN64__flir_camera_description__ubuntu_noble_amd64__binary/


FLIR camera messages
--------------------

| Package with with `image exposure and control
  messages <flir_camera_msgs/README.md>`__. These are used by the
  `spinnaker_camera_driver <spinnaker_camera_driver/doc/index.rst>`__.


|msg_humble| |msg_kilted| |msg_jazzy| |msg_rolling|

.. |msg_humble| image:: https://build.ros2.org/buildStatus/icon?job=Hbin_uJ64__flir_camera_msgs__ubuntu_jammy_amd64__binary&subject=Humble
   :target: https://build.ros2.org/job/Hbin_uJ64__flir_camera_msgs__ubuntu_jammy_amd64__binary/
.. |msg_jazzy| image:: https://build.ros2.org/buildStatus/icon?job=Jbin_uN64__flir_camera_msgs__ubuntu_noble_amd64__binary&subject=Jazzy
   :target: https://build.ros2.org/job/Jbin_uN64__flir_camera_msgs__ubuntu_noble_amd64__binary/
.. |msg_kilted| image:: https://build.ros2.org/buildStatus/icon?job=Kbin_uN64__flir_camera_msgs__ubuntu_noble_amd64__binary&subject=Kilted
   :target: https://build.ros2.org/job/Kbin_uN64__flir_camera_msgs__ubuntu_noble_amd64__binary/
.. |msg_rolling| image:: https://build.ros2.org/buildStatus/icon?job=Rbin_uN64__flir_camera_msgs__ubuntu_noble_amd64__binary&subject=Rolling
   :target: https://build.ros2.org/job/Rbin_uN64__flir_camera_msgs__ubuntu_noble_amd64__binary/
