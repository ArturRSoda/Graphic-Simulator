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
        self.Wcoord_min   : tuple[float, float]
        self.Wcoord_max   : tuple[float, float]
        self.VPcoord_min  : tuple[float, float]
        self.VPcoord_max  : tuple[float, float]
        self.display_file : list[Object]

        self.display_file = list()
        self.display_file.append(Line("X", "black", [(-10000, 0), (10000, 0)]))
        self.display_file.append(Line("Y", "black", [(0, -10000), (0, 10000)]))

    def run(self):
        self.interface = CGSystemInterface(self)

        self.VPcoord_max = (self.interface.canvas_width, self.interface.canvas_height)
        self.VPcoord_min = (0, 0)

        self.Wcoord_min = (-self.VPcoord_max[0]/2, -self.VPcoord_max[1]/2)
        self.Wcoord_max = (self.VPcoord_max[0]/2, self.VPcoord_max[1]/2)

        # test objects
        self.add_test()

        self.update_viewport()
        self.interface.app.mainloop()

    def add_object(self):
        NewObjWindow(self)


    def init_transformation_window(self, obj_id: int):
        obj = self.display_file[obj_id+2]
        TransformationWindow(self, obj)

    def add_message(self, message: str):
        self.interface.messageBox.insert(0, message)

    def transform_coordinates(self, coord: tuple[int, int]) -> tuple[float, float]:
        Xw = coord[0]
        Yw = coord[1]

        Xwmin, Ywmin  = self.Wcoord_min
        Xwmax, Ywmax = self.Wcoord_max

        Xvpmin, Yvpmin = self.VPcoord_min
        Xvpmax, Yvpmax = self.VPcoord_max

        Xvp = ( (Xw - Xwmin) / (Xwmax - Xwmin) ) * (Xvpmax - Xvpmin)
        Yvp = ( 1 - ((Yw - Ywmin) / (Ywmax - Ywmin)) ) * (Yvpmax - Yvpmin)


        return (Xvp, Yvp)

    def del_object(self, id: int):
        self.interface.objects_listbox.delete(id)
        self.display_file.pop(id+2)

        self.update_viewport()

        self.add_message("Object Deleted")

    def update_viewport(self):
        self.interface.clear_canvas()

        for obj in self.display_file:
            self.draw_object(obj)

    def draw_object(self, obj: Object):
        transformed_coordinates = []
        for coord in obj.coordinates:
            transformed_coordinates.append(self.transform_coordinates(coord))

        if (len(transformed_coordinates) == 1):
            coord = transformed_coordinates[0]
            self.interface.canvas.create_oval(coord[0], coord[1], coord[0], coord[1], fill=obj.color, width=5)

        else:
            for i in range(len(transformed_coordinates)-1):
                start_coord = transformed_coordinates[i]
                end_coord = transformed_coordinates[i+1]

                self.interface.canvas.create_line(start_coord[0], start_coord[1], end_coord[0], end_coord[1], fill=obj.color, width=2)

    def add_point(self,name: str, color: str, coord: tuple[int, int]):
        point = Point(name, color, [coord])

        self.display_file.append(point)
        self.interface.objects_listbox.insert("end", "%s [%s - Point]" % (name, color))

        self.add_message("    - Coord:  (%d, %d)" % coord)
        self.add_message("    - Color:  %s" % color)
        self.add_message("    - Name:  %s" % name)
        self.add_message("Point added:")

        self.update_viewport()

    def add_line(self, name: str, color: str, start_coord: tuple[int, int], end_coord: tuple[int, int]):
        line = Line(name, color, [start_coord, end_coord])

        self.display_file.append(line)
        self.interface.objects_listbox.insert("end", "%s [%s - Line]" % (name, color))

        self.add_message("    - Coord:  (%d, %d) to (%d, %d)" % (start_coord[0], start_coord[1], end_coord[0], end_coord[1]))
        self.add_message("    - Color:  %s" % color)
        self.add_message("    - Name:  %s" % name)
        self.add_message("Line added:")

        self.update_viewport()

    def add_wireframe(self, name: str, color: str, coord_list: list[tuple[int, int]]):
        if (len(coord_list) == 1):
            self.add_point(name, color, coord_list[0])
            return

        wf = WireFrame(name, color, coord_list)

        self.display_file.append(wf)
        self.interface.objects_listbox.insert("end", "%s [%s - Wireframe]" % (name, color))

        coords = ""
        for v in coord_list: coords += "(%d, %d) " % v
        self.add_message("    - Coord:  %s" % coords)
        self.add_message("    - Color:  %s" % color)
        self.add_message("    - Name:  %s" % name)
        self.add_message("Wireframe added:")

        self.update_viewport()

    def set_window_coord(self, coord: tuple[int, int]):
        width = abs(self.Wcoord_max[0] - self.Wcoord_min[0])
        height = abs(self.Wcoord_max[1] - self.Wcoord_min[1])

        offset_X = width / 2
        offset_Y = height / 2

        self.Wcoord_min = (coord[0]-offset_X, coord[1]-offset_Y)
        self.Wcoord_max = (coord[0]+offset_X, coord[1]+offset_Y)
        self.update_viewport()

        self.add_message("Window coordinates seted to (%d, %d)" % (coord[0], coord[1]))

    # if isObject == True then
    #     - move object
    #     - and object_id will have a value (remember to sum +2 on object_id, because of the 2 central lines)
    # else:
    #     - move window
    #     - object_id = None
    def move_up(self, offset: int, isObject: bool, object_id: int):
        if (isObject):
            obj = self.display_file[object_id+2]
            obj.coordinates = self.transform(obj.coordinates, 0, offset)
            obj_name = obj.name + "-" + obj.type
            self.add_message("%s moved up by %d" % (obj_name, offset))

        else:
            self.Wcoord_min = (self.Wcoord_min[0], self.Wcoord_min[1]+offset)
            self.Wcoord_max = (self.Wcoord_max[0], self.Wcoord_max[1]+offset)
            
            self.add_message("window moved up by %d" % offset)

        self.update_viewport()


    def move_down(self, offset: int, isObject: bool, object_id: int):
        if (isObject):
            obj = self.display_file[object_id+2]
            obj.coordinates = self.transform(obj.coordinates, 0, -offset)
            obj_name = obj.name + "-" + obj.type
            self.add_message("%s moved down by %d" % (obj_name, offset))

        else:
            self.Wcoord_min = (self.Wcoord_min[0], self.Wcoord_min[1]-offset)
            self.Wcoord_max = (self.Wcoord_max[0], self.Wcoord_max[1]-offset)

            self.add_message("window moved down by %d" % offset)

        self.update_viewport()

    def move_left(self, offset: int, isObject: bool, object_id: int):
        if (isObject):
            obj = self.display_file[object_id+2]
            obj.coordinates = self.transform(obj.coordinates, -offset, 0)
            obj_name = obj.name + "-" + obj.type
            self.add_message("%s moved left by %d" % (obj_name, offset))

        else:
            self.Wcoord_min = (self.Wcoord_min[0]-offset, self.Wcoord_min[1])
            self.Wcoord_max = (self.Wcoord_max[0]-offset, self.Wcoord_max[1])

            self.add_message("window moved left by %d" % offset)

        self.update_viewport()

    def move_right(self, offset: int, isObject: bool, object_id: int):
        if (isObject):
            obj = self.display_file[object_id+2]
            obj.coordinates = self.transform(obj.coordinates, offset, 0)
            obj_name = obj.name + "-" + obj.type
            self.add_message("%s moved right by %d" % (obj_name, offset))

        else:
            self.Wcoord_min = (self.Wcoord_min[0]+offset, self.Wcoord_min[1])
            self.Wcoord_max = (self.Wcoord_max[0]+offset, self.Wcoord_max[1])

            self.add_message("window moved right by %d" % offset)

        self.update_viewport()


    def zoom_in(self, zoom_factor: float, isObject: bool, object_id: int):
        if (isObject):
            obj = self.display_file[object_id+2]
            obj.coordinates = self.transform(obj.coordinates, 0, 0, zoom_factor, 0, self.get_center(obj.coordinates))
            obj_name = obj.name + "-" + obj.type
            self.add_message("%s zoomed in by %d" % (obj_name, zoom_factor))

        else:
            zoom_factor = 1/zoom_factor
            p0 = self.Wcoord_min
            p2 = self.Wcoord_max
            p1 = (p2[0], p0[1])
            p3 = (p0[0], p2[1])
            window_coordinates = [p0, p1, p2, p3]
            new_points = self.transform(window_coordinates, 0, 0, zoom_factor, 0, self.get_center(window_coordinates))

            self.Wcoord_min = new_points[0]
            self.Wcoord_max = new_points[2]

            self.add_message("window zoomed in by %f" % zoom_factor)

        self.update_viewport()


    def zoom_out(self, zoom_factor: float, isObject: bool, object_id: int):
        if (isObject):
            zoom_factor = 1/zoom_factor
            obj = self.display_file[object_id+2]
            obj.coordinates = self.transform(obj.coordinates, 0, 0, zoom_factor, 0, self.get_center(obj.coordinates))
            obj_name = obj.name + "-" + obj.type
            self.add_message("%s zoomed out by %d" % (obj_name, zoom_factor))

        else:
            p0 = self.Wcoord_min
            p2 = self.Wcoord_max
            p1 = (p2[0], p0[1])
            p3 = (p0[0], p2[1])

            window_coordinates = [p0, p1, p2, p3]
            new_points = self.transform(window_coordinates, 0, 0, zoom_factor, 0, self.get_center(window_coordinates))

            self.Wcoord_min = new_points[0]
            self.Wcoord_max = new_points[2]

            self.add_message("window zoomed out by %f" % zoom_factor)

        self.update_viewport()

    # Similar to move up function
    #     if isObject == True then 
    #         object_id = None
    #         rotation_opt = None
    #         rotation_point = None
    #
    # rotation_opt can be: "Origin", "Obj Center" and "Other"
    def rotate(self, isObject: bool, antiClockwise: bool, degrees: int, object_id: int, rotation_opt: str, rotation_point: tuple[int, int]):
        if not antiClockwise:
            degrees = -degrees

        if (isObject):
            obj = self.display_file[object_id+2]
            obj_name = obj.name + "-" + obj.type

            message: str
            if (rotation_opt == "Origin"):
                obj.coordinates = self.transform(obj.coordinates, 0, 0, 0, degrees)
                message = "%s rotated %d degree by the Origin %s" % (obj_name, degrees, ("anti-clockwise" if (antiClockwise) else "clockwise"))
            elif(rotation_opt == "Obj Center"):
                obj.coordinates = self.transform(obj.coordinates, 0, 0, 0, degrees, self.get_center(obj.coordinates))
                message = "%s rotated %d degree by the Object Center %s" % (obj_name, degrees, ("anti-clockwise" if (antiClockwise) else "clockwise"))
            else:
                obj.coordinates = self.transform(obj.coordinates, 0, 0, 0, degrees, rotation_point)
                message = "%s rotated %d degree by the point (%d, %d) %s" % (obj_name, degrees, rotation_point[0], rotation_point[1], ("anti-clockwise" if (antiClockwise) else "clockwise"))

            self.add_message(message)
        
        else:
            self.add_message("1.3 TODO")
            #self.add_message("Window rotated %d degrees %s" % (degrees, ("anti-clockwise" if (antiClockwise) else "clockwise")))

        self.update_viewport()

    def get_center(self, coordinates: list[tuple[float, float]]):
        # if the object is a polygon, the first and the last points are the same
        coordinates = coordinates.copy()
        if coordinates[0] == coordinates[-1]:
            last_coord = coordinates.pop()

        average_x = 0
        average_y = 0
        for x, y in coordinates:
            average_x += x
            average_y += y
        points_num = len(coordinates)
        average_x /= points_num
        average_y /= points_num

        return (average_x, average_y)

    def transform(self, coordinates: list[tuple[float, float]], offset_x: float=0, offset_y: float=0, scale_factor: float=0, rotation_degrees: float=0, transform_point: tuple[float, float]=(0,0)):
        transform_list = []
        center = self.get_center(coordinates)
        if transform_point != (0, 0):
            transform_list.append(np.array([[1, 0, 0],
                                            [0, 1, 0],
                                            [-transform_point[0], -transform_point[1], 1]]))
            transform_list.append(np.array([[1, 0, 0],
                                            [0, 1, 0],
                                            [transform_point[0], transform_point[1], 1]]))
        if offset_x != 0 or offset_y != 0:
            transform_list.insert(1, np.array([[1, 0, 0],
                                               [0, 1, 0],
                                               [offset_x, offset_y, 1]]))
        if scale_factor != 0:
            transform_list.insert(1, np.array([[scale_factor, 0, 0],
                                               [0, scale_factor, 0],
                                               [0, 0, 1]]))
        if rotation_degrees != 0:
            s = m.sin(m.radians(rotation_degrees))
            c = m.cos(m.radians(rotation_degrees))
            transform_list.insert(1, np.array([[c, -s, 0],
                                               [s, c, 0],
                                               [0, 0, 1]]))

        transform_matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        for matrix in transform_list:
            transform_matrix = np.matmul(transform_matrix, matrix)

        new_coordinates = []
        for i in range(len(coordinates)):
            x = coordinates[i][0]
            y = coordinates[i][1]
            coord_matrix = np.array([x, y, 1])
            new_coord_matrix = np.matmul(coord_matrix, transform_matrix)
            new_coordinates.append((new_coord_matrix[0].item(), new_coord_matrix[1].item()))

        return new_coordinates

    def apply_transformations(self, object: Object, transformation_list: list[tuple[str, float, tuple[int, int]|None, bool|None]]):
        # transformation_list = [ tranformation  : str,
        #                         factor         : float,
        #                         rotation_coord : (int, int) | None
        #                         antiClockwise  : bool | None
        #                       ]
        #   - tranformation can be: "move_up", "move_down", "move_left", "move_right",
        #                           "increase_escale", "decrease_escale",
        #                           "rotate_origin", "rotate_obj_center", "rotate_other"
        #
        #   if transformaton in ("move_up", "move_down", "move_left", "move_right") then:
        #       - factor is the offset 
        #       - rotation_coord = None
        #       - antiClockwise = None
        #
        #   if transformation in ("increase_escale", "decrease_escale") then
        #       - factor is the escale factor to increase or decrease
        #       - rotation_coord = None
        #       - antiClockwise = None
        #
        #   if transformation in ("rotate_origin", "rotate_obj_center", "rotate_other") then
        #       - factor is the degrees
        #       - rotation_coord is the coord to rotate IF TRANSFORMATION = "rotate_other"
        #       - antiClockwise = True if antiClockwise else False
        print(object.name)
        print(transformation_list)

    def add_test(self):
        self.add_wireframe("square", "blue", [(60, 60), (60, 10), (10, 10), (10, 60), (60, 60)])
        self.add_wireframe("L", "red", [(-70, 70), (-70, 30), (-45, 30)])
        self.add_wireframe("triangle", "green", [(-70, -70), (-30, -70), (-30, -40), (-70, -70)])
 
