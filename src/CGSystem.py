import numpy as np
import math as m

from numpy.linalg import norm

from CGSystemInterface import CGSystemInterface
from newObjWindow import NewObjWindow
from transformationWindow import TransformationWindow
#from objects import BSplineCurve, Object, Point, Line, Polygon, WireFrame, BezierCurve, BSplineCurve
from objects import Object3D, Point3D, Line3D, Polygon3D, WireFrame3D
import transformer
from window import Window
from transformer import Transformer
from clipper import Clipper
import window


class CGSystem():
    def __init__(self):
        self.interface     : CGSystemInterface
        self.window        : Window
        self.transformer : Transformer
        self.clipper       : Clipper

        self.vp_coord_min  : tuple[float, float]
        self.vp_coord_max  : tuple[float, float]

        # add aspect ratio

        self.display_file  : list[Object3D]

    def run(self):
        self.interface = CGSystemInterface(self)
        self.transformer = Transformer(self)
        self.clipper = Clipper()

        self.vp_coord_max = (self.interface.subcanvas_width, self.interface.subcanvas_height)
        self.vp_coord_min = (0, 0)

        self.window = Window(self, [
            (-self.vp_coord_max[0]/2, -self.vp_coord_max[1]/2, -300),
            ( self.vp_coord_max[0]/2, -self.vp_coord_max[1]/2, -300),
            ( self.vp_coord_max[0]/2,  self.vp_coord_max[1]/2, -300),
            (-self.vp_coord_max[0]/2,  self.vp_coord_max[1]/2, -300)
        ])

        self.display_file = list()

        # world center lines
        self.display_file.append(Line3D(self, "X", "black", [(-1000, 0, 0), (1000, 0, 0)], []))
        self.display_file.append(Line3D(self, "Y", "black", [(0, -1000, 0), (0, 1000, 0)], []))
        self.display_file.append(Line3D(self, "Z", "black", [(0, 0, -1000), (0, 0, 1000)], []))

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
        self.display_file.pop(id+3)

        self.update_viewport()


    def add_point(self,name: str, color: str, coord: tuple[float, float, float]):
        point = Point3D(self, name, color, [coord], [])

        self.display_file.append(point)
        self.interface.objects_listbox.insert("end", "%s [%s - Point]" % (name, color))

        self.generate_normal_coordinates()
        self.update_viewport()


    def add_line(self, name: str, color: str, start_coord: tuple[float, float, float], end_coord: tuple[float, float, float]):
        line = Line3D(self, name, color, [start_coord, end_coord], [])

        self.display_file.append(line)
        self.interface.objects_listbox.insert("end", "%s [%s - Line]" % (name, color))

        self.generate_normal_coordinates()
        self.update_viewport()


    def add_wireframe(self, name: str, color: str, coord_list: list[tuple[float, float, float]], edges: list[tuple[float, float]]):
        if (len(coord_list) == 1):
            self.add_point(name, color, coord_list[0])
            return

        wf = WireFrame3D(self, name, color, coord_list, edges, [])

        self.display_file.append(wf)
        self.interface.objects_listbox.insert("end", "%s [%s - Wireframe]" % (name, color))

        self.generate_normal_coordinates()
        self.update_viewport()


    def add_polygon(self, name: str, color: str, coord_list: list[tuple[float, float, float]], edges: list[tuple[float, float]]):
        if (len(coord_list) == 1):
            self.add_point(name, color, coord_list[0])
            return

        norm_coord = self.normalize_object_coordinates(coord_list)
        plg = Polygon3D(self, name, color, coord_list, edges, norm_coord)

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
        self.add_wireframe("cube", "green", [(100, 100, 100), (100, 100, -100), (100, 100, 100), (-100, 100, 100), (-100, 100, -100), (-100, 100, 100), (-100, -100, 100), (-100, -100, -100), (-100, -100, 100), (100, -100, 100), (100, -100, -100), (100, -100, 100), (100, 100, 100), (100, 100, -100), (-100, 100, -100), (-100, -100, -100), (100, -100, -100), (100, 100, -100)], [(0, 1), (0, 2), (0, 4), (3, 1), (3, 7), (3, 2), (6, 4), (6, 7), (6, 2), (5, 4), (5, 1), (5, 7)])
        self.add_wireframe("w", "red", [(100, 100, -100), (-100, 100, -100), (-100, -100, -100), (100, -100, -100)], [])
        self.add_line("l", "red", (0, 0, 0), (0, 0, 1))
        self.add_wireframe("vpn", "red", [(0, 0, 0), (0, 0, 50)], [])
        self.add_point("p", "red", (100, 100, 100))
        self.add_point("x", "blue", (100, 0, 0))
        self.add_point("y", "purple", (0, 100, 0))
        self.add_point("z", "pink", (0, 0, 100))

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


    def normalize_coordinates(self, coordinates: list[tuple[float, float, float]], window_coordinates: list[tuple[float, float, float]]):
        p0, p1, p2, p3 = window_coordinates
        normalized_coords = list()
        width = m.dist(p0, p1)
        height = m.dist(p1, p2)
        for coord in coordinates:
            x, y, z = coord

            normalized_x = 2 * (x - p0[0]) / width - 1
            normalized_y = 2 * (y - p0[1]) / height - 1

            normalized_coords.append((normalized_x, normalized_y))
        return normalized_coords


    def normalize_object_coordinates(self, coordinates: list[tuple[float, float, float]]):
        w_center = self.window.get_center()
        delta_angle = self.get_delta_angle()

        transformation_list = []
        self.transformer.add_translation(transformation_list, -w_center[0], -w_center[1], -w_center[0])
        self.transformer.add_rotation(transformation_list, -delta_angle, "z", (0, 0, 0))

        window_coordinates = self.transformer.transform(self.window.coordinates, transformation_list)
        transformed_coords = self.transformer.transform(coordinates, transformation_list)

        normalized_coordinates = self.normalize_coordinates(transformed_coords, window_coordinates)

        return normalized_coordinates


    def normalize_vector(self, vector: tuple[float, float, float]) -> tuple[float, float, float]:
        vector = np.array(vector)
        magnitude = np.linalg.norm(vector)
        normalized_vector = vector / magnitude
        return tuple([float(x) for x in normalized_vector])

    def generate_normal_coordinates(self):
        transformation_list = []
        align_vup_m = []

        # translate world to center
        w_center = self.window.get_center()
        self.transformer.add_translation(transformation_list, -w_center[0], -w_center[1], -w_center[2])

        # align world with z axis
        self.transformer.add_align_matrix(transformation_list, self.window.vpn, [0, 0, 1])
        self.transformer.add_align_matrix(align_vup_m, self.window.vpn, [0, 0, 1])

        # aligns the window and the up vector with the y-axis, move the objects
        # and calculates the normalized coordinates
        v_up = self.transformer.transform([self.window.up_vector], align_vup_m)[0]
        self.transformer.add_align_matrix(transformation_list, v_up, [0, 1, 0])

        window_coordinates = self.transformer.transform(self.window.coordinates, transformation_list)

        for obj in self.display_file:
            transformed_coords = self.transformer.transform(obj.coordinates, transformation_list)
            obj.normalized_coordinates = self.normalize_coordinates(transformed_coords, window_coordinates)


    def get_angles_to_align(self, v1, v2):
        vector1 = np.array(v1)
        vector2 = np.array(v2)
        vector1 = vector1 / np.linalg.norm(vector1)
        vector2 = vector2 / np.linalg.norm(vector2)
        a, b, c = vector1
        x, y, z = vector2
        x_angle = np.arccos(z / np.sqrt(b ** 2 + c ** 2)) - np.arctan2(-b, c)
        x_after_x_rotation = a
        y_after_x_rotation = b * np.cos(x_angle) - c * np.sin(x_angle)

        det = np.sqrt(x_after_x_rotation ** 2 + y_after_x_rotation ** 2)
        sin = x_after_x_rotation * y - y_after_x_rotation * x
        cos = y_after_x_rotation * y + x_after_x_rotation * x
        sin /= det if (det) else 1
        cos /= det if (det) else 1
        z_angle = np.arctan2(sin, cos)

        return float(np.rad2deg(x_angle)), float(np.rad2deg(z_angle))


    # get angle between y-axis and up vector 
    def get_delta_angle(self, v1):
        x, y, z = v1
        up_vector = np.array([x, y])
        norm_up = np.linalg.norm(up_vector)

        y_axis = np.array([0, 1])
        norm_y = np.linalg.norm(y_axis)

        dot_product = np.dot(up_vector, y_axis)
        delta_angle = m.degrees(m.acos(dot_product / (norm_up * norm_y)))
        delta_angle = -delta_angle if (x > 0) else delta_angle # dark magic

        return delta_angle

    def set_window_coord(self, coord: tuple[float, float, float]):
        w_center = self.window.get_center()

        offset_x = coord[0] - w_center[0]
        offset_y = coord[1] - w_center[1]
        offset_z = coord[2] - w_center[2]

        self.window.move(self.transformer, offset_x, offset_y, offset_z)
        self.generate_normal_coordinates();
        self.update_viewport()


    # direction can be: "up", "down", "left", "right", "in", "out"
    def move_window(self, offset: int, direction: str):
        offset_x, offset_y, offset_z = 0, 0, 0
        match direction:
            case "up":
                offset_x, offset_y, offset_z = [up_v*offset for up_v in self.window.up_vector]
            case "down":
                offset_x, offset_y, offset_z = [-up_v*offset for up_v in self.window.up_vector]
            case "right":
                offset_x, offset_y, offset_z = [rg_v*offset for rg_v in self.window.right_vector]
            case "left":
                offset_x, offset_y, offset_z = [-rg_v*offset for rg_v in self.window.right_vector]
            case "in":
                offset_x, offset_y, offset_z = [vpn*offset for vpn in self.window.vpn]
            case "out":
                offset_x, offset_y, offset_z = [-vpn*offset for vpn in self.window.vpn]

        self.window.move(self.transformer, offset_x, offset_y, offset_z)
        self.generate_normal_coordinates()
        self.update_viewport()


    # inORout can be: "in", "out"
    def zoom_window(self, zoom_factor: float, inORout: str):
        zoom_factor = 1/zoom_factor if (inORout == "in") else zoom_factor
        self.window.zoom(self.transformer, zoom_factor)
        self.generate_normal_coordinates()
        self.update_viewport()


    def rotate_window(self, degrees: int, antiClockwise: bool, axis: str):
        if (antiClockwise): degrees = -degrees
        self.window.rotate(self.transformer, degrees, axis)
        self.generate_normal_coordinates()
        self.update_viewport()


    # direction can be: "up", "down", "left", "right", "in", "out"
    def move_object(self, offset: int, direction: str, obj_id: int):
        obj = self.get_object(obj_id)

        offset_x, offset_y, offset_z = 0, 0, 0
        match direction:
            case "up":
                offset_x, offset_y, offset_z = [up_v*offset for up_v in self.window.up_vector]
            case "down":
                offset_x, offset_y, offset_z = [-up_v*offset for up_v in self.window.up_vector]
            case "right":
                offset_x, offset_y, offset_z = [rg_v*offset for rg_v in self.window.right_vector]
            case "left":
                offset_x, offset_y, offset_z = [-rg_v*offset for rg_v in self.window.right_vector]
            case "in":
                offset_x, offset_y, offset_z = [vpn*offset for vpn in self.window.vpn]
            case "out":
                offset_x, offset_y, offset_z = [-vpn*offset for vpn in self.window.vpn]

        obj.move(self.transformer, offset_x, offset_y, offset_z)
        #obj.normalized_coordinates = self.normalize_object_coordinates(obj.coordinates)
        self.generate_normal_coordinates()
        self.update_viewport()


    # inORout can be: "in", "out"
    def scale_object(self, scale_factor: float, object_id: int, inORout: str):
        scale_factor = 1/scale_factor if (inORout == "out") else scale_factor 
        obj = self.get_object(object_id)
        obj.scale(self.transformer, scale_factor)
        #obj.normalized_coordinates = self.normalize_object_coordinates(obj.coordinates)
        self.generate_normal_coordinates()
        self.update_viewport()


    # rotation_opt can be: "Origin", "Obj Center" and "Other"
    def rotate_object(self, antiClockwise: bool, degrees: int, object_id: int, axis: str):
        if (antiClockwise): degrees = -degrees
        obj = self.get_object(object_id)
        obj.rotate(self.transformer, degrees, axis)
        #obj.normalized_coordinates = self.normalize_object_coordinates(obj.coordinates)
        self.generate_normal_coordinates()
        self.update_viewport()


    def apply_transformations(self, obj: Object3D, transformation_tuple_list: list[tuple[str, float, tuple[float, float]|None, bool|None]]):
        obj.coordinates = self.transformer.apply_transformations(obj.coordinates, transformation_tuple_list, obj.get_center())
        self.generate_normal_coordinates()
        self.update_viewport()


    def get_object(self, id: int) -> Object3D:
        return self.display_file[id+3]
