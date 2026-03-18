std_msgs/Header header

ObjectInstance2D[] instances

sensor_msgs/Image semantic_mask             # optional: in case of panoptic segmentation (mono16 with class IDs)
uint16[] semantic_class_indices             # list of class indices in semantic mask (required if semantic mask is set)
string[] semantic_class_names               # list of corresponding class names (required if semantic mask is set)

sensor_msgs/Image instance_mask             # optional: combined instance masks (mono16 with instance IDs)
