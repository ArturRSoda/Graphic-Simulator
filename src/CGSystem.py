import numpy as np
import math as m

from numpy.linalg import norm

from CGSystemInterface import CGSystemInterface
from newObjWindow import NewObjWindow
from transformationWindow import TransformationWindow
#from objects import BSplineCurve, Object, Point, Line, Polygon, WireFrame, BezierCurve, BSplineCurve
from objects import Object3D, Point3D, Line3D, Polygon3D, WireFrame3D
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
        #self.add_line("line3d", "red", (0, 0, 0), (100, 100, 100))
        #self.add_line("linez", "purple", (0, 0, 0), (0, 0, 100))
        #self.add_wireframe("L", "red", [(-70, 70), (-70, 30), (-45, 30)])
        #self.add_wireframe("wireframe triangle", "green", [(-70, -70), (-30, -70), (-30, -40), (-70, -70)])
        #self.add_polygon("triangle", "green", [(10, 10), (100, 10), (100, 100)])
        #self.add_point("point", "blue", (10, 10))
        #self.add_polygon("concave hexagon", "red", [(100, 100), (150, 100), (200, 130), (160, 170), (200, 200), (100, 200)])
        #self.add_wireframe("concave wireframe hexagon", "red", [(-100, -100), (-150, -100), (-200, -130), (-160, -170), (-200, -200), (-100, -200), (-100, -100)])
        #self.add_curve("curva", "pink", [(25, 25), (40, 75), (70, 75), (90, 30), (120, 100)], "bezier")
        #self.add_curve("curva", "black", [(25, 25), (40, 75), (70, 75)], "bezier")
        #self.add_curve("curva", "purple", [(25, 25), (40, 75), (70, 75), (90, 30), (120, 100), (150, 50), (180, 200), (200, 150), (250, 300)], "bezier")
        #self.add_curve("curva BSPLINE", "red", [(-100, -100), (-100, 100), (100, 100), (100, -100)], "bspline")
        #self.add_curve("curva", "green", [(25, 25), (40, 75), (70, 75), (90, 30), (120, 100), (150, 50), (180, 200), (200, 150), (250, 300)], "bspline")
        #self.add_curve("circle", "purple", [(0, -100), (-100, -100), (-100, 0), (-100, 100), (0, 100), (100, 100), (100, 0), (100, -100), (0, -100), (-100, -100)], "bspline")


    def angle_between_vectors(self, u: tuple[float, float, float], v: tuple[float, float, float]) -> float:
        u = np.array(u)
        v = np.array(v)
        cos_theta = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
        angle_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))
        angle_deg = np.degrees(angle_rad)
        return angle_deg

    def get_rotation_matrix(self, i_v, unit=None):
        if unit is None:
            unit = [0.0, 0.0, 1.0]

        v1 = np.array(i_v)
        v2 = np.array(unit)

        # unit vectors
        u = v1 / np.linalg.norm(v1)
        Ru = v2 / np.linalg.norm(v2)
        # dimension of the space and identity
        dim = u.size
        I = np.identity(dim)
        # the cos angle between the vectors
        c = np.dot(u, Ru)
        # a small number
        eps = 1.0e-10
        if np.abs(c - 1.0) < eps:
            # same direction
            result = I
        elif np.abs(c + 1.0) < eps:
            # opposite direction
            result = -I
        else:
            # the cross product matrix of a vector to rotate around
            K = np.outer(Ru, u) - np.outer(u, Ru)
            # Rodrigues' formula
            result = I + K + (K @ K) / (1 + c)

        mr = [[float(a), float(b), float(c), 0] for (a, b, c) in result]
        mr.append([0, 0, 0, 1])
        return mr


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


    def get_align_vector_matrix(self, v1, v2):
        # Define the vector to be aligned
        v1 = np.array(v1)
        # Define the z-axis
        v2 = np.array(v2)
        # Determine the angle between the vector and the z-axis
        theta = np.acos(np.dot(v1, v2)/(np.linalg.norm(v1) * np.linalg.norm(v2)));
        # Determine the axis of rotation
        axis = np.cross(v1, v2)/np.linalg.norm(np.cross(v1, v2));
        # Construct the rotation matrix using Rodrigues' formula
        K = np.array([
            [0, -axis[2] ,axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])

        R = np.eye(3) + np.sin(theta)*K + (1-np.cos(theta))*K@K;
        # Apply the rotation matrix to the vector
        #v_aligned = R@v1

        m = list()
        for (a, b, c) in R:
            m.append([float(a), float(b), float(c), 0])
        m.append([0, 0, 0, 1])

        return m


    def generate_normal_coordinates(self):
        transformation_list = []

        # translate world to center
        w_center = self.window.get_center()
        self.transformer.add_translation(transformation_list, -w_center[0], -w_center[1], -w_center[2])

        # align world with z axis
        x_angle, y_angle = self.get_angles_to_align((self.window.vpn[0], self.window.vpn[2], self.window.vpn[1]), [0, 1, 0])
        x_angle, y_angle = self.get_angles_to_align_xy_axis(self.window.vpn, [0, 0, 1])
        print(x_angle, y_angle)

        m = []
        self.transformer.add_rotation(m, x_angle, "x")
        self.transformer.add_rotation(m, y_angle, "y")
        self.transformer.add_rotation(transformation_list, x_angle, "x")
        self.transformer.add_rotation(transformation_list, y_angle, "y")

        # aligns the window and the up vector with the y-axis, move the objects
        # and calculates the normalized coordinates
        v_up = self.transformer.transform([self.window.up_vector], m)[0]
        print("up_vec", self.window.up_vector)
        print("v_up", v_up)

        vpn = self.transformer.transform([self.window.vpn], m)[0]
        print("w_vpn", self.window.vpn)
        print("vpn", vpn)

        x_angle, z_angle = self.get_angles_to_align(v_up, [0, 1, 0])
        print(x_angle, z_angle)
        self.transformer.add_rotation(transformation_list, x_angle, "x")
        self.transformer.add_rotation(transformation_list, z_angle, "z")

        window_coordinates = self.transformer.transform(self.window.coordinates, transformation_list)

        for obj in self.display_file:
            transformed_coords = self.transformer.transform(obj.coordinates, transformation_list)
            obj.normalized_coordinates = self.normalize_coordinates(transformed_coords, window_coordinates)

    def get_angles_to_align_xy_axis(self, v1, v2):
        vector1 = np.array(v1)
        vector2 = np.array(v2)
        vector2 = vector2 / np.linalg.norm(vector2)

        a, b, c = vector1
        x, y, z = vector2

        # Calculate the angle to rotate around the x-axis
        x_angle = np.arccos(z / np.sqrt(b ** 2 + c ** 2)) - np.arctan2(-b, c)

        # Rotate around the x-axis
        x_after_x_rotation = a
        y_after_x_rotation = b * np.cos(x_angle) - c * np.sin(x_angle)
        z_after_x_rotation = b * np.sin(x_angle) + c * np.cos(x_angle)

        # Now, calculate the angle to rotate around the y-axis using the new components
        y_angle = np.arccos(x / np.sqrt(x_after_x_rotation ** 2 + z_after_x_rotation ** 2)) - np.arctan2(z_after_x_rotation, x_after_x_rotation)

        # Rotate around the y-axis
        x_final = x_after_x_rotation * np.cos(y_angle) + z_after_x_rotation * np.sin(y_angle)
        z_final = -x_after_x_rotation * np.sin(y_angle) + z_after_x_rotation * np.cos(y_angle)
        y_final = y_after_x_rotation  # No change in the y-component when rotating around y-axis

        return np.rad2deg(x_angle), np.rad2deg(y_angle) 

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

        return np.rad2deg(x_angle), np.rad2deg(z_angle)

    def get_delta_angle(self, v1):
        x, y, z = self.normalize_vector(v1)
        up_vector = np.array([x, y])
        norm_up = np.linalg.norm(up_vector)

        y_axis = np.array([0, 1])
        norm_y = np.linalg.norm(y_axis)

        dot_product = np.dot(up_vector, y_axis)
        delta_angle = m.degrees(m.acos(dot_product / (norm_up * norm_y)))
        delta_angle = -delta_angle if (x > 0) else delta_angle

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
