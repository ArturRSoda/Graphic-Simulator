import numpy as np
import math as m

from CGSystemInterface import CGSystemInterface
from newObjWindow import NewObjWindow
from transformationWindow import TransformationWindow
from clipping import cohen_sutherland, liang_barsky
from objects import Object, Point, Line, Polygon, WireFrame


class CGSystem():
    def __init__(self):
        self.interface     : CGSystemInterface

        self.vp_coord_min  : tuple[float, float]
        self.vp_coord_max  : tuple[float, float]
        self.subvp_coord_min  : tuple[float, float]
        self.subvp_coord_max  : tuple[float, float]

        # add aspect ratio

        # p0, p1, p2, p3 | p0 -> w_min, p2 -> w_max
        self.w_coordinates : list[tuple[float, float]]
        self.up_vector     : tuple[float, float]
        self.right_vector  : tuple[float, float]

        self.display_file  : list[Object]

    def run(self):
        self.interface = CGSystemInterface(self)

        #self.vp_coord_max = (self.interface.canvas_width, self.interface.canvas_height)
        #self.vp_coord_min = (0, 0)

        self.vp_coord_max = (self.interface.subcanvas_width, self.interface.subcanvas_height)
        self.vp_coord_min = (0, 0)

        self.w_coordinates = [
            (-self.vp_coord_max[0]/2, -self.vp_coord_max[1]/2),
            ( self.vp_coord_max[0]/2, -self.vp_coord_max[1]/2),
            ( self.vp_coord_max[0]/2,  self.vp_coord_max[1]/2),
            (-self.vp_coord_max[0]/2,  self.vp_coord_max[1]/2)
        ]

        self.up_vector = (0, 1)
        self.right_vector = (1, 0)

        self.display_file = list()

        # world center lines
        self.display_file.append(Line("X", "black", [(-10000, 0), (10000, 0)], []))
        self.display_file.append(Line("Y", "black", [(0, -10000), (0, 10000)], []))

        # test objects
        self.add_test()

        self.generate_normal_coordinates()
        self.update_viewport()

        self.interface.app.mainloop()


    def add_object(self):
        NewObjWindow(self)


    def init_transformation_window(self, obj_id: int):
        obj = self.get_object(obj_id)
        TransformationWindow(self, obj)


    def del_object(self, id: int):
        self.interface.objects_listbox.delete(id)
        self.display_file.pop(id+2)

        self.update_viewport()


    def add_point(self,name: str, color: str, coord: tuple[float, float]):
        norm_coord = self.normalize_object_coordinates([coord])
        point = Point(name, color, [coord], norm_coord)

        self.display_file.append(point)
        self.interface.objects_listbox.insert("end", "%s [%s - Point]" % (name, color))

        self.update_viewport()


    def add_line(self, name: str, color: str, start_coord: tuple[float, float], end_coord: tuple[float, float]):
        norm_coord = self.normalize_object_coordinates([start_coord, end_coord])
        line = Line(name, color, [start_coord, end_coord], norm_coord)

        self.display_file.append(line)
        self.interface.objects_listbox.insert("end", "%s [%s - Line]" % (name, color))

        self.generate_normal_coordinates()
        self.update_viewport()


    def add_wireframe(self, name: str, color: str, coord_list: list[tuple[float, float]]):
        if (len(coord_list) == 1):
            self.add_point(name, color, coord_list[0])
            return

        norm_coord = self.normalize_object_coordinates(coord_list)
        wf = WireFrame(name, color, coord_list, norm_coord)

        self.display_file.append(wf)
        self.interface.objects_listbox.insert("end", "%s [%s - Wireframe]" % (name, color))

        self.generate_normal_coordinates()
        self.update_viewport()


    def add_polygon(self, name: str, color: str, coord_list: list[tuple[float, float]]):
        if (len(coord_list) == 1):
            self.add_point(name, color, coord_list[0])
            return

        """
        if (self.is_concave(coord_list)):
            convexes = self.split_polygon(coord_list)
            for i, convex in enumerate(convexes):
                self.add_polygon(f"convex {i}", "cyan", convex)

        """

        norm_coord = self.normalize_object_coordinates(coord_list)
        plg = Polygon(name, color, coord_list, norm_coord)

        self.display_file.append(plg)
        self.interface.objects_listbox.insert("end", "%s [%s - Polygon]" % (name, color))

        self.generate_normal_coordinates()
        self.update_viewport()


    def add_test(self):
        self.add_wireframe("L", "red", [(-70, 70), (-70, 30), (-45, 30)])
        self.add_wireframe("wireframe triangle", "green", [(-70, -70), (-30, -70), (-30, -40), (-70, -70)])
        self.add_polygon("triangle", "green", [(10, 10), (100, 10), (100, 100)])
        self.add_point("point", "blue", (10, 10))
        self.add_polygon("concave hexagon", "red", [(100, 100), (150, 100), (200, 130), (160, 170), (200, 200), (100, 200)])
        self.add_wireframe("concave wireframe hexagon", "red", [(-100, -100), (-150, -100), (-200, -130), (-160, -170), (-200, -200), (-100, -200), (-100, -100)])


    def clip_point_coordinates(self, coords: list[tuple[float, float]]) -> list[tuple[float, float]]|None:
        x, y = coords[0]
        return None if ((x < -1) or (x > 1) or (y < -1) or (y > 1)) else coords


    def clip_wireframe_coordinates(self, coords: list[tuple[float, float]]) -> list[tuple[float, float]]|None:
        pop = None
        if coords[0] == coords[-1]:
            pop = coords[-1]

        clip_coords = self.sutherland_hodgman_clip(coords)

        if pop is not None and clip_coords != []:
            coords.append(pop)
            clip_coords.append(clip_coords[0])

        return clip_coords


    def get_line_clipping_func(self):
        func_str = self.interface.line_clip_opt_var.get()
        return cohen_sutherland if (func_str == "cohen_sutherland") else liang_barsky


    def is_concave(self, coords: list[tuple[float, float]]):
        sign = None
        n = len(coords)
        for i in range(n):
            o = coords[i]
            a = coords[(i + 1) % n]
            b = coords[(i + 2) % n]

            cross_product = (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
            if cross_product != 0:
                if sign is None:
                    sign = m.copysign(1, cross_product)
                elif m.copysign(1, cross_product) != sign:
                    return True

        return False


    # computes the intersection point of the line segment between p1, p2 and cp1, cp2
    def compute_intersection(self, p1, p2, cp1, cp2):
        dc = [cp1[0] - cp2[0], cp1[1] - cp2[1]]
        dp = [p1[0] - p2[0], p1[1] - p2[1]]
        n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
        n2 = p1[0] * p2[1] - p1[1] * p2[0]
        denom = dc[0] * dp[1] - dc[1] * dp[0]
        
        if denom == 0:
            return None  # lines are parallel or collinear

        x = (n1 * dp[0] - n2 * dc[0]) / denom
        y = (n1 * dp[1] - n2 * dc[1]) / denom
        return (x, y)


    def is_inside(self, point, cp1, cp2):
        return (cp2[0] - cp1[0]) * (point[1] - cp1[1]) > (cp2[1] - cp1[1]) * (point[0] - cp1[0])


    def sutherland_hodgman_clip(self, coords: list[tuple[float, float]]):
        output_list = coords
        window = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

        for i in range(4):
            input_list = output_list
            output_list = []

            cp1 = window[i]
            cp2 = window[(i + 1) % 4]

            if not input_list:
                break

            s = input_list[-1]
            for e in input_list:
                if self.is_inside(e, cp1, cp2):
                    if not self.is_inside(s, cp1, cp2):
                        output_list.append(self.compute_intersection(s, e, cp1, cp2))
                    output_list.append(e)
                elif self.is_inside(s, cp1, cp2):
                    output_list.append(self.compute_intersection(s, e, cp1, cp2))
                s = e

        return output_list


    def update_viewport(self):
        self.interface.clear_canvas()

        for obj in self.display_file:
            clip_coords = None
            match obj.type:
                case "point":
                    clip_coords = self.clip_point_coordinates(obj.normalized_coordinates)
                case "line":
                    clip_coords = self.get_line_clipping_func()(obj.normalized_coordinates)
                case "wireframe":
                    clip_coords = self.clip_wireframe_coordinates(obj.normalized_coordinates)
                case "polygon":
                    clip_coords = self.sutherland_hodgman_clip(obj.normalized_coordinates)

            if (clip_coords is not None and clip_coords != []):
                obj_vp_coords = self.normalized_coords_to_vp_coords(clip_coords)
                self.interface.draw_object(obj, obj_vp_coords)


    def normalized_coords_to_vp_coords(self, norm_coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
        vp_coords: list[tuple[float, float]] = list()

        x_vp_max, y_vp_max = self.vp_coord_max

        for norm_coord in norm_coords:
            norm_coord = (((norm_coord[0] + 1) / 2), ((norm_coord[1] +1) / 2))
            x = norm_coord[0] * x_vp_max 
            y = y_vp_max - (norm_coord[1] * y_vp_max)
            x += self.interface.subcanvas_shift
            y += self.interface.subcanvas_shift
            vp_coords.append((x, y))

        return vp_coords
    
    
    def normalize_coordinates(self, coordinates: list[tuple[float, float]], window_coordinates: list[tuple[float, float]]):
        p0, p1, p2, p3 = window_coordinates
        normalized_coords = list()
        width = m.dist(p0, p1)
        height = m.dist(p1, p2)
        for coord in coordinates:
            x, y = coord

            normalized_x = 2 * (x - p0[0]) / width - 1
            normalized_y = 2 * (y - p0[1]) / height - 1

            normalized_coords.append((normalized_x, normalized_y))
        return normalized_coords


    def normalize_object_coordinates(self, coordinates: list[tuple[float, float]]):
        w_center = self.get_center(self.w_coordinates)
        delta_angle = self.get_delta_angle()

        transformation_list = []
        self.add_translation(transformation_list, -w_center[0], -w_center[1])
        self.add_rotation(transformation_list, -delta_angle, (0, 0))

        window_coordinates = self.transform(self.w_coordinates, transformation_list)
        transformed_coords = self.transform(coordinates, transformation_list)

        normalized_coordinates = self.normalize_coordinates(transformed_coords, window_coordinates)

        return normalized_coordinates


    def generate_normal_coordinates(self, degrees: float=0):
        # rotate up vector and right vector
        s = m.sin(m.radians(degrees))
        c = m.cos(m.radians(degrees))

        x, y = self.up_vector
        x_new = c * x - s * y
        y_new = s * x + c * y

        norm = np.linalg.norm([x_new, y_new])
        self.up_vector = (x_new/norm, y_new/norm)

        x, y = self.right_vector
        x_new = c * x - s * y
        y_new = s * x + c * y

        norm = np.linalg.norm([x_new, y_new])
        self.right_vector = (x_new/norm, y_new/norm)

        # aligns the window and the up vector with the y-axis, move the objects
        # and calculates the normalized coordinates
        w_center = self.get_center(self.w_coordinates)
        delta_angle = self.get_delta_angle()

        transformation_list = []
        self.add_translation(transformation_list, -w_center[0], -w_center[1])
        self.add_rotation(transformation_list, -delta_angle, (0, 0))

        window_coordinates = self.transform(self.w_coordinates, transformation_list)
        for obj in self.display_file:
            transformed_coords = self.transform(obj.coordinates, transformation_list)
            obj.normalized_coordinates = self.normalize_coordinates(transformed_coords, window_coordinates)


    # get angle between y-axis and up vector 
    def get_delta_angle(self):
        x, y = self.up_vector
        up_vector = np.array([x, y])
        norm_up = np.linalg.norm(up_vector)

        y_axis = np.array([0, 1])
        norm_y = np.linalg.norm(y_axis)

        dot_product = np.dot(up_vector, y_axis)
        delta_angle = m.degrees(m.acos(dot_product / (norm_up * norm_y)))
        delta_angle = -delta_angle if (x > 0) else delta_angle # dark magic

        return delta_angle


    def set_window_coord(self, coord: tuple[float, float]):
        w_center = self.get_center(self.w_coordinates)

        offset_x = coord[0] - w_center[0]
        offset_y = coord[1] - w_center[1]

        tranformation_list = list()
        self.add_translation(tranformation_list, offset_x, offset_y)
        self.w_coordinates = self.transform(self.w_coordinates, tranformation_list)

        self.generate_normal_coordinates();
        self.update_viewport()


    # direction can be: "up", "down", "left", "right"
    def move_window(self, offset: int, direction: str):
        transformation_list = []
        match direction:
            case "up":
                self.add_translation(transformation_list, self.up_vector[0]*offset,
                                                          self.up_vector[1]*offset)
            case "down":
                self.add_translation(transformation_list, -self.up_vector[0]*offset,
                                                          -self.up_vector[1]*offset)
            case "right":
                self.add_translation(transformation_list, self.right_vector[0]*offset,
                                                          self.right_vector[1]*offset)
            case "left":
                self.add_translation(transformation_list, -self.right_vector[0]*offset,
                                                          -self.right_vector[1]*offset)

        self.w_coordinates = self.transform(self.w_coordinates, transformation_list)

        self.generate_normal_coordinates()
        self.update_viewport()


    # inORout can be: "in", "out"
    def zoom_window(self, zoom_factor: float, inORout: str):
        zoom_factor = 1/zoom_factor if (inORout == "in") else zoom_factor

        transformation_list = []
        self.add_scaling(transformation_list, zoom_factor)
        self.w_coordinates = self.transform(self.w_coordinates, transformation_list)
    
        self.generate_normal_coordinates()
        self.update_viewport()


    def rotate_window(self, degrees: int, antiClockwise: bool):
        degrees = degrees if (antiClockwise) else -degrees

        w_center = self.get_center(self.w_coordinates)
        transformation_list = []
        self.add_rotation(transformation_list, degrees, w_center)
        self.w_coordinates = self.transform(self.w_coordinates, transformation_list)

        self.generate_normal_coordinates(degrees)
        self.update_viewport()


    # direction can be: "up", "down", "left", "right"
    def move_object(self, offset: int, direction: str, obj_id: int):
        obj = self.get_object(obj_id)
        transformation_list = []
        match direction:
            case "up":
                self.add_translation(transformation_list, self.up_vector[0]*offset,
                                                          self.up_vector[1]*offset)
            case "down":
                self.add_translation(transformation_list, -self.up_vector[0]*offset,
                                                          -self.up_vector[1]*offset)
            case "right":
                self.add_translation(transformation_list, self.right_vector[0]*offset,
                                                          self.right_vector[1]*offset)
            case "left":
                self.add_translation(transformation_list, -self.right_vector[0]*offset,
                                                          -self.right_vector[1]*offset)

        obj.coordinates = self.transform(obj.coordinates, transformation_list)
        obj.normalized_coordinates = self.normalize_object_coordinates(obj.coordinates)

        self.update_viewport()


    # change inORout to zoom_direction or just direction

    # inORout can be: "in", "out"
    def scale_object(self, scale_factor: float, object_id: int, inORout: str):
            scale_factor = 1/scale_factor if (inORout == "out") else scale_factor 
            obj = self.get_object(object_id)

            transformation_list = []
            self.add_scaling(transformation_list, scale_factor, self.get_center(obj.coordinates))
            obj.coordinates = self.transform(obj.coordinates, transformation_list)
            obj.normalized_coordinates = self.normalize_object_coordinates(obj.coordinates)

            self.update_viewport()


    # change some parameters 

    # rotation_opt can be: "Origin", "Obj Center" and "Other"
    def rotate_object(self, antiClockwise: bool, degrees: int, object_id: int, rotation_opt: str, rotation_point: tuple[float, float]=(0, 0)):
        degrees = degrees if (antiClockwise) else -degrees
        obj = self.get_object(object_id)

        transformation_list = []
        if (rotation_opt == "Origin"):
            self.add_rotation(transformation_list, degrees, (0, 0))
        elif(rotation_opt == "Obj Center"):
            self.add_rotation(transformation_list, degrees, self.get_center(obj.coordinates))
        else:
            self.add_rotation(transformation_list, degrees, rotation_point)

        obj.coordinates = self.transform(obj.coordinates, transformation_list)
        obj.normalized_coordinates = self.normalize_object_coordinates(obj.coordinates)

        self.update_viewport()


    def get_center(self, coordinates: list[tuple[float, float]]):
        # if the object is a polygon, the first and the last points are the same
        coordinates = coordinates.copy()
        if (coordinates[0] == coordinates[-1]) and (len(coordinates) > 1):
            coordinates.pop()

        average_x, average_y = 0, 0
        for x, y in coordinates:
            average_x += x
            average_y += y
        points_num = len(coordinates)
        average_x /= points_num
        average_y /= points_num

        return (average_x, average_y)


    def add_translation(self, transformation_list: list[list[list]], offset_x: float, offset_y: float):
        transformation_list.insert(1, np.array([[1, 0, 0],
                                                [0, 1, 0],
                                                [offset_x, offset_y, 1]]))


    def add_scaling(self, transformation_list: list[list[list]], scale_factor: float, transformation_point: tuple[float, float]=(0, 0)):
        if transformation_point != (0, 0):
            transformation_list.append(np.array([[1, 0, 0],
                                                 [0, 1, 0],
                                                 [-transformation_point[0], -transformation_point[1], 1]]))
            transformation_list.append(np.array([[1, 0, 0],
                                                 [0, 1, 0],
                                                 [transformation_point[0], transformation_point[1], 1]]))

        transformation_list.insert(1, np.array([[scale_factor, 0, 0],
                                                [0, scale_factor, 0],
                                                [0, 0, 1]]))


    def add_rotation(self, transformation_list: list[list[list]], rotation_degrees: float, transformation_point: tuple[float, float]=(0, 0)):
        if transformation_point != (0, 0):
            transformation_list.append(np.array([[1, 0, 0],
                                                 [0, 1, 0],
                                                 [-transformation_point[0], -transformation_point[1], 1]]))
            transformation_list.append(np.array([[1, 0, 0],
                                                 [0, 1, 0],
                                                 [transformation_point[0], transformation_point[1], 1]]))

        s = m.sin(m.radians(rotation_degrees))
        c = m.cos(m.radians(rotation_degrees))
        transformation_list.insert(1, np.array([[c, s, 0],
                                                [-s, c, 0],
                                                [0, 0, 1]]))


    def transform(self, coordinates: list[tuple[float, float]], transformation_list: list[list[list]]):
        transformation_matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        for matrix in transformation_list:
            transformation_matrix = np.matmul(transformation_matrix, matrix)

        new_coordinates = []
        for i in range(len(coordinates)):
            x = coordinates[i][0]
            y = coordinates[i][1]
            coord_matrix = np.array([x, y, 1])
            new_coord_matrix = np.matmul(coord_matrix, transformation_matrix)
            new_coordinates.append((new_coord_matrix[0].item(), new_coord_matrix[1].item()))

        return new_coordinates


    # transformation_typle_list = [ tranformation_type : str,
    #                               factor             : float,
    #                               rotation_center    : (float, float) | None
    #                               antiClockwise      : bool | None ]
    # tranformation can be: "move_up", "move_down", "move_left", "move_right",
    #                       "increase_scale", "decrease_scale",
    #                       "rotate_origin", "rotate_obj_center", "rotate_other"
    def apply_transformations(self, obj: Object, transformation_tuple_list: list[tuple[str, float, tuple[float, float]|None, bool|None]]):
        transformation_list = []
        for transformation_type, factor, rotation_center, antiClockwise in transformation_tuple_list:
            if antiClockwise != None and not antiClockwise:
                factor = -factor
            match transformation_type:
                case "move_up":
                    self.add_translation(transformation_list, self.up_vector[0]*factor,
                                                              self.up_vector[1]*factor)
                case "move_down":
                    self.add_translation(transformation_list, -self.up_vector[0]*factor,
                                                              -self.up_vector[1]*factor)
                case "move_left":
                    self.add_translation(transformation_list, -self.right_vector[0]*factor,
                                                              -self.right_vector[1]*factor)
                case "move_right":
                    self.add_translation(transformation_list, self.right_vector[0]*factor,
                                                              self.right_vector[1]*factor)
                case "increase_scale":
                    self.add_scaling(transformation_list, factor, self.get_center(obj.coordinates))
                case "decrease_scale":
                    self.add_scaling(transformation_list, 1/factor, self.get_center(obj.coordinates))
                case "rotate_origin":
                    self.add_rotation(transformation_list, factor)
                case "rotate_obj_center":
                    self.add_rotation(transformation_list, factor, self.get_center(obj.coordinates))
                case "rotate_other":
                    self.add_rotation(transformation_list, factor, rotation_center)

        obj.coordinates = self.transform(obj.coordinates, transformation_list)

        self.generate_normal_coordinates()
        self.update_viewport()


    def get_object(self, id: int) -> Object:
        return self.display_file[id+2]
