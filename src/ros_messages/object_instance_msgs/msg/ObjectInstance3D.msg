uint16 id
string class_name
uint8 class_index
uint8 class_count                           # stores number of classes
float32[] class_probabilities               # may contain just one value if other prob. are not available
bool is_instance                            # flag for non-instance point clouds, like e.g ground points. These can be
                                            # visualized differently in rviz

geometry_msgs/Pose bounding_box_pose        # the orientation of the object must be selected, such that the x-axis of
                                            # the object local coordinate system is aligned to the length of the object.
                                            # Analogously the y- and z-axis must be aligned to the width and the height,
                                            # respectively. From object perspective the axes x, y, and z are pointing
                                            # forward, to the left, and upwards, respectively.
geometry_msgs/Vector3 bounding_box_size     # x -> length, y -> width, z -> height of object

sensor_msgs/PointCloud2 point_cloud