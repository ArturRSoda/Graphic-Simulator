from CGSystemInterface import CGSystemInterface
from newObjWindow import NewObjWindow

from objects import Object, Point, Line, WireFrame

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

        self.update_viewport()
        self.interface.app.mainloop()

    def add_object(self):
        NewObjWindow(self)

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

    def del_object(self):
        id = self.interface.objects_listbox.curselection()[0]

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

    def move_window_up(self, offset: int):
        self.Wcoord_min = (self.Wcoord_min[0], self.Wcoord_min[1]+offset)
        self.Wcoord_max = (self.Wcoord_max[0], self.Wcoord_max[1]+offset)
        self.update_viewport()
        
        self.add_message("window moved up by %d" % offset)

    def move_window_down(self, offset: int):
        self.Wcoord_min = (self.Wcoord_min[0], self.Wcoord_min[1]-offset)
        self.Wcoord_max = (self.Wcoord_max[0], self.Wcoord_max[1]-offset)
        self.update_viewport()

        self.add_message("window moved down by %d" % offset)

    def move_window_left(self, offset: int):
        self.Wcoord_min = (self.Wcoord_min[0]-offset, self.Wcoord_min[1])
        self.Wcoord_max = (self.Wcoord_max[0]-offset, self.Wcoord_max[1])
        self.update_viewport()

        self.add_message("window moved left by %d" % offset)

    def move_window_right(self, offset: int):
        self.Wcoord_min = (self.Wcoord_min[0]+offset, self.Wcoord_min[1])
        self.Wcoord_max = (self.Wcoord_max[0]+offset, self.Wcoord_max[1])
        self.update_viewport()

        self.add_message("window moved right by %d" % offset)

    def zoom_window_in(self, offset: int):
        self.Wcoord_min = (self.Wcoord_min[0]+offset, self.Wcoord_min[1]+offset)
        self.Wcoord_max = (self.Wcoord_max[0]-offset, self.Wcoord_max[1]-offset)
        self.update_viewport()

        self.add_message("window zoomed in by %d" % offset)

    def zoom_window_out(self, offset):
        self.Wcoord_min = (self.Wcoord_min[0]-offset, self.Wcoord_min[1]-offset)
        self.Wcoord_max = (self.Wcoord_max[0]+offset, self.Wcoord_max[1]+offset)
        self.update_viewport()

        self.add_message("window zoomed out by %d" % offset)

    def add_message(self, message: str):
        self.interface.messageBox.insert(0, message)
