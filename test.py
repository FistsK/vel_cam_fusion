import numpy as np
import cv2
import os
import pandas as pd
import open3d as o3d
vis = o3d.visualization.Visualizer()
vis.create_window(width=800, height=600)  # 创建窗口

# #设置连续帧 雷达第一视角
pcd = o3d.geometry.PointCloud()
to_reset = True
vis.add_geometry(pcd)
render_option = vis.get_render_option()  # 渲染配置
render_option.background_color = np.array([0, 0, 0])  # 设置点云渲染参数，背景颜色
render_option.point_size = 1.0  # 设置渲染点的大小



Columns_name = ['type','truncated','occluded','alpha','bbox_lift','bbox_top','bbox_right','bbox_bottom','height','width','length','pos_x','pos_y','pos_z','rot_y']
DETECTION_COLOR_DICT = {'Car': (255,255,0),'Pedestrian':(0,266,255),'Cyclist':(141,40,255)}
image_02_path = "./training/image_02/0001/" # 本人自己的测试数据路径，直接替换即可
velodyne_path = "./training/velodyne/0001/"
label_02_path = "./training/label_02/"
with open(f'./training/calib/0001.txt','r') as f:
    calib = f.readlines()
# P2 (3 x 4) for left eye
P2 = np.array([float(x) for x in calib[2].strip('\n').split(' ')[1:]]).reshape(3,4)
R0_rect = np.array([float(x) for x in calib[4].strip('\n').split(' ')[1:]]).reshape(3,3)
# Add a 1 in bottom-right, reshape to 4 x 4
R0_rect = np.insert(R0_rect,3,values=[0,0,0],axis=0)
R0_rect = np.insert(R0_rect,3,values=[0,0,0,1],axis=1)
Tr_velo_to_cam = np.array([float(x) for x in calib[5].strip('\n').split(' ')[1:]]).reshape(3,4)
Tr_velo_to_cam = np.insert(Tr_velo_to_cam,3,values=[0,0,0,1],axis=0)

cv2.namedWindow('image_origin', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('image_dect', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('image+velodyne', cv2.WINDOW_AUTOSIZE)
files = os.listdir(image_02_path)
for file_index in range(len(files)):
    try:
        # 图像的路径
        image_data_path = os.path.join(image_02_path, "%06d.png" % file_index)
        # 从bin文件中得到激光雷达点云信息
        lidar_data_path = os.path.join(velodyne_path, "%06d.bin" % file_index)
        # 从label_02文件夹中拿出2d检测框真实值
        label_data_path = os.path.join(label_02_path, "%06d.txt" % file_index)
        df = pd.read_csv(label_data_path, header=None, sep=' ')
        df.columns = Columns_name
        df.head()
        df.loc[df.type.isin(['Van', 'Truck', 'Tram']), 'type'] = 'Car'
        df = df[df.type.isin(['Car', 'Cyclist', 'Pedestrian'])]
        boxs = np.array(df.loc[:][['bbox_lift', 'bbox_top', 'bbox_right', 'bbox_bottom']])
        types = np.array(df.loc[:]['type'])

        # read raw data from binary
        scan = np.fromfile(lidar_data_path, dtype=np.float32).reshape((-1, 4))
        points = scan[:, 0:3]  # lidar xyz (front, left, up)
        point_xyz = points[:, :3]  # x, y, z
        point_intensity = scan[:, 3]  # intensity

        pcd.points = o3d.utility.Vector3dVector(point_xyz)
        vis.update_geometry(pcd)
        if to_reset:
            vis.reset_view_point(True)
            to_reset = False
        vis.poll_events()
        vis.update_renderer()

        # TODO: use fov filter?
        velo = np.insert(points, 3, 1, axis=1).T
        velo = np.delete(velo, np.where(velo[0, :] < 0), axis=1)
        cam = P2.dot(R0_rect.dot(Tr_velo_to_cam.dot(velo)))
        cam = np.delete(cam, np.where(cam[2, :] < 0), axis=1)
        # get u,v,z
        cam[:2] /= cam[2, :]
        img = cv2.imread(image_data_path)
        cv2.imshow('image_origin', img)
        IMG_H, IMG_W, _ = img.shape
        # filter point out of canvas
        u, v, z = cam
        u_out = np.logical_or(u < 0, u > IMG_W)
        v_out = np.logical_or(v < 0, v > IMG_H)
        outlier = np.logical_or(u_out, v_out)
        cam = np.delete(cam, np.where(outlier), axis=1)
        for typ, box in list(zip(types, boxs)):
            top_lift = int(box[0]), int(box[1])
            bottom_right = int(box[2]), int(box[3])
            cv2.rectangle(img, top_lift, bottom_right, DETECTION_COLOR_DICT[typ], 2)
        cv2.imshow('image_dect', img)
        # generate color map from depth
        u, v, z = cam
        for i in range(len(u)):
            cv2.circle(img, (int(u[i]), int(v[i])), 1, (int(z[i]), int(z[i]*10), int(255/z[i])*5), -1)
        cv2.imshow('image+velodyne', img)
        cv2.waitKey(10)
    except:
        print("ERROR! But running!")
cv2.destroyAllWindows()

