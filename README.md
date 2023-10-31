# IMU_CAMERA_Time-synchronization

# 使用注意事项
1 录制的rosbag必须包括/imu/data /imu/time_ref /imu/trigger /capture_node/triggers（双目为/master_cam/triggers）
2 录制的rosbag位置和名称修改在`imu_data.py`的第四行，重新打包的rosbag名称为`output.bag`，位置处于代码所在文件夹

# imu_data.py：
## 作用：
原数据查看及处理重新打包

## 关于print：
输出的时间点都为imu对相机发出trigger的时刻
`type_list`:相机trigger的type,这里只会输出1，意为接收到IMU发出trigger时的数据
`DAVIS_time`:电脑接收相机数据的时间戳
`imu_seq`:imu的seq（用来对应数据的）
`imu_status`:vector.x=1时，为脉冲上升沿时刻，即trigger时刻
`imu_time`:电脑接收imu数据的时间戳
`imu_time_ref`:imu自身时间戳
`offset_time`:相邻两次`DAVIS_time`和`imu_time_ref`差值的平均值

## 关于修改后的`output.bag`：
修改的数据为IMU的时间戳，将触发作为分段依据，计算每次触发时刻`DAVIS_time`和`imu_time_ref`差值，并将相邻两次的平均值作为中间这段时间的offset time，再将每个时刻IMU的`imu_time_ref+offset_time`赋给 /imu/data 中的时间戳，其他数据不变

# data_read.py：
## 作用：
读取imu_data.py输出的output.bag中的数据

## 关于print：
与imu_data.py的基本相似，区别只有imu_time不同，为修改后的时间，且应与DAVIS_time基本一致，若想查看数据处理效果，看最后两行输出即可


