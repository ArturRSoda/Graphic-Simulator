import numpy as np

from transformer import Transformer

class Object3D:
    def __init__(self, system,
                       name: str, 
                       color: str,
                       type: str,
                       coordinates: list[tuple[float, float, float]],
                       normalized_coordinates: list[tuple[float, float]]):

        self.system = system
        self.name = name
        self.color = color
        self.type = type
        self.coordinates = coordinates
        self.normalized_coordinates = normalized_coordinates

    def get_center(self):
        coordinates = self.coordinates
        coords = [tuple(t) for t in coordinates]
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


    def move(self, offset_x: float, offset_y: float, offset_z: float):
        transformation_list = []
        self.system.transformer.add_translation(transformation_list, offset_x, offset_y, offset_z)
        self.coordinates = self.system.transformer.transform(self.coordinates, transformation_list)


    def scale(self, factor: float):
        transformation_list = []
        self.system.transformer.add_scaling(transformation_list, factor, self.get_center())
        self.coordinates = self.system.transformer.transform(self.coordinates, transformation_list)


    def rotate(self, degrees: int, axis: str):
        transformation_list = []
        if (axis in ("x", "y", "z")):
            self.system.transformer.add_rotation(transformation_list, degrees, axis)
        else:
            offset_x, offset_y, offset_z = self.get_center()

            self.system.transformer.add_translation(transformation_list, -offset_x, -offset_y, -offset_z)

            self.system.transformer.add_align_matrix(transformation_list, self.system.window.vpn, [0, 1, 0])

            self.system.transformer.add_rotation(transformation_list, degrees, "y")

            self.system.transformer.add_align_matrix(transformation_list, [0, 1, 0], self.system.window.vpn)

            self.system.transformer.add_translation(transformation_list, offset_x, offset_y, offset_z)

        self.coordinates = self.system.transformer.transform(self.coordinates, transformation_list)


class Point3D(Object3D):
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(system, name, color, "point", coordinates, normalized_coordinates)
        self.edges = []


class Line3D(Object3D):
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(system, name, color, "line", coordinates, normalized_coordinates)
        self.edges = [(0, 1)]


class WireFrame3D(Object3D):
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], edges: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(system, name, color, "wireframe", coordinates, normalized_coordinates)
        self.edges = edges


class Polygon3D(Object3D):
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], edges: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(system, name, color, "polygon", coordinates, normalized_coordinates)
        self.edges = edges


class Object:
    def __init__(self, name: str, 
                       color: str,
                       type: str,
                       coordinates: list[tuple[float, float]],
                       normalized_coordinates: list[tuple[float, float]]):

        self.name = name
        self.color = color
        self.type = type
        self.coordinates = coordinates
        self.normalized_coordinates = normalized_coordinates

    def get_center(self):
        coordinates = self.coordinates
        coords = [tuple(t) for t in coordinates]
        if (coords[0] == coords[-1]) and (len(coords) > 1):
            coords.pop()

        average_x, average_y = 0, 0
        for x, y in coords:
            average_x += x
            average_y += y
        points_num = len(coords)
        average_x /= points_num
        average_y /= points_num

        return (average_x, average_y)


    def rotate(self, transformer: Transformer, degrees: int, rotation_point: tuple[float, float]):
        transformation_list = []
        transformer.add_rotation(transformation_list, degrees, rotation_point)
        self.coordinates = transformer.transform(self.coordinates, transformation_list)


    def scale(self, transformer: Transformer, factor: float):
        transformation_list = []
        transformer.add_scaling(transformation_list, factor, self.get_center())
        self.coordinates = transformer.transform(self.coordinates, transformation_list)


    def move(self, transformer: Transformer, offset_x: float, offset_y: float):
        transformation_list = []
        transformer.add_translation(transformation_list, offset_x, offset_y)
        self.coordinates = transformer.transform(self.coordinates, transformation_list)


class Point(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "point", coordinates, normalized_coordinates)


class Line(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "line", coordinates, normalized_coordinates)


class WireFrame(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "wireframe", coordinates, normalized_coordinates)


class Polygon(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "polygon", coordinates, normalized_coordinates)


class BezierCurve(Object):
    def __init__(self, name: str, color: str, control_points: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]], n: int=100):
        super().__init__(name, color, "curve", [], normalized_coordinates)

        self.control_points = control_points
        self.step = n
        self.generate()


    def cubic_bezier(self, p0, p1, p2, p3, t):
        return (1 - t)**3 * np.array(p0) + \
               3 * (1 - t)**2 * t * np.array(p1) + \
               3 * (1 - t) * t**2 * np.array(p2) + \
               t**3 * np.array(p3)


    def generate(self):
        t_values = np.linspace(0, 1, self.step)
        cp_num = len(self.control_points)
        for i in range(0, cp_num - 3, 3):
            p0, p1, p2, p3 = self.control_points[i:i+4]

            # g1 continuity
            if i + 4 < cp_num:
                self.control_points[i+4] = 2 * np.array(p3) - np.array(p2)

            segment = [self.cubic_bezier(p0, p1, p2, p3, t) for t in t_values]
            coords = [(float(x), float(y)) for (x, y) in segment]
            self.coordinates.extend(coords)

        # ensures all the points are used
        if cp_num % 3 != 1:
            p0, p1, p2 = self.control_points[-3:]
            p3 = p2
            segment = [self.cubic_bezier(p0, p1, p2, p3, t) for t in t_values]
            coords = [(float(x), float(y)) for (x, y) in segment]
            self.coordinates.extend(coords)


class BSplineCurve(Object):
    def __init__(self, name: str, color: str, control_points: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "curve", [], normalized_coordinates)

        self.control_points = control_points
        self.delta = 0.01

        self.e_delta = np.array([
            [              0,               0,          0, 1],
            [  self.delta**3,   self.delta**2, self.delta, 0],
            [6*self.delta**3, 2*self.delta**2,          0, 0],
            [6*self.delta**3,               0,          0, 0]
        ])

        self.matriz_bs_base = (1/6) * np.array([
                                          [-1,  3, -3,  1],
                                          [ 3, -6,  3,  0],
                                          [-3,  0,  3,  0],
                                          [ 1,  4,  1,  0]
                                      ])

        self.generate()


    def get_geometry_vector(self, vetor):
        g_x = np.array([x for (x, _) in vetor])
        g_y = np.array([y for (_, y) in vetor])
        return g_x, g_y

    def generate(self):
        n = int(1/self.delta)
        i = 0
        while (i+4 <= len(self.control_points)):
            points = self.control_points[i:i+4]
            i += 1

            g_x, g_y = self.get_geometry_vector(points)
            m_bs = self.matriz_bs_base

            c_x = np.matmul(m_bs, g_x)
            c_y = np.matmul(m_bs, g_y)

            fx, d_fx, d2_fx, d3_fx = np.matmul(self.e_delta, c_x)
            fy, d_fy, d2_fy, d3_fy = np.matmul(self.e_delta, c_y)

            self.fwd_diff(n, fx, d_fx, d2_fx, d3_fx, fy, d_fy, d2_fy, d3_fy)


    def fwd_diff(self, n, x, dx, d2x, d3x, y, dy, d2y, d3y):
        i = 1
        self.coordinates.append((float(x), float(y)))
        while (i < n):
            i += 1
            x, dx, d2x = x+dx, dx+d2x, d2x+d3x
            y, dy, d2y = y+dy, dy+d2y, d2y+d3y
            self.coordinates.append((float(x), float(y)))
