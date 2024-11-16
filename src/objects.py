import numpy as np

from transformer import Transformer

class Object3D:
    def __init__(self, system,
                       name                   : str, 
                       color                  : str,
                       type                   : str,
                       coordinates            : list[tuple[float, float, float]],
                       normalized_coordinates : list[tuple[float, float, float]],
                       edges                  : list[tuple[int, int]]):

        self.system = system
        self.name = name
        self.color = color
        self.type = type
        self.coordinates = coordinates
        self.normalized_coordinates = normalized_coordinates
        self.edges = edges

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
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "point", coordinates, normalized_coordinates, [])


class Line3D(Object3D):
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "line", coordinates, normalized_coordinates, [(0, 1)])


class WireFrame3D(Object3D):
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], edges: list[tuple[int, int]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "wireframe", coordinates, normalized_coordinates, edges)


class BezierCurve3D(Object3D):
    def __init__(self, system, name: str, color: str, control_matrices: list[list[tuple[float, float, float]]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "curve", [], normalized_coordinates, [])

        self.control_matrices = control_matrices

        for i, m in enumerate(self.control_matrices):
            self.generate(i, m)


    def continuity(self, matrices: list[list[tuple[float, float, float]]]):
        for m in matrices: m.sort()
        for i in range(len(matrices)-1):
            matrices[i][-4:] = matrices[i+1][:4]


    def get_GB(self, matrix: list[tuple[float, float, float]]) -> tuple:
        lcp = len(matrix)
        GBx = np.array([[x for (x,_,_) in matrix[i:i+4]] for i in range(0, lcp, 4)])
        GBy = np.array([[y for (_,y,_) in matrix[i:i+4]] for i in range(0, lcp, 4)])
        GBz = np.array([[z for (_,_,z) in matrix[i:i+4]] for i in range(0, lcp, 4)])

        return GBx, GBy, GBz


    def generate(self, mi: int, matrix: list[tuple[float, float, float]], step: int=15):
        Mb = np.array([
            [-1,  3, -3,  1],
            [ 3, -6,  3,  0],
            [-3,  3,  0,  0],
            [ 1,  0,  0,  0]
        ])

        s = np.linspace(0, 1, step)
        t = np.linspace(0, 1, step)

        GBx, GBy, GBz = self.get_GB(matrix)

        for i, ti in enumerate(t):
            tv = np.array([ti**3, ti**2, ti, 1])

            for j, si in enumerate(s):
                sv = np.array([si**3, si**2, si, 1])

                xp = float(sv @ Mb @ GBx @ Mb.T @ tv.T)
                yp = float(sv @ Mb @ GBy @ Mb.T @ tv.T)
                zp = float(sv @ Mb @ GBz @ Mb.T @ tv.T)

                self.coordinates.append((xp, yp, zp))
                if (j < step-1):
                    l = len(self.coordinates)
                    self.edges.append((l-1, l))

            if (i < step-1):
                for t in range(step):
                    l = len(self.coordinates)
                    p1 = mi*step**2 + i*step+t
                    p2 = p1+step
                    self.edges.append((p1, p2))


class BSplineCurve3D(Object3D):
    def __init__(self, system, name: str, color: str, control_points: list[list[tuple[float, float, float]]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "curve", [], normalized_coordinates, [])

        self.control_points = control_points[0]

        self.generate()


    def get_control_point_matrices(self):
        n = int(len(self.control_points) ** (1/2))

        x = self.control_points
        matrices = list()
        for i in range(0, n-3):
            for j in range(0, n-3):
                m = [
                    [x[    i*n + j], x[    i*n + (j+1)], x[    i*n + (j+2)], x[    i*n + (j+3)]],
                    [x[(i+1)*n + j], x[(i+1)*n + (j+1)], x[(i+1)*n + (j+2)], x[(i+1)*n + (j+3)]],
                    [x[(i+2)*n + j], x[(i+2)*n + (j+1)], x[(i+2)*n + (j+2)], x[(i+2)*n + (j+3)]],
                    [x[(i+3)*n + j], x[(i+3)*n + (j+1)], x[(i+3)*n + (j+2)], x[(i+3)*n + (j+3)]],
                ]
                matrices.append(m)

        return matrices


    def get_G(self, matrix: list[list[tuple[float, float, float]]]) -> tuple:
        Gx = np.array([[x for (x, _, _) in l] for l in matrix])
        Gy = np.array([[y for (_, y, _) in l] for l in matrix])
        Gz = np.array([[z for (_, _, z) in l] for l in matrix])
        return Gx, Gy, Gz


    def draw_fwd_diff_curve(self, n,
                           x, Dx, D2x, D3x,
                           y, Dy, D2y, D3y,
                           z, Dz, D2z, D3z):

        old_x, old_y, old_z = x, y, z
        for _ in range(1, n):
            x += Dx;  Dx += D2x;  D2x += D3x;
            y += Dy;  Dy += D2y;  D2y += D3y;
            z += Dz;  Dz += D2z;  D2z += D3z;

            self.coordinates.append((old_x, old_y, old_z))
            self.coordinates.append((x, y, z))

            l = len(self.coordinates)
            self.edges.append((l-2, l-1))

            old_x, old_y, old_z = x, y, z

        return 


    def update_DD(self, DDx, DDy, DDz):
        #row1 <- row1 + row2
        DDx[0][0] += DDx[1][0]; DDx[0][1] += DDx[1][1]; DDx[0][2] += DDx[1][2]; DDx[0][3] += DDx[1][3];
        DDy[0][0] += DDy[1][0]; DDy[0][1] += DDy[1][1]; DDy[0][2] += DDy[1][2]; DDy[0][3] += DDy[1][3];
        DDz[0][0] += DDz[1][0]; DDz[0][1] += DDz[1][1]; DDz[0][2] += DDz[1][2]; DDz[0][3] += DDz[1][3];
        #row2 <- row2 + row3
        DDx[1][0] += DDx[2][0]; DDx[1][1] += DDx[2][1]; DDx[1][2] += DDx[2][2]; DDx[1][3] += DDx[2][3];
        DDy[1][0] += DDy[2][0]; DDy[1][1] += DDy[2][1]; DDy[1][2] += DDy[2][2]; DDy[1][3] += DDy[2][3];
        DDz[1][0] += DDz[2][0]; DDz[1][1] += DDz[2][1]; DDz[1][2] += DDz[2][2]; DDz[1][3] += DDz[2][3];
        #row3 <- row3 + row4 
        DDx[2][0] += DDx[3][0]; DDx[2][1] += DDx[3][1]; DDx[2][2] += DDx[3][2]; DDx[2][3] += DDx[3][3];
        DDy[2][0] += DDy[3][0]; DDy[2][1] += DDy[3][1]; DDy[2][2] += DDy[3][2]; DDy[2][3] += DDy[3][3];
        DDz[2][0] += DDz[3][0]; DDz[2][1] += DDz[3][1]; DDz[2][2] += DDz[3][2]; DDz[2][3] += DDz[3][3];  

        return DDx, DDy, DDz


    def draw_fwd_diff_surface(self, step, Cx, Cy, Cz, Es):
        DDx = Es @ Cx @ Es.T
        DDy = Es @ Cy @ Es.T
        DDz = Es @ Cz @ Es.T

        for _ in range(step):
            self.draw_fwd_diff_curve(step,
                DDx[0][0], DDx[0][1], DDx[0][2], DDx[0][3],
                DDy[0][0], DDy[0][1], DDy[0][2], DDy[0][3],
                DDz[0][0], DDz[0][1], DDz[0][2], DDz[0][3]
            )
            DDx, DDy, DDz = self.update_DD(DDx, DDy, DDz)

        DDx = (Es @ Cx @ Es.T).T
        DDy = (Es @ Cy @ Es.T).T
        DDz = (Es @ Cz @ Es.T).T

        for _ in range(step):
            self.draw_fwd_diff_curve(step,
                DDx[0][0], DDx[0][1], DDx[0][2], DDx[0][3],
                DDy[0][0], DDy[0][1], DDy[0][2], DDy[0][3],
                DDz[0][0], DDz[0][1], DDz[0][2], DDz[0][3]
            )
            DDx, DDy, DDz = self.update_DD(DDx, DDy, DDz)


    def generate(self, step=10):
        M = np.array([
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  0,  3, 0],
            [ 1,  4,  1, 0]
        ]) / 6

        cp_matrices = self.get_control_point_matrices()
        for control_points in cp_matrices:
            Gx, Gy, Gz = self.get_G(control_points)

            Cx = M @ Gx @ M.T
            Cy = M @ Gy @ M.T
            Cz = M @ Gz @ M.T

            ds = 1 / (step - 1)

            Es = np.array([
                [      0,       0,  0, 1],
                [  ds**3,   ds**2, ds, 0],
                [6*ds**3, 2*ds**2,  0, 0],
                [6*ds**3,       0,  0, 0]
            ])

            self.draw_fwd_diff_surface(step, Cx, Cy, Cz, Es)

