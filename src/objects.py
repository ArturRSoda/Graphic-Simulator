from abc import ABC

class Object(ABC):
    def __init__(self, name: str, color: str, type: str, coordinates: list[tuple[float, float]]):
        self.name = name
        self.color = color
        self.type = type
        self.coordinates = coordinates

class Point(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "point", coordinates)


class Line(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "line", coordinates)


class WireFrame(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "wireframe", coordinates)


