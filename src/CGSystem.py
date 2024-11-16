import math as m

from CGSystemInterface import CGSystemInterface
from newObjWindow import NewObjWindow
from transformationWindow import TransformationWindow
from objects import Object3D, Point3D, Line3D, WireFrame3D, BezierCurve3D, BSplineCurve3D
from window import Window
from transformer import Transformer
from clipper import Clipper
from objConverter import ObjConverter


class CGSystem():
    def __init__(self):
        self.interface     : CGSystemInterface
        self.window        : Window
        self.transformer   : Transformer
        self.clipper       : Clipper
        self.vp_coord_min  : tuple[float, float]
        self.vp_coord_max  : tuple[float, float]
        self.display_file  : list[Object3D]
        self.obj_converter : ObjConverter

    def run(self):
        self.interface = CGSystemInterface(self)
        self.transformer = Transformer(self)
        self.clipper = Clipper()
        self.obj_converter = ObjConverter(self)
        self.display_file = list()

        self.vp_coord_max = (self.interface.subcanvas_width, self.interface.subcanvas_height)
        self.vp_coord_min = (0, 0)

        self.window = Window(self, [
            (-self.vp_coord_max[0]/2, -self.vp_coord_max[1]/2, -300),
            ( self.vp_coord_max[0]/2, -self.vp_coord_max[1]/2, -300),
            ( self.vp_coord_max[0]/2,  self.vp_coord_max[1]/2, -300),
            (-self.vp_coord_max[0]/2,  self.vp_coord_max[1]/2, -300)
        ])

        # world center lines
        x = Line3D(self, "X", "black", [(0, 0, 0), (10000, 0, 0)], [])
        y = Line3D(self, "Y", "black", [(0, 0, 0), (0, 10000, 0)], [])
        z = Line3D(self, "Z", "black", [(0, 0, 0), (0, 0, 10000)], [])
        self.normalize_object_coordinates(x)
        self.normalize_object_coordinates(y)
        self.normalize_object_coordinates(z)
        self.display_file.extend((x, y, z))

        # test objects
        self.rotate_window(45, False, "x")
        self.rotate_window(10, True, "y")
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

        self.normalize_object_coordinates(point)
        self.update_viewport()


    def add_line(self, name: str, color: str, start_coord: tuple[float, float, float], end_coord: tuple[float, float, float]):
        line = Line3D(self, name, color, [start_coord, end_coord], [])

        self.display_file.append(line)
        self.interface.objects_listbox.insert("end", "%s [%s - Line]" % (name, color))

        self.normalize_object_coordinates(line)
        self.update_viewport()


    def add_wireframe(self, name: str, color: str, coord_list: list[tuple[float, float, float]], edges: list[tuple[float, float]]):
        if (len(coord_list) == 1):
            self.add_point(name, color, coord_list[0])
            return

        wf = WireFrame3D(self, name, color, coord_list, edges, [])

        self.display_file.append(wf)
        self.interface.objects_listbox.insert("end", "%s [%s - Wireframe]" % (name, color))

        self.normalize_object_coordinates(wf)
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
    def add_surface(self, name: str, color: str, coord_matrices: list[list[tuple[float, float, float]]], type: str):
        curve_class = BezierCurve3D if (type == "bezier") else BSplineCurve3D

        plg = curve_class(self, name, color, coord_matrices, [])

        self.display_file.append(plg)
        self.interface.objects_listbox.insert("end", "%s [%s - Curve]" % (name, color))

        self.normalize_object_coordinates(plg)
        self.update_viewport()


    def add_test(self):
        self.add_wireframe("cube", "green", [(100, 100, 100), (-100, 100, 100), (-100, -100, 100), (100, -100, 100), (100, 100, -100), (-100, 100, -100), (-100, -100, -100), (100, -100, -100)], [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 5), (2, 6), (3, 7), (4, 5), (5, 6), (6, 7), (7, 4)])
        self.add_surface("curve", "blue", [
            [
                    (0, 0, 0),   (0, 100, 100),     (0, 0, 200),   (0, 100, 300),
                (100, 100, 0), (100, 200, 100), (100, 100, 200), (100, 200, 300),
                  (200, 0, 0), (200, 100, 100),   (200, 0, 200), (200, 100, 300),
                (300, 100, 0), (300, 200, 100), (300, 100, 200),   (300, 0, 300)
            ],
            [
                (300, 100, 0), (300, 200, 100), (300, 100, 200),   (300, 0, 300),
                (400, 100, 0), (400, 200, 100), (400, 100, 200), (400, 200, 300),
                  (500, 0, 0), (500, 100, 100),   (500, 0, 200), (500, 100, 300),
                (600, 100, 0), (600, 200, 100), (600, 100, 200),   (600, 0, 300)
            ]
        ], "bezier")

        self.add_surface("spline", "pink", [
            [
                (  0,    0, 0), (  0, 100, 100), (  0, 200, 200), (  0, 100, 300), (  0,    0, 400), (  0, -100, 500),
                (100,  100, 0), (100, 200, 100), (100, 300, 200), (100, 200, 300), (100,  100, 400), (100,    0, 500),
                (200,  200, 0), (200, 300, 100), (200, 400, 200), (200, 300, 300), (200,  200, 400), (200,  100, 500),
                (300,  100, 0), (300, 200, 100), (300, 300, 200), (300, 200, 300), (300,  100, 400), (300,    0, 500),
                (400,    0, 0), (400, 100, 100), (400, 200, 200), (400, 100, 300), (400,    0, 400), (400, -100, 500),
                (500, -100, 0), (500,   0, 100), (500, 100, 200), (500,   0, 300), (500, -100, 400), (500, -200, 500)
            ]
        ], "bspline")


    def import_obj(self, path):
        path_ = ""
        for c in path:
            if c == '.':
                break
            path_ += c

        self.obj_converter.import_obj(path_)
        self.generate_normal_coordinates()
        self.update_viewport()


    def update_viewport(self):
        self.interface.clear_canvas()

        for obj in self.display_file[:3]:
            obj.normalized_coordinates = [(x, y, 0) for (x, y, _) in obj.normalized_coordinates]

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
                    clip_coords = self.clipper.clip_wireframe(obj.normalized_coordinates, obj.edges, func_opt)
                case "curve":
                    func_opt = self.interface.line_clip_opt_var.get()
                    clip_coords = self.clipper.clip_curve(obj.normalized_coordinates, obj.edges, func_opt)

            if (clip_coords is not None):
                obj_vp_coords = self.normalized_coords_to_vp_coords(clip_coords)
                self.interface.draw_object(obj, obj_vp_coords)


    def normalized_coords_to_vp_coords(self, norm_coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
        vp_coords: list[tuple[float, float]] = list()

        x_vp_max, y_vp_max = self.vp_coord_max

        for norm_coord in norm_coords:
            norm_coord = (((norm_coord[0] + 1) / 2), ((norm_coord[1] +1) / 2))
            x = (norm_coord[0] * x_vp_max) + self.interface.subcanvas_shift
            y = (y_vp_max - (norm_coord[1] * y_vp_max)) + self.interface.subcanvas_shift
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

            normalized_coords.append((normalized_x, normalized_y, z))
        return normalized_coords


    def get_aligner_transformation_list(self):
        transformation_list = []
        align_vup_m = []

        # translate de cop to the world center
        cop = self.window.cop
        self.transformer.add_translation(transformation_list, -cop[0], -cop[1], -cop[2])

        # align vpn with z-axis
        self.transformer.add_align_matrix(transformation_list, self.window.vpn, [0, 0, 1])
        self.transformer.add_align_matrix(align_vup_m, self.window.vpn, [0, 0, 1])

        # align vup with y-axis
        v_up = self.transformer.transform([self.window.up_vector], align_vup_m)[0]
        self.transformer.add_align_matrix(transformation_list, v_up, [0, 1, 0])

        return transformation_list


    def normalize_object_coordinates(self, obj: Object3D):
        transformation_list = self.get_aligner_transformation_list()
        window_coordinates = self.transformer.transform(self.window.coordinates, transformation_list)
        transformed_coords = self.transformer.transform(obj.coordinates, transformation_list)
        projection_coords = self.get_projection_coords(transformed_coords, self.window.cop_dist)
        obj.normalized_coordinates = self.normalize_coordinates(projection_coords, window_coordinates)


    def generate_normal_coordinates(self):
        transformation_list = self.get_aligner_transformation_list()
        window_coordinates = self.transformer.transform(self.window.coordinates, transformation_list)
        for obj in self.display_file:
            transformed_coords = self.transformer.transform(obj.coordinates, transformation_list)
            projection_coords = self.get_projection_coords(transformed_coords, self.window.cop_dist)
            obj.normalized_coordinates = self.normalize_coordinates(projection_coords, window_coordinates)


    def get_projection_coords(self, coordinates: list[tuple[float, float, float]], d: float) -> list[tuple[float, float, float]]:
        projection_coords = [(d*x/z, d*y/z, z) for (x, y, z) in coordinates]
        return projection_coords


    def get_center(self, coords: list[tuple[float, float, float]]) -> tuple[float, float, float]:
        if (coords[0] == coords[-1]) and (len(coords) > 1):
            coords.pop()

        average_x, average_y, average_z = 0, 0, 0
        for x, y, z in coords:
            average_x += x
            average_y += y
            average_z += z
        points_num = len(coords)
        average_x /= points_num
        average_y /= points_num
        average_z /= points_num

        return (average_x, average_y, average_z)


    def set_window_coord(self, coord: tuple[float, float, float]):
        w_center = self.window.get_center()

        offset_x = coord[0] - w_center[0]
        offset_y = coord[1] - w_center[1]
        offset_z = coord[2] - w_center[2]

        self.window.move(offset_x, offset_y, offset_z)
        self.generate_normal_coordinates();
        self.update_viewport()


    def set_obj_coord(self, obj_id: int, coord: tuple[float, float, float]):
        obj = self.get_object(obj_id)
        obj_center = obj.get_center()

        offset_x = coord[0] - obj_center[0]
        offset_y = coord[1] - obj_center[1]
        offset_z = coord[2] - obj_center[2]

        obj.move(offset_x, offset_y, offset_z)
        self.normalize_object_coordinates(obj)
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

        self.window.move(offset_x, offset_y, offset_z)
        self.generate_normal_coordinates()
        self.update_viewport()


    # inORout can be: "in", "out"
    def zoom_window(self, zoom_factor: float, inORout: str):
        zoom_factor = 1/zoom_factor if (inORout == "in") else zoom_factor
        self.window.zoom(zoom_factor)
        self.generate_normal_coordinates()
        self.update_viewport()


    def rotate_window(self, degrees: int, antiClockwise: bool, axis: str):
        if (antiClockwise): degrees = -degrees
        self.window.rotate(degrees, axis)
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

        obj.move(offset_x, offset_y, offset_z)
        self.normalize_object_coordinates(obj)
        self.update_viewport()


    # inORout can be: "in", "out"
    def scale_object(self, scale_factor: float, object_id: int, inORout: str):
        scale_factor = 1/scale_factor if (inORout == "out") else scale_factor 
        obj = self.get_object(object_id)
        obj.scale(scale_factor)
        self.normalize_object_coordinates(obj)
        self.update_viewport()


    # rotation_opt can be: "Origin", "Obj Center" and "Other"
    def rotate_object(self, antiClockwise: bool, degrees: int, object_id: int, axis: str):
        if (antiClockwise): degrees = -degrees
        obj = self.get_object(object_id)
        obj.rotate(degrees, axis)
        self.normalize_object_coordinates(obj)
        self.update_viewport()


    def apply_transformations(self, obj: Object3D, transformation_tuple_list: list[tuple[str, float, str | None, bool | None]]):
        obj.coordinates = self.transformer.apply_transformations(obj.coordinates, transformation_tuple_list, obj.get_center())
        self.generate_normal_coordinates()
        self.update_viewport()


    def get_object(self, id: int) -> Object3D:
        return self.display_file[id+3]
