import rosbag

bag_filepath = "output.bag"
bag = rosbag.Bag(bag_filepath)


#单目
# topic_name = "/capture_node/triggers"
# type_list = [] 
# time_list = []

#双目
# topic_name = "/master_cam/triggers"
# type_list = [] 
# time_list = []

topic_name = "/davis_left/ext_trigger"
type_list = [] 
time_list = []

imu_status_topic_name = "/imu/status"
status_list = []
status_time_list = []
status_seq_list = []

imu_data_topic_name = "/imu/data"
imu_data_time_list=[]
imu_time_ref_topic_name = "/imu/time_ref"
time_ref_list = []

capture_node_camera_image_topic_name = "capture_node/camera/image"
image_list = []

capture_node_events = "/capture_node/events"
events_list = []

for topic, msg, t in bag.read_messages():

    # print(msg)
    if (topic == imu_status_topic_name): 
        # print(msg)
        timestamp = msg.header.stamp.to_sec()
        status = msg.vector.x
        seq = msg.header.seq
        if status == 1.0:
            status_seq_list.append(seq)
            status_list.append(status)
            status_time_list.append(timestamp)
    elif (topic == topic_name):
        timestamp = msg.header.stamp.to_sec()
        trigger_type = msg.point.x
        type_list.append(trigger_type)
        time_list.append(timestamp)


for topic, msg, t in bag.read_messages():
    if (topic == imu_time_ref_topic_name): 
        # print(msg)
        time_ref=msg.time_ref.to_sec()
        time_secs=msg.time_ref.secs
        seq = msg.header.seq
        if seq in status_seq_list:
            time_ref_list.append(time_ref)
    elif (topic == imu_data_topic_name): 
        seq = msg.header.seq
        if seq in status_seq_list:
            timestamp = msg.header.stamp.to_sec()
            imu_data_time_list.append(timestamp)
            # print(msg)
    elif (topic == capture_node_camera_image_topic_name): 
        # print(msg)
        data=msg.data
        image_list.append(data)
    elif (topic == capture_node_events): 
        # print(msg)
        events = msg.events
        events_list.append(events)






# print('type_list:',type_list)
print('imu_seq:',status_seq_list)
# print('imu_staus:',status_list)
# print('imu_time:',status_time_list)

print('imu_time_ref:',time_ref_list)
print('imu_data_time:',imu_data_time_list)
print('DAVIS_time:',time_list)
