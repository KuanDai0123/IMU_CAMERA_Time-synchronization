import rosbag
import rospy
import math

bag_filepath = "record.bag"
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
            timestamp = msg.header.stamp.to_sec()
            trigger_type = msg.point.x
            type_list.append(trigger_type)
            time_list.append(timestamp)
            
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

# 首位对齐
def aligning(a_list,b_list):
    a=abs(a_list[0]-b_list[0])
    b=abs(a_list[0]-b_list[1])
    c=abs(a_list[1]-b_list[0])
    if (min(a,b,c) == a):
        return a_list,b_list
    elif (min(a,b,c) == b):
        return a_list,b_list[1:]
    elif (min(a,b,c) == c):
        return a_list[1:],b_list
    
time_list,status_time_list = aligning(time_list,status_time_list)

# 删除缺位，方便offset time计算
davis_period_list=[]
imu_period_list=[]

def period_list(list):
    period_list=[]
    for i in range(len(list)-1):
        period = list[i+1]-list[i]
        period_list.append(period)
    average_period=(list[len(list)-1]-list[0])/(len(list)-1)
    return average_period,period_list

davis_average_period,davis_period_list = period_list (time_list)
imu_average_period,imu_period_list = period_list (status_time_list)

# 判断缺几个
def count_number(period,avg_period):
    count_number=0
    while(1):
        count_number+=1
        if period < (count_number+0.8)*avg_period :
            break
    return count_number

davis_count_number=[0]

i=0
davis_count_number=[]
while i < len(davis_period_list) :
    davis_count_number.append(0)
    if (davis_period_list[i] > 1.2*davis_average_period):
        num=count_number(davis_period_list[i],davis_average_period)
        for j in range(num):
            davis_count_number.append(1)
    i+=1
davis_count_number.append(0)

i=0
imu_count_number=[]
while i < len(imu_period_list) :
    imu_count_number.append(0)
    if (imu_period_list[i] > 1.2*imu_average_period):
        num=count_number(imu_period_list[i],imu_average_period)
        for j in range(num):
            imu_count_number.append(1)
    i+=1
imu_count_number.append(0)

i=0
for status in imu_count_number:
    if status == 1:
        time_list.pop(i)
    else:
        i+=1
      
i=0
for status in davis_count_number:
    if status == 1:
        time_ref_list.pop(i)
    else:
        i+=1 


offset_list=[]
num_time_list = len(time_list)#求每段的offset_time

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
