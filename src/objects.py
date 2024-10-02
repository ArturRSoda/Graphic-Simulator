import numpy as np

from transformer import Transformer

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
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]], n: int=100):
        super().__init__(name, color, "bezier", coordinates, normalized_coordinates)

        self.control_points = []
        self.curve_points = np.empty((0, 2), dtype=np.float64)
        self.d = 0
        self.t = 0
        self.step = np.float64(1.0/n)
        self.run = False

        for coordinate in coordinates:
            x, y = coordinate
            self.add_point(x, y)

        self.generate()
        self.coordinates = self.curve_points

    def add_point(self, x, y):
        if self.d == 0:
            self.control_points.append([[x, y]])
        else:
            self.control_points[0].append([x, y])
            self.control_points.append([])
        self.d += 1

    def bezier(self):
        for d in range(1, self.d):
            self.control_points[d] = []
            for i in range(self.d - d):
                self.control_points[d].append([
                    self.control_points[d - 1][i][0] + self.t * (self.control_points[d - 1][i + 1][0] - self.control_points[d - 1][i][0]),
                    self.control_points[d - 1][i][1] + self.t * (self.control_points[d - 1][i + 1][1] - self.control_points[d - 1][i][1])
                ])
        xy = np.array(self.control_points[-1])
        self.curve_points = np.append(self.curve_points, xy, axis=0)

    def generate(self, t=None):
        if t:
            if type(t) is not list:
                t = [t]
            for x in t:
                self.t = x
                self.bezier()
        else:
            while True:
                self.bezier()
                if self.t == 1:
                    break
                self.t = min(self.t + self.step, 1)
        self.run = True

    def curve(self, t=None):
        if not self.run:
            self.generate(t)
        return self.curve_points

    def points(self):
        return np.array(self.control_points[0])
