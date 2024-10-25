import math as m

class Clipper:
    def __init__(self):
        self.w_max = 1
        self.w_min = -1
        self.left = 1
        self.right = 2
        self.top = 4
        self.bottom = 8


    def clip_point(self, coords: list[tuple[float, float, float]]) -> list[tuple[float, float]]|None:
        x, y, z = coords[0]
        return None if ((x < -1) or (x > 1) or (y < -1) or (y > 1) or (z < 0)) else [(x, y)]


    def clip_line(self, coords: list[tuple[float, float, float]], func_opt: str) -> list[tuple[float, float]]|None:
        (x_s, y_s, z_s), (x_e, y_e, z_e) = coords
        func = self.cohen_sutherland if (func_opt == "cohen_sutherland") else self.liang_barsky
        return None if ((z_s < 0) or (z_e < 0)) else func([(x_s, y_s), (x_e, y_e)])


    def clip_wireframe(self, coords: list[tuple[float, float, float]], edges: list[tuple[int, int]], func_opt: str) -> list[tuple[float, float]]|None:
        wf_clip_coords = list()
        clip_func = self.cohen_sutherland if (func_opt == "cohen_sutherland") else self.liang_barsky

        for (id1, id2) in edges:
            (x1, y1, z1), (x2, y2, z2) = coords[id1], coords[id2]
            if (z1 < 0) or (z2 < 0):
                continue

            clip_coords = clip_func([(x1, y1), (x2, y2)])
            if (clip_coords is not None):
                wf_clip_coords.append(clip_coords[0])
                wf_clip_coords.append(clip_coords[1])

        return wf_clip_coords if (wf_clip_coords) else None


    def clip_polygon(self, coords: list[tuple[float, float]]) -> list[tuple[float, float]]|None:
        return self.sutherland_hodgman_clip(coords)


    def clip_curve(self, coords: list[tuple[float, float]]) -> list[tuple[float, float]]|None:
        return self.clip_wireframe(coords, "")


    def get_region_code(self, coord: tuple[float, float]) -> int:
        self.left, self.right, self.bottom, self.top = 1, 2, 4, 8

        code = 0
        x = coord[0]
        y = coord[1]

        if (y > 1):
            code |= self.top
        elif (y < -1):
            code |= self.bottom

        if (x < -1):
            code |= self.left
        elif (x > 1):
            code |= self.right

        return code


    def cohen_sutherland(self, line: list[tuple[float, float]]) -> list[tuple[float, float]]|None:
        self.left, self.right, self.bottom, self.top = 1, 2, 4, 8

        x1, y1 = line[0]
        x2, y2 = line[1]

        code1 = self.get_region_code((x1, y1))
        code2 = self.get_region_code((x2, y2))

        flag = False
        while True:
            # Line is completely inside the window, so accept
            if (not code1) and (not code2): 
                flag = True
                break

            # Line is parallel and outside the window, so reject
            elif (code1 & code2): 
                break

            else:
                x, y = 1, 1

                # At least one of the point is outside the window, choose one
                code_out = code1 if (code1 != 0) else code2

                # Find and calculate intersection point
                m = (y2 - y1) / (x2 - x1) if (x2 - x1) else 1
                if (code_out & self.top):
                    x = x1 + (1/m) * (self.w_max - y1) if (m) else x1
                    y = self.w_max

                elif (code_out & self.bottom):
                    x = x1 + (1/m) * (self.w_min - y1) if (m) else x1
                    y = self.w_min

                elif (code_out & self.right):
                    y = y1 + m * (self.w_max - x1) if (m) else y1
                    x = self.w_max

                elif (code_out & self.left):
                    y = y1 + m * (self.w_min - x1) if (m) else y1
                    x = self.w_min


                # Replace the outside point by the calculated intersection point
                if (code_out == code1): 
                    x1, y1 = x, y
                    code1 = self.get_region_code((x1, y1))

                else:
                    x2, y2 = x, y
                    code2 = self.get_region_code((x2, y2)) 

        return [(x1, y1), (x2, y2)] if (flag) else None


    def liang_barsky(self, line: list[tuple[float, float]]) -> list[tuple[float, float]]|None:
        x1, y1 = line[0]
        x2, y2 = line[1]

        dx = x2 - x1
        dy = y2 - y1

        p = [-dx, dx, -dy, dy]
        q = [x1-self.w_min, self.w_max-x1, y1-self.w_min, self.w_max-y1]

        # if (pi == 0) and (qi == 0) then
        #   line is parallel and outside the window, so reject
        if ( (p[0] == 0 and q[0] < 0) or
            (p[1] == 0 and q[1] < 0) or
            (p[2] == 0 and q[2] < 0) or
            (p[3] == 0 and q[3] < 0) ):
            return None

        u1 = max([0] + [q[i]/p[i] for i in range(4) if p[i] < 0])
        u2 = min([1] + [q[i]/p[i] for i in range(4) if p[i] > 0])

        # if (u1 > u2) then
        #   line is completely outside the window, so reject
        if (u1 > u2):
            return None

        # clipping coordinates
        new_x1 = x1 + u1*dx
        new_y1 = y1 + u1*dy
        new_x2 = x1 + u2*dx
        new_y2 = y1 + u2*dy

        return [(new_x1, new_y1), (new_x2, new_y2)]


    def is_concave(self, coords: list[tuple[float, float]]):
        sign = None
        n = len(coords)
        for i in range(n):
            o = coords[i]
            a = coords[(i + 1) % n]
            b = coords[(i + 2) % n]

            cross_product = (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
            if cross_product != 0:
                if sign is None:
                    sign = m.copysign(1, cross_product)
                elif m.copysign(1, cross_product) != sign:
                    return True

        return False


    # computes the intersection point of the line segment between p1, p2 and cp1, cp2
    def compute_intersection(self, p1, p2, cp1, cp2):
        dc = [cp1[0] - cp2[0], cp1[1] - cp2[1]]
        dp = [p1[0] - p2[0], p1[1] - p2[1]]
        n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
        n2 = p1[0] * p2[1] - p1[1] * p2[0]
        denom = dc[0] * dp[1] - dc[1] * dp[0]

        if denom == 0:
            return None  # lines are parallel or collinear

        x = (n1 * dp[0] - n2 * dc[0]) / denom
        y = (n1 * dp[1] - n2 * dc[1]) / denom
        return (x, y)


    def is_inside(self, point, cp1, cp2):
        return (cp2[0] - cp1[0]) * (point[1] - cp1[1]) > (cp2[1] - cp1[1]) * (point[0] - cp1[0])


    def sutherland_hodgman_clip(self, coords: list[tuple[float, float]]):
        output_list = coords
        window = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

        for i in range(4):
            input_list = output_list
            output_list = []

            cp1 = window[i]
            cp2 = window[(i + 1) % 4]

            if not input_list:
                break

            s = input_list[-1]
            for e in input_list:
                if self.is_inside(e, cp1, cp2):
                    if not self.is_inside(s, cp1, cp2):
                        output_list.append(self.compute_intersection(s, e, cp1, cp2))
                    output_list.append(e)
                elif self.is_inside(s, cp1, cp2):
                    output_list.append(self.compute_intersection(s, e, cp1, cp2))
                s = e

        if output_list:
            return output_list
        else: 
            return None

