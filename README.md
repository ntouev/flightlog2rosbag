This repo has been archived. The idea of using ros tools to visualize flight data turned out to be an overkill.

# Flightlog2rosbag
This repo is used to generate rosbags from flight data and simulation data. The idea is to be able to use existing powerful visualization tools of the ROS ecosystem (eg Foxglove).

## Prerequisites
- Install ros2 humble (any ros2 distro should work but not tested).

## Usage
Start by creating the file structure
```
mkdir -p logs/simulink
mkdir -p rosbags/simulink
```
