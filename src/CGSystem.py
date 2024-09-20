import numpy as np
import math as m

from CGSystemInterface import CGSystemInterface
from newObjWindow import NewObjWindow
from transformationWindow import TransformationWindow

from objects import Object, Point, Line, WireFrame


class CGSystem():
    def __init__(self):
        self.interface    : CGSystemInterface
        self.w_coord_min   : tuple[float, float]
        self.w_coord_max   : tuple[float, float]
        self.vp_coord_min  : tuple[float, float]
        self.vp_coord_max  : tuple[float, float]
        self.display_file : list[Object]

        self.display_file = list()

    def run(self):
        self.interface = CGSystemInterface(self)

        self.vp_coord_max = (self.interface.canvas_width, self.interface.canvas_height)
        self.vp_coord_min = (0, 0)

        self.w_coord_min = (-self.vp_coord_max[0]/2, -self.vp_coord_max[1]/2)
        self.w_coord_max = (self.vp_coord_max[0]/2, self.vp_coord_max[1]/2)

        norm_coord_x = self.normalize_coordinates([(-10000, 0), (10000, 0)])
        self.display_file.append(Line("X", "black", [(-10000, 0), (10000, 0)], norm_coord_x))
        norm_coord_y = self.normalize_coordinates([(0, -10000), (0, 10000)])
        self.display_file.append(Line("Y", "black", [(0, -10000), (0, 10000)], norm_coord_y))

        # window center lines
        norm_coord_x = self.normalize_coordinates([(-10000, 0), (10000, 0)])
        self.display_file.append(Line("X_window", "gray", [(-10000, 0), (10000, 0)], norm_coord_x))
        norm_coord_y = self.normalize_coordinates([(0, -10000), (0, 10000)])
        self.display_file.append(Line("Y_window", "gray", [(0, -10000), (0, 10000)], norm_coord_y))

        # test objects
        self.add_test()

        self.update_viewport()
        self.interface.app.mainloop()

    def add_object(self):
        NewObjWindow(self)


    def init_transformation_window(self, obj_id: int):
        obj = self.display_file[obj_id+4]
        TransformationWindow(self, obj)

    def add_message(self, message: str):
        self.interface.messageBox.insert(0, message)

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
        self.display_file.pop(id+4)

        self.update_viewport()

        self.add_message("Object Deleted")

    def update_normalized_coordinates(self):
        for obj in self.display_file:
            obj.normalized_coordinates = self.normalize_coordinates(obj.coordinates)

    def update_viewport(self):
        self.interface.clear_canvas()

        for obj in self.display_file:
            self.draw_object(obj)

    def draw_object(self, obj: Object):
        # nao utiliza mais
        # transformed_coordinates = []
        # for coord in obj.coordinates:
        #    transformed_coordinates.append(self.transform_coordinates(coord))

        obj_vp_coords = self.norm_coords_to_vp_coords(obj.normalized_coordinates)

        if (len(obj_vp_coords) == 1):
            coord = obj_vp_coords[0]
            self.interface.canvas.create_oval(coord[0], coord[1], coord[0], coord[1], fill=obj.color, width=5)

        else:
            for i in range(len(obj_vp_coords)-1):
                start_coord = obj_vp_coords[i]
                end_coord = obj_vp_coords[i+1]

                self.interface.canvas.create_line(start_coord[0], start_coord[1], end_coord[0], end_coord[1], fill=obj.color, width=2)

    def normalize_coordinates(self, coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
        normalized_coords: list[tuple[float, float]] = list()

        x_wmin, y_wmin = self.w_coord_min
        x_wmax, y_wmax = self.w_coord_max

        width = x_wmax - x_wmin
        height = y_wmax - y_wmin

        for coord in coords:
            x, y = coord
            normalized_x = 2 * (x - x_wmin) / width - 1
            normalized_y = 2 * (y - y_wmin) / height - 1 
            normalized_coords.append((normalized_x, normalized_y))

        for i, coord in enumerate(normalized_coords):
            print(f"{i}: {coord}")
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

        self.add_message("    - Coord:  (%d, %d)" % coord)
        self.add_message("    - Color:  %s" % color)
        self.add_message("    - Name:  %s" % name)
        self.add_message("Point added:")

        self.update_viewport()

    def add_line(self, name: str, color: str, start_coord: tuple[float, float], end_coord: tuple[float, float]):
        norm_coord = self.normalize_coordinates([start_coord, end_coord])
        line = Line(name, color, [start_coord, end_coord], norm_coord)

        self.display_file.append(line)
        self.interface.objects_listbox.insert("end", "%s [%s - Line]" % (name, color))

        self.add_message("    - Coord:  (%d, %d) to (%d, %d)" % (start_coord[0], start_coord[1], end_coord[0], end_coord[1]))
        self.add_message("    - Color:  %s" % color)
        self.add_message("    - Name:  %s" % name)
        self.add_message("Line added:")

        self.update_viewport()

    def add_wireframe(self, name: str, color: str, coord_list: list[tuple[float, float]]):
        if (len(coord_list) == 1):
            self.add_point(name, color, coord_list[0])
            return

        norm_coord = self.normalize_coordinates(coord_list)
        wf = WireFrame(name, color, coord_list, norm_coord)

        self.display_file.append(wf)
        self.interface.objects_listbox.insert("end", "%s [%s - Wireframe]" % (name, color))

        coords = ""
        for v in coord_list: coords += "(%d, %d) " % v
        self.add_message("    - Coord:  %s" % coords)
        self.add_message("    - Color:  %s" % color)
        self.add_message("    - Name:  %s" % name)
        self.add_message("Wireframe added:")

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

        self.add_message("Window coordinates seted to (%d, %d)" % (coord[0], coord[1]))


    # direction can be: "up", "down", "left", "right"
    # remember to sum +2 in obj_id
    def move_object(self, offset: int, direction: str, obj_id: int):
        obj = self.display_file[obj_id+4]

        offset_x: int = 0
        offset_y: int = 0
        match direction:
            case "up":
                offset_x = 0
                offset_y = offset
            case "down":
                offset_x = 0
                offset_y = -offset
            case "right":
                offset_x = offset
                offset_y = 0
            case "left":
                offset_x = -offset
                offset_y = 0

        transformation_list = []
        self.add_translation(transformation_list, offset_x, offset_y)
        obj.coordinates = self.transform(obj.coordinates, transformation_list)
        obj.normalized_coordinates = self.normalize_coordinates(obj.coordinates)

        self.update_viewport()

        obj_name = obj.name + "-" + obj.type
        self.add_message("%s moved %s by %d" % (obj_name, direction, offset))


    # direction can be: "up", "down", "left", "right"
    def move_window(self, offset: int, direction: str):
        offset_x_min : int = 0 
        offset_y_min : int = 0
        offset_x_max : int = 0
        offset_y_max : int = 0

        match direction:
            case "up":
                offset_y_min = offset
                offset_y_max = offset
            case "down":
                offset_y_min = -offset
                offset_y_max = -offset
            case "right":
                offset_x_min = offset
                offset_x_max = offset
            case "left":
                offset_x_min = -offset
                offset_x_max = -offset

        self.w_coord_min = (self.w_coord_min[0]+offset_x_min, self.w_coord_min[1]+offset_y_min)
        self.w_coord_max = (self.w_coord_max[0]+offset_x_max, self.w_coord_max[1]+offset_y_max)

        # window lines
        self.move_object(offset, direction, -1)
        self.move_object(offset, direction, -2)

        self.update_normalized_coordinates()
        self.update_viewport()

        self.add_message("window moved %s by %d" % (direction, offset))


    # inORout can be: "in", "out"
    def escale_object(self, escale_factor: float, object_id: int, inORout: str):
            obj = self.display_file[object_id+4]

            escale_factor = 1/escale_factor if (inORout == "out") else escale_factor 

            transformation_list = []
            self.add_scaling(transformation_list, escale_factor, self.get_center(obj.coordinates))
            obj.coordinates = self.transform(obj.coordinates, transformation_list)
            obj.normalized_coordinates = self.normalize_coordinates(obj.coordinates)

            self.update_viewport()

            obj_name = obj.name + "-" + obj.type
            self.add_message("%s escaled %s by %.2f" % (obj_name, inORout, escale_factor))


    # inORout can be: "in", "out"
    def zoom_window(self, zoom_factor: float, inORout: str):
        zoom_factor = 1/zoom_factor if (inORout == "in") else zoom_factor

        p0 = self.w_coord_min
        p2 = self.w_coord_max
        p1 = (p2[0], p0[1])
        p3 = (p0[0], p2[1])
        window_coordinates = [p0, p1, p2, p3]

        transformation_list = []
        self.add_scaling(transformation_list, zoom_factor)
        new_points = self.transform(window_coordinates, transformation_list)

        self.w_coord_min = new_points[0]
        self.w_coord_max = new_points[2]

        self.update_normalized_coordinates()
        self.update_viewport()

        self.add_message("window zoomed %s by %.2f" % (inORout, zoom_factor))

    def zoom_in(self, zoom_factor: float, isObject: bool, object_id: int):
        if (isObject):
            obj = self.display_file[object_id+4]
            transformation_list = []
            self.add_scaling(transformation_list, zoom_factor, self.get_center(obj.coordinates))
            obj.coordinates = self.transform(obj.coordinates, transformation_list)
            obj_name = obj.name + "-" + obj.type
            self.add_message("%s zoomed in by %d" % (obj_name, zoom_factor))

        else:
            zoom_factor = 1/zoom_factor
            p0 = self.w_coord_min
            p2 = self.w_coord_max
            p1 = (p2[0], p0[1])
            p3 = (p0[0], p2[1])
            window_coordinates = [p0, p1, p2, p3]
            transformation_list = []
            self.add_scaling(transformation_list, zoom_factor)
            new_points = self.transform(window_coordinates, transformation_list)

            self.w_coord_min = new_points[0]
            self.w_coord_max = new_points[2]

            self.add_message("window zoomed in by %f" % zoom_factor)

        self.update_viewport()


    def zoom_out(self, zoom_factor: float, isObject: bool, object_id: int):
        if (isObject):
            zoom_factor = 1/zoom_factor
            obj = self.display_file[object_id+4]
            transformation_list = []
            self.add_scaling(transformation_list, zoom_factor, self.get_center(obj.coordinates))
            obj.coordinates = self.transform(obj.coordinates, transformation_list)
            obj_name = obj.name + "-" + obj.type
            self.add_message("%s zoomed out by %d" % (obj_name, zoom_factor))

        else:
            p0 = self.w_coord_min
            p2 = self.w_coord_max
            p1 = (p2[0], p0[1])
            p3 = (p0[0], p2[1])

            window_coordinates = [p0, p1, p2, p3]
            transformation_list = []
            self.add_scaling(transformation_list, zoom_factor)
            new_points = self.transform(window_coordinates, transformation_list)

            self.w_coord_min = new_points[0]
            self.w_coord_max = new_points[2]

            self.add_message("window zoomed out by %f" % zoom_factor)

        self.update_viewport()

    # rotation_opt can be: "Origin", "Obj Center" and "Other"
    def rotate_object(self, antiClockwise: bool, degrees: int, object_id: int, rotation_opt: str, rotation_point: tuple[float, float]):
        if not antiClockwise:
            degrees = -degrees

        obj = self.display_file[object_id+4]
        obj_name = obj.name + "-" + obj.type

        transformation_list = []
        message: str
        if (rotation_opt == "Origin"):
            self.add_rotation(transformation_list, degrees, (0, 0))
            message = "%s rotated %d degree by the Origin %s" % (obj_name, degrees, ("anti-clockwise" if (antiClockwise) else "clockwise"))
        elif(rotation_opt == "Obj Center"):
            self.add_rotation(transformation_list, degrees, self.get_center(obj.coordinates))
            message = "%s rotated %d degree by the Object Center %s" % (obj_name, degrees, ("anti-clockwise" if (antiClockwise) else "clockwise"))
        else:
            self.add_rotation(transformation_list, degrees, rotation_point)
            message = "%s rotated %d degree by the point (%d, %d) %s" % (obj_name, degrees, rotation_point[0], rotation_point[1], ("anti-clockwise" if (antiClockwise) else "clockwise"))

        obj.coordinates = self.transform(obj.coordinates, transformation_list)
        obj.normalized_coordinates = self.normalize_coordinates(obj.coordinates)

        self.update_viewport()

        self.add_message(message)
        

    def rotate_window(self, degrees: int, antiClockwise: bool):
        self.add_message("1.3 TODO")
        #self.add_message("Window rotated %d degrees %s" % (degrees, ("anti-clockwise" if (antiClockwise) else "clockwise")))

        self.update_viewport()

    def get_center(self, coordinates: list[tuple[float, float]]):
        # if the object is a polygon, the first and the last points are the same
        coordinates = coordinates.copy()
        if (coordinates[0] == coordinates[-1]) and (len(coordinates) > 1):
            coordinates.pop()

        average_x = 0
        average_y = 0
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


    def add_test(self):
        #self.add_wireframe("square", "blue", [(60, 60), (60, 10), (10, 10), (10, 60), (60, 60)])
        #self.add_wireframe("L", "red", [(-70, 70), (-70, 30), (-45, 30)])
        self.add_wireframe("triangle", "green", [(-70, -70), (-30, -70), (-30, -40), (-70, -70)])
        #self.add_point("point", "green", (50,-50))
 
