import rosbag
import rospy

bag_filepath = "record.bag"
bag = rosbag.Bag(bag_filepath)

#单目
# topic_name = "/capture_node/triggers"
# type_list = [] 
# time_list = []

#双目
topic_name = "/master_cam/triggers"
type_list = [] 
time_list = []

imu_status_topic_name = "/imu/status"
status_list = []
status_time_list = []
status_seq_list = []

imu_data_topic_name = "/imu/data"

imu_time_ref_topic_name = "/imu/time_ref"
time_ref_list = []

for topic, msg, t in bag.read_messages():
    # print(topic)
    if (topic == imu_status_topic_name): #记录imu带触发信号的seq和电脑接收到信号的时间戳
        # print(msg)
        timestamp = msg.header.stamp.to_sec()
        status = msg.vector.x
        seq = msg.header.seq
        if status == 1.0:
            status_seq_list.append(seq)
            status_list.append(status)
            status_time_list.append(timestamp)
    else:
        if (topic == topic_name): #记录相机受到imu信号触发的时间戳
            timestamp = msg.timestamp.to_sec()
            trigger_type = msg.type
            # print(type(trigger_type))
            if trigger_type not in [6,7,8,9]:
                type_list.append(trigger_type)
                time_list.append(timestamp)
# print(time_list)
# print(status_time_list)
seq_all_list=[]
time_ref_all_list=[]

for topic, msg, t in bag.read_messages():#用上方得到的seq筛选出需要的time_ref和imu_data数据
    if (topic == imu_time_ref_topic_name): 
        # print(msg)
        time_ref=msg.time_ref.to_sec()
        seq = msg.header.seq
        
        time_ref_all_list.append(time_ref)
        seq_all_list.append(seq)
        # print(seq_list)
        if seq in status_seq_list:
            time_ref_list.append(time_ref)
    else:
        if (topic == imu_data_topic_name): 
            # print(msg)
            seq = msg.header.seq
            # if seq in status_seq_list:
            #     print(msg)

print('type_list:',type_list)
print('DAVIS_time:',time_list)

print('imu_seq:',status_seq_list)
print('imu_staus:',status_list)
print('imu_time:',status_time_list)

print('imu_time_ref:',time_ref_list)

num_time_list = len(time_list)#求每段的offset_time
offset_list=[]
for i in range(num_time_list-1):
    offest=(time_list[i]+time_list[i+1]-time_ref_list[i]-time_ref_list[i+1])/2
    offset_list.append(offest)
    
print('offset_time:',offset_list)

     
def add_offset(ref_time,offset_time):#调整时间戳
    final_time=ref_time+offset_time
    secs=int(final_time)
    nsecs=int((final_time%1)*1000000000)
    return secs,nsecs
    
    
j=0
# print(num_time_list)
# print(status_seq_list[3])

with rosbag.Bag('output.bag', 'w') as outbag:
    for topic, msg, t in rosbag.Bag(bag_filepath).read_messages():
        if topic == '/imu/data':
            if j == num_time_list-1:
                break
            
            start_seq=status_seq_list[j]
            end_seq=status_seq_list[j+1]
            
            seq=msg.header.seq
            num=seq_all_list.index(seq)
            
            if msg.header.seq >= start_seq and msg.header.seq <= end_seq:
                msg.header.stamp.secs,msg.header.stamp.nsecs=add_offset(time_ref_all_list[num],offset_list[j])
                outbag.write(topic, msg, msg.header.stamp) 
            else:
                if msg.header.seq >= end_seq:
                    j+=1
                    # print(j)

        elif topic == '/master_cam/triggers':

            outbag.write(topic, msg, msg.timestamp)
        else:
            outbag.write(topic, msg, msg.header.stamp) 


    # print(j)            
        
                    


# print('type_list:',type_list)
# print('DAVIS_time:',time_list)

# print('imu_seq:',status_seq_list)
# print('imu_staus:',status_list)
# print('imu_time:',status_time_list)

# print('imu_time_ref:',time_ref_list)
