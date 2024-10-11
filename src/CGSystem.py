import numpy as np
import math as m

from CGSystemInterface import CGSystemInterface
from newObjWindow import NewObjWindow
from transformationWindow import TransformationWindow
from objects import BSplineCurve, Object, Point, Line, Polygon, WireFrame, BezierCurve, BSplineCurve
from window import Window
from transformer import Transformer
from clipper import Clipper


class CGSystem():
    def __init__(self):
        self.interface     : CGSystemInterface
        self.window        : Window
        self.transformer : Transformer
        self.clipper       : Clipper

        self.vp_coord_min  : tuple[float, float]
        self.vp_coord_max  : tuple[float, float]

        # add aspect ratio

        self.up_vector     : tuple[float, float]
        self.right_vector  : tuple[float, float]

        self.display_file  : list[Object]

    def run(self):
        self.interface = CGSystemInterface(self)
        self.transformer = Transformer(self)
        self.clipper = Clipper()

        self.vp_coord_max = (self.interface.subcanvas_width, self.interface.subcanvas_height)
        self.vp_coord_min = (0, 0)

        self.window = Window([
            (-self.vp_coord_max[0]/2, -self.vp_coord_max[1]/2),
            ( self.vp_coord_max[0]/2, -self.vp_coord_max[1]/2),
            ( self.vp_coord_max[0]/2,  self.vp_coord_max[1]/2),
            (-self.vp_coord_max[0]/2,  self.vp_coord_max[1]/2)
        ])

        self.up_vector = (0, 1)
        self.right_vector = (1, 0)

        self.display_file = list()

        # world center lines
        self.display_file.append(Line("X", "black", [(-1000, 0), (1000, 0)], []))
        self.display_file.append(Line("Y", "black", [(0, -1000), (0, 1000)], []))

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

        norm_coord = self.normalize_object_coordinates(coord_list)
        plg = Polygon(name, color, coord_list, norm_coord)

        self.display_file.append(plg)
        self.interface.objects_listbox.insert("end", "%s [%s - Polygon]" % (name, color))

        self.generate_normal_coordinates()
        self.update_viewport()


    # type can be "bspline" or "bezier"
    def add_curve(self, name: str, color: str, coord_list: list[tuple[float, float]], type: str):
        curve_class = BezierCurve if (type == "bezier") else BSplineCurve

        plg = curve_class(name, color, coord_list, [])
        plg.normalized_coordinates = self.normalize_object_coordinates(plg.coordinates)

        self.display_file.append(plg)
        self.interface.objects_listbox.insert("end", "%s [%s - Curve]" % (name, color))

        self.generate_normal_coordinates()
        self.update_viewport()


    def add_test(self):
        #self.add_wireframe("L", "red", [(-70, 70), (-70, 30), (-45, 30)])
        #self.add_wireframe("wireframe triangle", "green", [(-70, -70), (-30, -70), (-30, -40), (-70, -70)])
        #self.add_polygon("triangle", "green", [(10, 10), (100, 10), (100, 100)])
        #self.add_point("point", "blue", (10, 10))
        #self.add_polygon("concave hexagon", "red", [(100, 100), (150, 100), (200, 130), (160, 170), (200, 200), (100, 200)])
        #self.add_wireframe("concave wireframe hexagon", "red", [(-100, -100), (-150, -100), (-200, -130), (-160, -170), (-200, -200), (-100, -200), (-100, -100)])
        self.add_curve("curva", "pink", [(25, 25), (40, 75), (70, 75), (90, 30), (120, 100)], "bezier")
        self.add_curve("curva", "black", [(25, 25), (40, 75), (70, 75)], "bezier")
        self.add_curve("curva", "purple", [(25, 25), (40, 75), (70, 75), (90, 30), (120, 100), (150, 50), (180, 200), (200, 150), (250, 300)], "bezier")
        self.add_curve("curva BSPLINE", "red", [(-100, -100), (-100, 100), (100, 100), (100, -100)], "bspline")
        self.add_curve("curva", "green", [(25, 25), (40, 75), (70, 75), (90, 30), (120, 100), (150, 50), (180, 200), (200, 150), (250, 300)], "bspline")
        self.add_curve("circle", "purple", [(0, -100), (-100, -100), (-100, 0), (-100, 100), (0, 100), (100, 100), (100, 0), (100, -100), (0, -100), (-100, -100)], "bspline")


    def update_viewport(self):
        self.interface.clear_canvas()

        for obj in self.display_file:
            clip_coords = None
            match obj.type:
                case "point":
                    clip_coords = self.clipper.clip_point(obj.normalized_coordinates)
                case "line":
                    func_opt = self.interface.line_clip_opt_var.get()
                    clip_coords = self.clipper.clip_line(obj.normalized_coordinates, func_opt)
                case "wireframe":
                    func_opt = self.interface.line_clip_opt_var.get()
                    clip_coords = self.clipper.clip_wireframe(obj.normalized_coordinates, func_opt)
                case "polygon":
                    clip_coords = self.clipper.clip_polygon(obj.normalized_coordinates)
                case "curve":
                    clip_coords = self.clipper.clip_curve(obj.normalized_coordinates)

            if (clip_coords is not None):
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
        w_center = self.window.get_center()
        delta_angle = self.get_delta_angle()

        transformation_list = []
        self.transformer.add_translation(transformation_list, -w_center[0], -w_center[1])
        self.transformer.add_rotation(transformation_list, -delta_angle, (0, 0))

        window_coordinates = self.transformer.transform(self.window.coordinates, transformation_list)
        transformed_coords = self.transformer.transform(coordinates, transformation_list)

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
        w_center = self.window.get_center()
        delta_angle = self.get_delta_angle()

        transformation_list = []
        self.transformer.add_translation(transformation_list, -w_center[0], -w_center[1])
        self.transformer.add_rotation(transformation_list, -delta_angle, (0, 0))

        window_coordinates = self.transformer.transform(self.window.coordinates, transformation_list)

        for obj in self.display_file:
            transformed_coords = self.transformer.transform(obj.coordinates, transformation_list)
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
        w_center = self.window.get_center()

        offset_x = coord[0] - w_center[0]
        offset_y = coord[1] - w_center[1]

        self.window.move(self.transformer, offset_x, offset_y)
        self.generate_normal_coordinates();
        self.update_viewport()


    # direction can be: "up", "down", "left", "right"
    def move_window(self, offset: int, direction: str):
        offset_x, offset_y = 0, 0
        match direction:
            case "up":
                offset_x, offset_y = [up_v*offset for up_v in self.up_vector]
            case "down":
                offset_x, offset_y = [-up_v*offset for up_v in self.up_vector]
            case "right":
                offset_x, offset_y = [rg_v*offset for rg_v in self.right_vector]
            case "left":
                offset_x, offset_y = [-rg_v*offset for rg_v in self.right_vector]

        self.window.move(self.transformer, offset_x, offset_y)
        self.generate_normal_coordinates()
        self.update_viewport()


    # inORout can be: "in", "out"
    def zoom_window(self, zoom_factor: float, inORout: str):
        zoom_factor = 1/zoom_factor if (inORout == "in") else zoom_factor
        self.window.zoom(self.transformer, zoom_factor)
        self.generate_normal_coordinates()
        self.update_viewport()


    def rotate_window(self, degrees: int, antiClockwise: bool):
        degrees = degrees if (antiClockwise) else -degrees
        self.window.rotate(self.transformer, degrees)
        self.generate_normal_coordinates(degrees)
        self.update_viewport()


    # direction can be: "up", "down", "left", "right"
    def move_object(self, offset: int, direction: str, obj_id: int):
        obj = self.get_object(obj_id)

        offset_x, offset_y = 0, 0
        match direction:
            case "up":
                offset_x, offset_y = [up_v*offset for up_v in self.up_vector]
            case "down":
                offset_x, offset_y = [-up_v*offset for up_v in self.up_vector]
            case "right":
                offset_x, offset_y = [rg_v*offset for rg_v in self.right_vector]
            case "left":
                offset_x, offset_y = [-rg_v*offset for rg_v in self.right_vector]

        obj.move(self.transformer, offset_x, offset_y)
        obj.normalized_coordinates = self.normalize_object_coordinates(obj.coordinates)
        self.update_viewport()


    # inORout can be: "in", "out"
    def scale_object(self, scale_factor: float, object_id: int, inORout: str):
        scale_factor = 1/scale_factor if (inORout == "out") else scale_factor 
        obj = self.get_object(object_id)
        obj.scale(self.transformer, scale_factor)
        obj.normalized_coordinates = self.normalize_object_coordinates(obj.coordinates)
        self.update_viewport()


    # rotation_opt can be: "Origin", "Obj Center" and "Other"
    def rotate_object(self, antiClockwise: bool, degrees: int, object_id: int, rotation_opt: str, rotation_point: tuple[float, float]=(0, 0)):
        degrees = degrees if (antiClockwise) else -degrees
        obj = self.get_object(object_id)
        rp = obj.get_center() if (rotation_opt == "Obj Center") else (0, 0) if (rotation_opt == "Origin") else rotation_point
        obj.rotate(self.transformer, degrees, rp)
        obj.normalized_coordinates = self.normalize_object_coordinates(obj.coordinates)
        self.update_viewport()


    def apply_transformations(self, obj: Object, transformation_tuple_list: list[tuple[str, float, tuple[float, float]|None, bool|None]]):
        obj.coordinates = self.transformer.apply_transformations(obj.coordinates, transformation_tuple_list, obj.get_center())
        self.generate_normal_coordinates()
        self.update_viewport()


    def get_object(self, id: int) -> Object:
        return self.display_file[id+2]
