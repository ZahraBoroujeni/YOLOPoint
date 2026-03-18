uint16 id
string class_name
uint8 class_index
uint8 class_count                           # stores number of classes
float32[] class_probabilities               # may contain just one value if other prob. are not available
bool is_instance                            # flag for non-instance pixels, like e.g background. These can be
                                            # visualized differently in rviz

uint32 bounding_box_min_x
uint32 bounding_box_min_y
uint32 bounding_box_max_x
uint32 bounding_box_max_y