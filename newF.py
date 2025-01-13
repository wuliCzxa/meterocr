class AxisProportion:
    def __init__(self, axis_model, axis_left=0.0, axis_right=0.0, axis_up=0.0, axis_down=0.0):
        self.axis_x1 = axis_model[0][0]
        self.axis_x2 = axis_model[2][0]
        self.axis_y1 = axis_model[0][1]
        self.axis_y2 = axis_model[2][1]

        self.axis_left = axis_left
        self.axis_right = axis_right
        self.axis_up = axis_up
        self.axis_down = axis_down
    def get_axis_arr(self):
        axis_arr = (
            int(self.axis_x1 + self.axis_left * (self.axis_x2 - self.axis_x1)),
            int(self.axis_y1 + self.axis_up * (self.axis_x2 - self.axis_x1)),
            int(self.axis_x2 + self.axis_right * (self.axis_x2 - self.axis_x1)),
            int(self.axis_y2 + self.axis_down * (self.axis_x2 - self.axis_x1))
        )
        return axis_arr
def process_points(draw, img, points, list, point_proportion = 0.2, thrshd_proportion = 0.25):
    point_flag = 0
    for idx in len(list):
        point_left = points.axis_left + list[idx]
        point_right = points.axis_right + list[idx]
        draw.rectangle((
            points.axis_x1 + point_left * (points.axis_x2 - points.axis_x1),
            points.axis_y1 + points.axis_up * (points.axis_x2 - points.axis_x1),
            points.axis_x2 + point_right * (points.axis_x2 - points.axis_x1),
            points.axis_y2 + points.axis_down * (points.axis_x2 - points.axis_x1)), outline='yellow', width=3)
        point_arr = 255 * img[
                          int(points.axis_y1 + points.axis_up * (points.axis_x2 - points.axis_x1)):
                          int(points.axis_y2 + points.axis_down * (points.axis_x2 - points.axis_x1)),
                          int(points.axis_x1 + point_left * (points.axis_x2 - points.axis_x1)):
                          int(points.axis_x2 + point_right * (points.axis_x2 - points.axis_x1))
                          ]
        point_arr = img_binary(point_arr, thrshd_proportion)
        pixel_black = np.sum(point_arr == 0)
        # 小数点占比
        print(f'小数点 {idx} : {pixel_black / point_arr.size * 100:.1f}%')

        if pixel_black / point_arr.size > point_proportion:
            point_flag = idx
            point_proportion = pixel_black / point_arr.size
            # img_test = Image.fromarray(point_arr.astype(np.uint8))
            # img_test.show()
    return point_flag