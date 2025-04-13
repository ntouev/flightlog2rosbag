import pandas as pd
from rosbags.rosbag2 import Writer
from rosbags.typesys import Stores, get_typestore
from builtin_interfaces.msg import Time as RosTime
from geometry_msgs.msg import TransformStamped
from tf2_msgs.msg import TFMessage
import h5py
import os
import shutil
import argparse

def mat_to_df(matfile):
    with h5py.File(matfile, 'r') as file:
        out = file['out'][:]

        df = pd.DataFrame(out, columns=['time', 'x', 'y', 'z', 'qs', 'qx', 'qy', 'qz'])
        return df

# argument parser
parser = argparse.ArgumentParser(description="Create rosbag from flight data.")
parser.add_argument("data_source", help="Data source (e.g., simulink, pprz)")
parser.add_argument("file_name", help="The name of the file (e.g., circles)")
args = parser.parse_args()
data_source = args.data_source
file_name = args.file_name

file_path = f'logs/{data_source}/{file_name}.mat'
rosbag_path = f'rosbags/{data_source}/{file_name}'

if os.path.exists(rosbag_path):
    response = input(f"Folder {rosbag_path} already exists. Overwrite? [y/n]: ").strip().lower()
    if response == 'y':
        shutil.rmtree(rosbag_path)
        print("✅ Existing folder removed.")
    else:
        print("❌ Operation cancelled.")
        exit()

df = mat_to_df(file_path)

typestore = get_typestore(Stores.LATEST)
TFMessage = typestore.types['tf2_msgs/msg/TFMessage']

with Writer(rosbag_path, version=9) as writer:
    topic = '/tf'
    msgtype = TFMessage.__msgtype__
    connection = writer.add_connection(topic, msgtype, typestore=typestore)

    for i, row in df.iterrows():
        sec = int(row['time'])
        nsec = int((row['time'] - sec) * 1e9)
        stamp = RosTime(sec=sec, nanosec=nsec)
        print(f"sec: {sec}", end='\r')

        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id = 'world'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = row['x']
        t.transform.translation.y = row['y']
        t.transform.translation.z = row['z']
        t.transform.rotation.w = row['qs']
        t.transform.rotation.x = row['qx']
        t.transform.rotation.y = row['qy']
        t.transform.rotation.z = row['qz']

        message = TFMessage(transforms=[t])
        timestamp = stamp.sec * 10**9 + stamp.nanosec
        writer.write(connection, timestamp, typestore.serialize_cdr(message, msgtype))

print("✅ Bag written")
