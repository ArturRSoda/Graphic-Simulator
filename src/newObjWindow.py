import tkinter as tk
from tkinter import ttk, messagebox

from CGSystemInterface import Label, Frame, Tab

class NewObjWindow:
    def __init__(self, system):
        self.tab_menu                : ttk.Notebook
        self.point_tab               : Tab
        self.line_tab                : Tab
        self.wireframe_tab           : Tab
        self.polygon_tab             : Tab
        self.curve_tab               : Tab
        self.color_opt_frame         : Frame
        self.wireframe_coord_list    : list[tuple[float, float, float]]
        self.wireframe_edges_list    : list[tuple[float, float]]
        self.polygon_coord_list      : list[tuple[float, float, float]]
        self.polygon_edges_list      : list[tuple[float, float]]
        self.curve_coord_list        : list[tuple[float, float]]
        self.wireframe_coord_listbox : tk.Listbox
        self.wireframe_edges_listbox : tk.Listbox
        self.polygon_coord_listbox   : tk.Listbox
        self.polygon_edges_listbox   : tk.Listbox
        self.curve_coord_listbox     : tk.Listbox
        self.color_opt_var           : tk.StringVar
        self.obj_name_var            : tk.StringVar
        self.curve_opt               : tk.StringVar
        self.tab_width               : float
        self.tab_height              : float

        self.point_coord_tuple       : tuple[tk.IntVar, tk.IntVar, tk.IntVar]
        self.line_start_coord_tuple  : tuple[tk.IntVar, tk.IntVar, tk.IntVar]
        self.line_end_coord_tuple    : tuple[tk.IntVar, tk.IntVar, tk.IntVar]
        self.wireframe_coord_tuple   : tuple[tk.IntVar, tk.IntVar, tk.IntVar]
        self.wireframe_edges_tuple   : tuple[tk.IntVar, tk.IntVar]
        self.polygon_coord_tuple     : tuple[tk.IntVar, tk.IntVar, tk.IntVar]
        self.polygon_edges_tuple     : tuple[tk.IntVar, tk.IntVar]
        self.curve_coord_tuple       : tuple[tk.IntVar, tk.IntVar]

        self.system = system
        self.app = tk.Toplevel()
        self.app.title("New Object")
        self.app.geometry("550x430")

        self.add_name_obj_entry()
        self.add_color_buttons()
        self.add_tabs()


    def add_name_obj_entry(self):
        Label(self.app, "Name:", 10).place(x=10, y=15)

        self.obj_name_var = tk.StringVar()
        tk.Entry(self.app, textvariable=self.obj_name_var, width=50).place(x=60, y=10)

    def add_color_buttons(self):
        self.app.update()
        self.color_opt_frame = Frame(self.app, self.app.winfo_width()-20, 60)
        self.color_opt_frame.place(x=10, y=40)

        Label(self.color_opt_frame, "Color:", 10).place(x=10, y=10)

        self.color_opt_var = tk.StringVar(self.color_opt_frame, "red")
        tk.Radiobutton(self.color_opt_frame, text="Red", variable=self.color_opt_var, value="red").place(x=10, y=30)
        tk.Radiobutton(self.color_opt_frame, text="Blue", variable=self.color_opt_var, value="blue").place(x=70, y=30)
        tk.Radiobutton(self.color_opt_frame, text="Green", variable=self.color_opt_var, value="green").place(x=130, y=30)
        tk.Radiobutton(self.color_opt_frame, text="Black", variable=self.color_opt_var, value="black").place(x=200, y=30)
        tk.Radiobutton(self.color_opt_frame, text="Purple", variable=self.color_opt_var, value="purple").place(x=270, y=30)

    def add_tabs(self):
        self.tab_menu = ttk.Notebook(self.app)

        self.tab_width = self.app.winfo_width()-20
        self.tab_height = self.app.winfo_height()-self.color_opt_frame.winfo_height()-135

        self.add_point_tab()
        self.add_line_tab()
        self.add_wireframe_tab()
        self.add_polygon_tab()
        #self.add_curve_tab()

        self.tab_menu.place(x=10, y=105)

    def add_coord_frame(self, parent, x: float, y: float, variables: tuple[tk.IntVar, tk.IntVar, tk.IntVar]):
        fm = Frame(parent, width=240, height=50)
        fm.place(x=x, y=y)

        Label(fm, "X:", 10).place(x=10, y=10)
        tk.Entry(fm, textvariable=variables[0], width=4).place(x=30, y=10)

        Label(fm, "Y:", 10).place(x=80, y=10)
        tk.Entry(fm, textvariable=variables[1], width=4).place(x=100, y=10)

        Label(fm, "Z:", 10).place(x=150, y=10)
        tk.Entry(fm, textvariable=variables[2], width=4).place(x=170, y=10)


    def add_point_tab(self):
        self.point_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.point_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())

        ttk.Label(self.point_tab, text="Coordinates").place(x=10, y=10)
        self.add_coord_frame(self.point_tab, 10, 30, self.point_coord_tuple)

        tk.Button(self.point_tab, text="Add", command=self.add_point).place(x=170, y=self.tab_height-45)
        tk.Button(self.point_tab, text="Cancel", command=self.cancel).place(x=300, y=self.tab_height-45)

        self.tab_menu.add(self.point_tab, text="Point")

    def add_line_tab(self):
        self.line_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        ttk.Label(self.line_tab, text="Start Coordinates").place(x=10, y=10)
        ttk.Label(self.line_tab, text="End Coordinates").place(x=10, y=90)

        self.line_start_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())
        self.line_end_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())

        self.add_coord_frame(self.line_tab, 10, 30, self.line_start_coord_tuple)
        self.add_coord_frame(self.line_tab, 10, 110, self.line_end_coord_tuple)

        tk.Button(self.line_tab, text="Add", command=self.add_line).place(x=170, y=self.tab_height-45)
        tk.Button(self.line_tab, text="Cancel", command=self.cancel).place(x=300, y=self.tab_height-45)

        self.tab_menu.add(self.line_tab, text="Line")

    def add_vertex_frame(self, parent, x: float, y: float, variables: tuple[tk.IntVar, tk.IntVar]):
        fm = Frame(parent, width=240, height=50)
        fm.place(x=x, y=y)

        Label(fm, "VTX1:", 10).place(x=10, y=10)
        tk.Entry(fm, textvariable=variables[0], width=4).place(x=50, y=10)

        Label(fm, "VTX2:", 10).place(x=100, y=10)
        tk.Entry(fm, textvariable=variables[1], width=4).place(x=140, y=10)


    def add_wireframe_tab(self):
        self.wireframe_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.wireframe_coord_list = list()
        self.wireframe_edges_list = list()
        self.wireframe_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())
        self.wireframe_edges_tuple = (tk.IntVar(), tk.IntVar())

        ttk.Label(self.wireframe_tab, text="Coordinates").place(x=10, y=10)
        self.add_coord_frame(self.wireframe_tab, 10, 30, self.wireframe_coord_tuple)

        ttk.Label(self.wireframe_tab, text="Added Coordinates").place(x=120, y=85)
        self.wireframe_coord_listbox = tk.Listbox(self.wireframe_tab, width=13, height=7)
        self.wireframe_coord_listbox.place(x=120, y=105)

        tk.Button(self.wireframe_tab, text="Add Coord", command=self.add_wireframe_coord).place(x=10, y=110)
        tk.Button(self.wireframe_tab, text="Del Coord", command=self.del_wireframe_coord).place(x=10, y=150)

        ttk.Label(self.wireframe_tab, text="Edges").place(x=260, y=10)
        self.add_vertex_frame(self.wireframe_tab, 260, 30, self.wireframe_edges_tuple)

        tk.Label(self.wireframe_tab, text="Added Edges").place(x=370, y=85)
        self.wireframe_edges_listbox = tk.Listbox(self.wireframe_tab, width=10, height=7) 
        self.wireframe_edges_listbox.place(x=370, y=105)

        tk.Button(self.wireframe_tab, text="Add Edge", command=self.add_wireframe_edge).place(x=260, y=110)
        tk.Button(self.wireframe_tab, text="Del Edge", command=self.del_wireframe_edge).place(x=260, y=150)

        tk.Button(self.wireframe_tab, text="Add", command=self.add_wireframe).place(x=170, y=self.tab_height-45)
        tk.Button(self.wireframe_tab, text="Cancel", command=self.cancel).place(x=300, y=self.tab_height-45)


        self.tab_menu.add(self.wireframe_tab, text="WireFrame")

    def add_polygon_tab(self):
        self.polygon_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.polygon_coord_list = list()
        self.polygon_edges_list = list()
        self.polygon_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())
        self.polygon_edges_tuple = (tk.IntVar(), tk.IntVar())

        ttk.Label(self.polygon_tab, text="Coordinates").place(x=10, y=10)
        self.add_coord_frame(self.polygon_tab, 10, 30, self.polygon_coord_tuple)

        ttk.Label(self.polygon_tab, text="Added Coordinates").place(x=120, y=85)
        self.polygon_coord_listbox = tk.Listbox(self.polygon_tab, width=13, height=7)
        self.polygon_coord_listbox.place(x=120, y=105)

        tk.Button(self.polygon_tab, text="Add Coord", command=self.add_polygon_coord).place(x=10, y=110)
        tk.Button(self.polygon_tab, text="Del Coord", command=self.del_polygon_coord).place(x=10, y=150)

        ttk.Label(self.polygon_tab, text="Edges").place(x=260, y=10)
        self.add_vertex_frame(self.polygon_tab, 260, 30, self.polygon_edges_tuple)

        tk.Label(self.polygon_tab, text="Added Edges").place(x=370, y=85)
        self.polygon_edges_listbox = tk.Listbox(self.polygon_tab, width=10, height=7) 
        self.polygon_edges_listbox.place(x=370, y=105)

        tk.Button(self.polygon_tab, text="Add Edge", command=self.add_polygon_edge).place(x=260, y=110)
        tk.Button(self.polygon_tab, text="Del Edge", command=self.del_polygon_edge).place(x=260, y=150)

        tk.Button(self.polygon_tab, text="Add", command=self.add_polygon).place(x=170, y=self.tab_height-45)
        tk.Button(self.polygon_tab, text="Cancel", command=self.cancel).place(x=300, y=self.tab_height-45)
        self.tab_menu.add(self.polygon_tab, text="Polygon")

    def add_curve_tab(self):
        self.curve_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.curve_coord_list = list()
        self.curve_coord_tuple = (tk.IntVar(), tk.IntVar())

        ttk.Label(self.curve_tab, text="Control coordinates").place(x=10, y=10)
        self.add_coord_frame(self.curve_tab, 10, 30, self.curve_coord_tuple)

        ttk.Label(self.curve_tab, text="Added Coordinates").place(x=200, y=10)
        self.curve_coord_listbox = tk.Listbox(self.curve_tab, width=10, height=7)
        self.curve_coord_listbox.place(x=200, y=30)

        self.curve_opt = tk.StringVar(self.curve_tab, "bspline")
        tk.Radiobutton(self.curve_tab, text="B-Spline", variable=self.curve_opt, value="bspline").place(x=10, y=170)
        tk.Radiobutton(self.curve_tab, text="Bezier", variable=self.curve_opt, value="bezier").place(x=100, y=170)

        tk.Button(self.curve_tab, text="Add Coord", command=self.add_curve_coord).place(x=10, y=90)
        tk.Button(self.curve_tab, text="Del Coord", command=self.del_curve_coord).place(x=10, y=130)
        tk.Button(self.curve_tab, text="Add", command=self.add_curve).place(x=170, y=self.tab_height-45)
        tk.Button(self.curve_tab, text="Cancel", command=self.cancel).place(x=300, y=self.tab_height-45)

        self.tab_menu.add(self.curve_tab, text="Curve")

    def add_wireframe_coord(self):
        coord_x = self.verify_num_entry(self.wireframe_coord_tuple[0])
        coord_y = self.verify_num_entry(self.wireframe_coord_tuple[1])
        coord_z = self.verify_num_entry(self.wireframe_coord_tuple[2])

        if (coord_x is not None) and (coord_y is not None) and (coord_z is not None):
            self.wireframe_coord_list.append((coord_x, coord_y, coord_z))
            self.wireframe_coord_listbox.insert(tk.END, "%d - (%d, %d, %d)" % (len(self.wireframe_coord_list)-1, coord_x, coord_y, coord_z))

    def del_wireframe_coord(self):
        tp = self.wireframe_coord_listbox.curselection()
        if (not tp):
            self.send_error("Select an item", "Please select an item to delete!")
            return

        id = tp[0]
        self.wireframe_coord_list.pop(id)

        self.wireframe_coord_listbox.delete(0, tk.END)
        for i, (x, y, z) in enumerate(self.wireframe_coord_list):
            self.wireframe_coord_listbox.insert(tk.END, "%d - (%d, %d, %d)" % (i, x, y, z))

        edges_list = list()
        for (v1, v2) in self.wireframe_edges_list:
            if (v1 == id) or (v2 == id): continue

            vtx1, vtx2 = v1, v2
            if (v1 > id): vtx1 -= 1
            if (v2 > id): vtx2 -= 1

            edges_list.append((vtx1, vtx2))

        self.wireframe_edges_list = edges_list

        self.wireframe_edges_listbox.delete(0, tk.END)
        for (v1, v2) in self.wireframe_edges_list:
            self.wireframe_edges_listbox.insert(tk.END, "(%d, %d)" % (v1, v2))

    def add_wireframe_edge(self):
        vtx1 = self.verify_num_entry(self.wireframe_edges_tuple[0])
        vtx2 = self.verify_num_entry(self.wireframe_edges_tuple[1])

        if (vtx1 is not None) and (vtx2 is not None):
            if ((vtx1, vtx2) not in self.wireframe_edges_list) and (vtx1 != vtx2):
                ln = len(self.wireframe_coord_list)
                if (vtx1 >= ln) or (vtx2 >= ln):
                    self.send_error("Invalid Vertex", "Please enter an existing vertex!")
                    return

                self.wireframe_edges_list.append((vtx1, vtx2))
                self.wireframe_edges_listbox.insert(tk.END, "(%d, %d)" % (vtx1, vtx2))

    def del_wireframe_edge(self):
        tp = self.wireframe_edges_listbox.curselection()
        if (not tp):
            self.send_error("Select an item", "Please select an item to delete!")
            return

        id = tp[0]
        self.wireframe_edges_list.pop(id)
        self.wireframe_edges_listbox.delete(id)


    def add_polygon_coord(self):
        coord_x = self.verify_num_entry(self.polygon_coord_tuple[0])
        coord_y = self.verify_num_entry(self.polygon_coord_tuple[1])
        coord_z = self.verify_num_entry(self.polygon_coord_tuple[2])

        if (coord_x is not None) and (coord_y is not None) and (coord_z is not None):
            self.polygon_coord_list.append((coord_x, coord_y, coord_z))
            self.polygon_coord_listbox.insert(tk.END, "%d - (%d, %d, %d)" % (len(self.polygon_coord_list)-1, coord_x, coord_y, coord_z))

    def del_polygon_coord(self):
        tp = self.polygon_coord_listbox.curselection()
        if (not tp):
            self.send_error("Select an item", "Please select an item to delete!")
            return

        id = tp[0]
        self.polygon_coord_list.pop(id)

        self.polygon_coord_listbox.delete(0, tk.END)
        for i, (x, y, z) in enumerate(self.polygon_coord_list):
            self.polygon_coord_listbox.insert(tk.END, "%d - (%d, %d, %d)" % (i, x, y, z))

        edges_list = list()
        for (v1, v2) in self.polygon_edges_list:
            if (v1 == id) or (v2 == id): continue

            vtx1, vtx2 = v1, v2
            if (v1 > id): vtx1 -= 1
            if (v2 > id): vtx2 -= 1

            edges_list.append((vtx1, vtx2))

        self.polygon_edges_list = edges_list

        self.polygon_edges_listbox.delete(0, tk.END)
        for (v1, v2) in self.polygon_edges_list:
            self.polygon_edges_listbox.insert(tk.END, "(%d, %d)" % (v1, v2))

    def add_polygon_edge(self):
        vtx1 = self.verify_num_entry(self.polygon_edges_tuple[0])
        vtx2 = self.verify_num_entry(self.polygon_edges_tuple[1])

        if (vtx1 is not None) and (vtx2 is not None):
            if ((vtx1, vtx2) not in self.polygon_edges_list) and (vtx1 != vtx2):
                ln = len(self.polygon_coord_list)
                if (vtx1 >= ln) or (vtx2 >= ln):
                    self.send_error("Invalid Vertex", "Please enter an existing vertex!")
                    return

                self.polygon_edges_list.append((vtx1, vtx2))
                self.polygon_edges_listbox.insert(tk.END, "(%d, %d)" % (vtx1, vtx2))

    def del_polygon_edge(self):
        tp = self.polygon_edges_listbox.curselection()
        if (not tp):
            self.send_error("Select an item", "Please select an item to delete!")
            return

        id = tp[0]
        self.polygon_edges_list.pop(id)
        self.polygon_edges_listbox.delete(id)

    def add_curve_coord(self):
        coord_x = self.verify_num_entry(self.curve_coord_tuple[0])
        coord_y = self.verify_num_entry(self.curve_coord_tuple[1])

        if (coord_x is not None) and (coord_y is not None):
            self.curve_coord_list.append((coord_x, coord_y))
            self.curve_coord_listbox.insert(tk.END, "(%d , %d)" % (coord_x, coord_y))

    def del_curve_coord(self):
        tp = self.curve_coord_listbox.curselection()
        if (not tp):
            self.send_error("Select an item", "Please select an item to delete!")
            return

        id = tp[0]
        self.curve_coord_listbox.delete(id)
        self.curve_coord_list.pop(id)

    def add_point(self):
        coord_x = self.verify_num_entry(self.point_coord_tuple[0])
        coord_y = self.verify_num_entry(self.point_coord_tuple[1])
        coord_z = self.verify_num_entry(self.point_coord_tuple[2])

        if (coord_x is not None) and (coord_y is not None) and (coord_z is not None):
            name = self.obj_name_var.get()
            color = self.color_opt_var.get()
            self.system.add_point(name, color, (coord_x, coord_y, coord_z))

            self.system.interface.add_message("    - Coord:  (%d, %d, %d)" % (coord_x, coord_y, coord_z))
            self.system.interface.add_message("    - Color:  %s" % color)
            self.system.interface.add_message("    - Name:  %s" % name)
            self.system.interface.add_message("Point added:")

            self.app.destroy()

    def add_line(self):
        start_coord_x = self.verify_num_entry(self.line_start_coord_tuple[0])
        start_coord_y = self.verify_num_entry(self.line_start_coord_tuple[1])
        start_coord_z = self.verify_num_entry(self.line_start_coord_tuple[2])

        end_coord_x = self.verify_num_entry(self.line_end_coord_tuple[0])
        end_coord_y = self.verify_num_entry(self.line_end_coord_tuple[1])
        end_coord_z = self.verify_num_entry(self.line_end_coord_tuple[2])

        if (start_coord_x is not None) and (start_coord_y is not None) and (start_coord_z is not None) and (end_coord_x is not None) and (end_coord_y is not None) and (end_coord_z is not None):
            start_coord = (start_coord_x, start_coord_y, start_coord_z)
            end_coord = (end_coord_x, end_coord_y, end_coord_z)
            name = self.obj_name_var.get()
            color = self.color_opt_var.get()

            self.system.add_line(name, color, start_coord, end_coord)

            self.system.interface.add_message("    - Coord:  (%d, %d, %d) to (%d, %d, %d)" % (start_coord[0], start_coord[1], start_coord[2], end_coord[0], end_coord[1], end_coord[2]))
            self.system.interface.add_message("    - Color:  %s" % color)
            self.system.interface.add_message("    - Name:  %s" % name)
            self.system.interface.add_message("Line added:")

            self.app.destroy()

    def add_wireframe(self):
        name = self.obj_name_var.get()
        color = self.color_opt_var.get()

        self.system.add_wireframe(name, color, self.wireframe_coord_list, self.wireframe_edges_list)


        coords = ""
        edges = ""
        for v in self.wireframe_coord_list: coords += "(%d, %d, %d) " % v
        for e in self.wireframe_edges_list: edges += "(%d, %d)" % e
        self.system.interface.add_message("    - Edges:  %s" % edges)
        self.system.interface.add_message("    - Coord:  %s" % coords)
        self.system.interface.add_message("    - Color:  %s" % color)
        self.system.interface.add_message("    - Name:  %s" % name)
        self.system.interface.add_message("Wireframe added:")

        self.app.destroy()

    def add_polygon(self):
        name = self.obj_name_var.get()
        color = self.color_opt_var.get()

        self.system.add_polygon(name, color, self.polygon_coord_list, self.polygon_edges_list)

        coords = ""
        edges = ""
        for v in self.polygon_coord_list: coords += "(%d, %d, %d) " % v
        for e in self.polygon_edges_list: edges += "(%d, %d)" % e
        self.system.interface.add_message("    - Edges:  %s" % edges)
        self.system.interface.add_message("    - Coord:  %s" % coords)
        self.system.interface.add_message("    - Color:  %s" % color)
        self.system.interface.add_message("    - Name:  %s" % name)
        self.system.interface.add_message("Polygon added:")

        self.app.destroy()

    def add_curve(self):
        name = self.obj_name_var.get()
        color = self.color_opt_var.get()

        minimum_num_coord = 3 if (self.curve_opt.get() == "bezier") else 4
        message = "Pleas insert at least %d coordinates to create a %s curve" % (minimum_num_coord, self.curve_opt.get())
        if (len(self.curve_coord_list) < minimum_num_coord):
            self.send_error("Minimum coordinates", message)
            return

        self.system.add_curve(name, color, self.curve_coord_list, self.curve_opt.get())

        coords = ""
        for v in self.curve_coord_list: coords += "(%d, %d) " % v
        self.system.interface.add_message("    - Coord:  %s" % coords)
        self.system.interface.add_message("    - Color:  %s" % color)
        self.system.interface.add_message("    - Name:  %s" % name)
        self.system.interface.add_message("Curve added:")

        self.app.destroy()

    def cancel(self):
        self.app.destroy()

    def verify_num_entry(self, entry) -> int|float|None:
        try:
            value = entry.get()
        except Exception as e:
            self.send_error("Value Error", "Please enter a numeric value on entry")
        else:
            return value

    def send_error(self, title: str, message: str):
        messagebox.showerror(title, message)
