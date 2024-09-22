import numpy as np
import math as m

from CGSystemInterface import CGSystemInterface
from newObjWindow import NewObjWindow
from transformationWindow import TransformationWindow

from objects import Object, Point, Line, WireFrame
import transformationWindow


class CGSystem():
    def __init__(self):
        self.interface    : CGSystemInterface
        self.w_coord_min  : tuple[float, float]
        self.w_coord_max  : tuple[float, float]
        self.vp_coord_min : tuple[float, float]
        self.vp_coord_max : tuple[float, float]
        self.up_vector   : tuple[float, float]
        self.display_file : list[Object]

        self.width : float
        self.height : float

        self.display_file = list()


    def run(self):
        self.interface = CGSystemInterface(self)

        self.up_vector = (0, 1)

        self.vp_coord_max = (self.interface.canvas_width, self.interface.canvas_height)
        self.vp_coord_min = (0, 0)

        self.w_coord_min = (-self.vp_coord_max[0]/2, -self.vp_coord_max[1]/2)
        self.w_coord_max = (self.vp_coord_max[0]/2, self.vp_coord_max[1]/2)

        self.width = self.w_coord_max[0] - self.w_coord_min[0]
        self.height = self.w_coord_max[1] - self.w_coord_min[1]

        # world center lines
        norm_coord_x = self.normalize_coordinates([(-10000, 0), (10000, 0)])
        self.display_file.append(Line("X", "black", [(-10000, 0), (10000, 0)], norm_coord_x))
        norm_coord_y = self.normalize_coordinates([(0, -10000), (0, 10000)])
        self.display_file.append(Line("Y", "black", [(0, -10000), (0, 10000)], norm_coord_y))

        # test objects
        self.add_test()

        self.update_viewport()
        self.interface.app.mainloop()


    def add_object(self):
        NewObjWindow(self)


    def init_transformation_window(self, obj_id: int):
        obj = self.get_object(obj_id)
        TransformationWindow(self, obj)


    def transform_window_to_vp_coordinates(self, coord: tuple[float, float]) -> tuple[float, float]:
        x_w = coord[0]
        y_w = coord[1]

        x_wmin, y_wmin  = self.w_coord_min
        x_wmax, y_wmax = self.w_coord_max

        x_vpmin, y_vpmin = self.vp_coord_min
        x_vpmax, y_vpmax = self.vp_coord_max

        x_vp = ( (x_w - x_wmin) / (x_wmax - x_wmin) ) * (x_vpmax - x_vpmin)
        y_vp = ( 1 - ((y_w - y_wmin) / (y_wmax - y_wmin)) ) * (y_vpmax - y_vpmin)

        return (x_vp, y_vp)


    def del_object(self, id: int):
        self.interface.objects_listbox.delete(id)
        self.display_file.pop(id+2)

        self.update_viewport()


    def update_normalized_coordinates(self):
        for obj in self.display_file:
            obj.normalized_coordinates = self.normalize_coordinates(obj.coordinates)


    def update_viewport(self):
        self.interface.clear_canvas()

        for obj in self.display_file:
            obj_vp_coords = self.norm_coords_to_vp_coords(obj.normalized_coordinates)
            self.interface.draw_object(obj, obj_vp_coords)


    def get_projection(self, a, b, p):
        a, b, p = np.array(a), np.array(b), np.array(p) 

        ap = p - a
        ab = b - a
        result = a + np.dot(ap, ab) / np.dot(ab, ab) * ab

        return result


    def normalize_coordinates(self, coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
        normalized_coords: list[tuple[float, float]] = list()

        p0, p1, p2, p3 = self.get_window_coordinates()
        width = m.dist(p0, p1)
        height = m.dist(p1, p2)

        for coord in coords:
            x, y = coord

            """
            print("p0", p0)
            print("p3", p3)
            print("coord", coord)
            proj_y = self.get_projection(p0, p3, coord)
            proj_x = self.get_projection(p0, p1, coord)
            print("proj_y", proj_y)
            print("proj_x", proj_x)
            

            dx = m.dist(proj_y, coord)
            dx = -dx if (coord[0] < proj_y[0]) else dx

            dy = m.dist(proj_x, coord)
            dy = -dy if (coord[1] < proj_x[1]) else dy
            """

            normalized_x = 2 * (x - p0[0]) / width - 1
            normalized_y = 2 * (y - p0[1]) / height - 1
            # normalized_x = 2 * dx / width - 1
            # normalized_y = 2 * dy / height - 1
            normalized_coords.append((normalized_x, normalized_y))

        #print(normalized_coords)
        return normalized_coords


    def norm_coords_to_vp_coords(self, norm_coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
        vp_coords: list[tuple[float, float]] = list()

        x_vp_max, y_vp_max = self.vp_coord_max

        for norm_coord in norm_coords:
            norm_coord = (((norm_coord[0] + 1) / 2), ((norm_coord[1] +1) / 2))
            x = norm_coord[0] * x_vp_max 
            y = self.vp_coord_max[1] - (norm_coord[1] * y_vp_max)
            vp_coords.append((x, y))

        return vp_coords


    def add_point(self,name: str, color: str, coord: tuple[float, float]):
        norm_coord = self.normalize_coordinates([coord])
        point = Point(name, color, [coord], norm_coord)

        self.display_file.append(point)
        self.interface.objects_listbox.insert("end", "%s [%s - Point]" % (name, color))

        self.update_viewport()


    def add_line(self, name: str, color: str, start_coord: tuple[float, float], end_coord: tuple[float, float]):
        norm_coord = self.normalize_coordinates([start_coord, end_coord])
        line = Line(name, color, [start_coord, end_coord], norm_coord)

        self.display_file.append(line)
        self.interface.objects_listbox.insert("end", "%s [%s - Line]" % (name, color))

        self.update_viewport()


    def add_wireframe(self, name: str, color: str, coord_list: list[tuple[float, float]]):
        if (len(coord_list) == 1):
            self.add_point(name, color, coord_list[0])
            return

        norm_coord = self.normalize_coordinates(coord_list)
        wf = WireFrame(name, color, coord_list, norm_coord)

        self.display_file.append(wf)
        self.interface.objects_listbox.insert("end", "%s [%s - Wireframe]" % (name, color))

        self.update_viewport()


    def set_window_coord(self, coord: tuple[float, float]):
        width = abs(self.w_coord_max[0] - self.w_coord_min[0])
        height = abs(self.w_coord_max[1] - self.w_coord_min[1])

        offset_X = width / 2
        offset_Y = height / 2

        self.w_coord_min = (coord[0]-offset_X, coord[1]-offset_Y)
        self.w_coord_max = (coord[0]+offset_X, coord[1]+offset_Y)

        self.update_normalized_coordinates()
        self.update_viewport()


    # direction can be: "up", "down", "left", "right"
    def move_object(self, offset: int, direction: str, obj_id: int):
        obj = self.get_object(obj_id)

        offset_x: int = 0
        offset_y: int = 0
        match direction:
            case   "up"  : offset_x, offset_y = 0, offset
            case "down"  : offset_x, offset_y = 0, -offset
            case "right" : offset_x, offset_y =  offset, 0
            case "left"  : offset_x, offset_y = -offset, 0

        transformation_list = []
        self.add_translation(transformation_list, offset_x, offset_y)
        obj.coordinates = self.transform(obj.coordinates, transformation_list)
        obj.normalized_coordinates = self.normalize_coordinates(obj.coordinates)

        self.update_viewport()


    # direction can be: "up", "down", "left", "right"
    def move_window(self, offset: int, direction: str):
        offset_x_min : int = 0 
        offset_y_min : int = 0
        offset_x_max : int = 0
        offset_y_max : int = 0

        match direction:
            case    "up" : offset_y_min, offset_y_max =  offset,  offset
            case  "down" : offset_y_min, offset_y_max = -offset, -offset
            case "right" : offset_x_min, offset_x_max =  offset,  offset
            case  "left" : offset_x_min, offset_x_max = -offset, -offset

        self.w_coord_min = (self.w_coord_min[0]+offset_x_min, self.w_coord_min[1]+offset_y_min)
        self.w_coord_max = (self.w_coord_max[0]+offset_x_max, self.w_coord_max[1]+offset_y_max)

        self.update_normalized_coordinates()
        self.update_viewport()


    # inORout can be: "in", "out"
    def scale_object(self, scale_factor: float, object_id: int, inORout: str):
            obj = self.get_object(object_id)

            scale_factor = 1/scale_factor if (inORout == "out") else scale_factor 

            transformation_list = []
            self.add_scaling(transformation_list, scale_factor, self.get_center(obj.coordinates))
            obj.coordinates = self.transform(obj.coordinates, transformation_list)
            obj.normalized_coordinates = self.normalize_coordinates(obj.coordinates)

            self.update_viewport()


    # inORout can be: "in", "out"
    def zoom_window(self, zoom_factor: float, inORout: str):
        zoom_factor = 1/zoom_factor if (inORout == "in") else zoom_factor

        window_coordinates = self.get_window_coordinates()

        transformation_list = []
        self.add_scaling(transformation_list, zoom_factor)
        new_points = self.transform(window_coordinates, transformation_list)

        self.w_coord_min = new_points[0]
        self.w_coord_max = new_points[2]

        self.update_normalized_coordinates()
        self.update_viewport()


    # rotation_opt can be: "Origin", "Obj Center" and "Other"
    def rotate_object(self, antiClockwise: bool, degrees: int, object_id: int, rotation_opt: str, rotation_point: tuple[float, float]=(0, 0)):
        if not antiClockwise:
            degrees = -degrees

        obj = self.get_object(object_id)

        transformation_list = []
        if (rotation_opt == "Origin"):
            self.add_rotation(transformation_list, degrees, (0, 0))
        elif(rotation_opt == "Obj Center"):
            self.add_rotation(transformation_list, degrees, self.get_center(obj.coordinates))
        else:
            self.add_rotation(transformation_list, degrees, rotation_point)

        obj.coordinates = self.transform(obj.coordinates, transformation_list)
        obj.normalized_coordinates = self.normalize_coordinates(obj.coordinates)

        self.update_viewport()


    def rotate_window(self, degrees: int, antiClockwise: bool):
        if not antiClockwise:
            degrees = -degrees

        # Move window
        window_coordinates = self.get_window_coordinates()
        transformation_list = []
        self.add_rotation(transformation_list, degrees, self.get_center(window_coordinates))
        new_coords = self.transform(window_coordinates, transformation_list)
        print(new_coords)
        self.w_coord_min, self.w_coord_max = new_coords[0], new_coords[2]



        # add translation transformation
        w_center = self.get_center(self.get_window_coordinates())
        transformation_list = []
        self.add_translation(transformation_list, -w_center[0], -w_center[1])
        #-------------------------

        # get vup
        s = m.sin(m.radians(degrees))
        c = m.cos(m.radians(degrees))
        x, y = self.up_vector
        x_new = c * x - s * y
        y_new = s * x + c * y
        up_norm = np.linalg.norm([x_new, y_new])
        self.up_vector = (x_new/up_norm, y_new/up_norm)
        #------------------------

        # add rotation transformation
        up_vector = np.array([x_new, y_new])
        norm_up = np.linalg.norm(up_vector)

        y_axis = np.array([0, 1])
        norm_y = np.linalg.norm(y_axis)

        dot_product = np.dot(up_vector, y_axis)
        delta_angle = round(m.degrees(m.acos(dot_product / (norm_up * norm_y))))
        print(delta_angle)
        self.add_rotation(transformation_list, -delta_angle, (0, 0))
        #--------------------------

        #apply transformation
        p0, p1, p2, p3 = self.get_window_coordinates()
        #width = m.dist(p0, p1)
        print(w_center)
        print(self.width)
        self.set_window_coord((0, 0))
        #height = m.dist(p1, p2)
        for obj in self.display_file:
            coords = obj.coordinates
            transformed_coords = self.transform(coords, transformation_list)

            normalized_coords = list()
            for coord in transformed_coords:
                x, y = coord

                normalized_x = 2 * (x - p0[0]) / self.width - 1
                normalized_y = 2 * (y - p0[1]) / self.height - 1

                #normalized_x = 2 * dx / width - 1
                #normalized_y = 2 * dy / height - 1
                normalized_coords.append((normalized_x, normalized_y))

            obj.normalized_coordinates = normalized_coords

        self.update_viewport()

        """
        window_coordinates = self.get_window_coordinates()
        window_center = self.get_center(window_coordinates)

        # 1. Translate window to world center
        self.set_window_coord((0, 0))


        # 1.1 translate world by [-w_center_x, -w_center_y]
        offset_x = window_center[0] - self.world_center[0]
        offset_y = window_center[1] - self.world_center[1]
        for i in range(len(self.display_file)):
            obj = self.display_file[i]
            transformation_list = []
            self.add_translation(transformation_list, -offset_x, -offset_y)
            obj.coordinates = self.transform(obj.coordinates, transformation_list)
            obj.normalized_coordinates = self.normalize_coordinates(obj.coordinates)

        # 2. get up_vector
        s = m.sin(m.radians(degrees))
        c = m.cos(m.radians(degrees))
        x, y = self.get_vup_vector()
        x_new = c * x - s * y
        y_new = s * x + c * y

        # 2.1 calculate the angle between up vector and world Y axis
        up_vector = np.array([x_new, y_new])
        norm_up = np.linalg.norm(up_vector)

        y_axis = np.array([x, y])
        norm_y = np.linalg.norm(y_axis)

        dot_product = np.dot(up_vector, y_axis)
        delta_angle = round(m.degrees(m.acos(dot_product / (norm_up * norm_y))))

        # 3. rotates world
        for i in range(len(self.display_file)):
            self.rotate_object(antiClockwise, -delta_angle, i-4, "Origin")


        transf_list = []
        new_center = (self.world_center[0]-offset_x, self.world_center[1]-offset_y)
        delta_angle = -delta_angle if (antiClockwise) else delta_angle
        self.add_rotation(transf_list, delta_angle, self.world_center)
        self.world_center = self.transform([new_center], transf_list)[0]


        # 4. Normalize and update viewport
        self.update_normalized_coordinates()
        self.update_viewport()
        """


    def get_vup_vector(self):
        window_coordinates = self.get_window_coordinates()
        w_center_x, w_center_y = self.get_center(window_coordinates)

        p2, p3 = window_coordinates[2], window_coordinates[3]
        xm = (p2[0] + p3[0]) / 2
        ym = (p2[1] + p3[1]) / 2

        x_vup = xm - w_center_x
        y_vup = ym - w_center_y

        return (x_vup, y_vup)


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
                    self.add_translation(transformation_list, 0, factor)
                case "move_down":
                    self.add_translation(transformation_list, 0, -factor)
                case "move_left":
                    self.add_translation(transformation_list, -factor, 0)
                case "move_right":
                    self.add_translation(transformation_list, factor, 0)
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
        obj.normalized_coordinates = self.normalize_coordinates(obj.coordinates)

        self.update_viewport()

    def get_window_coordinates(self):
        p0 = self.w_coord_min
        p2 = self.w_coord_max
        p1 = (p2[0], p0[1])
        p3 = (p0[0], p2[1])
        window_coordinates = [p0, p1, p2, p3]

        return window_coordinates


    def add_test(self):
        #self.add_wireframe("square", "blue", [(60, 60), (60, 10), (10, 10), (10, 60), (60, 60)])
        self.add_wireframe("L", "red", [(-70, 70), (-70, 30), (-45, 30)])
        self.add_wireframe("triangle", "green", [(-70, -70), (-30, -70), (-30, -40), (-70, -70)])
        #self.add_point("point", "green", (50,-50))
 

    def get_object(self, id: int) -> Object:
        return self.display_file[id+2]
