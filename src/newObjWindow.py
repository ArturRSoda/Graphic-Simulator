import tkinter as tk
from tkinter import Button, ttk, messagebox

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
        self.polygon_coord_list      : list[tuple[float, float]]
        self.curve_coord_list        : list[list[tuple[float, float, float]]]
        self.wireframe_coord_listbox : tk.Listbox
        self.polygon_coord_listbox   : tk.Listbox
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
        self.polygon_coord_tuple     : tuple[tk.IntVar, tk.IntVar]

        self.system = system
        self.app = tk.Toplevel()
        self.app.title("New Object")
        self.app.geometry("400x400")

        self.add_name_obj_entry()
        self.add_color_buttons()
        self.add_tabs()


    def add_name_obj_entry(self):
        Label(self.app, "Name:", 10).place(x=10, y=15)

        self.obj_name_var = tk.StringVar()
        tk.Entry(self.app, textvariable=self.obj_name_var, width=35).place(x=60, y=10)


    def add_color_buttons(self):
        self.app.update()
        self.color_opt_frame = Frame(self.app, self.app.winfo_width()-20, 60)
        self.color_opt_frame.place(x=10, y=40)

        Label(self.color_opt_frame, "Color:", 10).place(x=10, y=10)

        self.color_opt_var = tk.StringVar(self.color_opt_frame, "Red")
        tk.Radiobutton(self.color_opt_frame, text="Red", variable=self.color_opt_var, value="Red").place(x=10, y=30)
        tk.Radiobutton(self.color_opt_frame, text="Blue", variable=self.color_opt_var, value="Blue").place(x=70, y=30)
        tk.Radiobutton(self.color_opt_frame, text="Green", variable=self.color_opt_var, value="Green").place(x=130, y=30)
        tk.Radiobutton(self.color_opt_frame, text="Black", variable=self.color_opt_var, value="Black").place(x=200, y=30)


    def add_tabs(self):
        self.tab_menu = ttk.Notebook(self.app)

        self.tab_width = self.app.winfo_width()-20
        self.tab_height = self.app.winfo_height()-self.color_opt_frame.winfo_height()-135

        self.add_point_tab()
        self.add_line_tab()
        self.add_wireframe_tab()
        #self.add_polygon_tab()
        self.add_curve_tab()

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

        tk.Button(self.point_tab, text="Add", command=self.add_point).place(x=80, y=self.tab_height-45)
        tk.Button(self.point_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.point_tab, text="Point")


    def add_line_tab(self):
        self.line_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        ttk.Label(self.line_tab, text="Start Coordinates").place(x=10, y=10)
        ttk.Label(self.line_tab, text="End Coordinates").place(x=10, y=90)

        self.line_start_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())
        self.line_end_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())

        self.add_coord_frame(self.line_tab, 10, 30, self.line_start_coord_tuple)
        self.add_coord_frame(self.line_tab, 10, 110, self.line_end_coord_tuple)

        tk.Button(self.line_tab, text="Add", command=self.add_line).place(x=80, y=self.tab_height-45)
        tk.Button(self.line_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.line_tab, text="Line")


    def add_wireframe_tab(self):
        self.wireframe_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.wireframe_coord_list = list()
        self.wireframe_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())

        ttk.Label(self.wireframe_tab, text="Coordinates").place(x=10, y=10)
        self.add_coord_frame(self.wireframe_tab, 10, 30, self.wireframe_coord_tuple)

        ttk.Label(self.wireframe_tab, text="Added Coordinates").place(x=250, y=10)
        self.wireframe_coord_listbox = tk.Listbox(self.wireframe_tab, width=10, height=7)
        self.wireframe_coord_listbox.place(x=260, y=30)

        tk.Button(self.wireframe_tab, text="Add Coord", command=self.add_wireframe_coord).place(x=10, y=90)
        tk.Button(self.wireframe_tab, text="Del Coord", command=self.del_wireframe_coord).place(x=10, y=130)
        tk.Button(self.wireframe_tab, text="Add", command=self.add_wireframe).place(x=80, y=self.tab_height-45)
        tk.Button(self.wireframe_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.wireframe_tab, text="WireFrame")


    def add_polygon_tab(self):
        self.polygon_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.polygon_coord_list = list()
        self.polygon_coord_tuple = (tk.IntVar(), tk.IntVar())

        ttk.Label(self.polygon_tab, text="Coordinates").place(x=10, y=10)
        self.add_coord_frame(self.polygon_tab, 10, 30, self.polygon_coord_tuple)

        ttk.Label(self.polygon_tab, text="Added Coordinates").place(x=200, y=10)
        self.polygon_coord_listbox = tk.Listbox(self.polygon_tab, width=10, height=7)
        self.polygon_coord_listbox.place(x=200, y=30)

        tk.Button(self.polygon_tab, text="Add Coord", command=self.add_polygon_coord).place(x=10, y=90)
        tk.Button(self.polygon_tab, text="Del Coord", command=self.del_polygon_coord).place(x=10, y=130)
        tk.Button(self.polygon_tab, text="Add", command=self.add_polygon).place(x=80, y=self.tab_height-45)
        tk.Button(self.polygon_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.polygon_tab, text="Polygon")


    def add_curve_tab(self):
        self.curve_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.curve_coord_list = list()

        tk.Button(self.curve_tab, text="Add Matrix", command=self.add_matrix).place(x=10, y=40)

        Label(self.curve_tab, "Added Matrices", 10).place(x=130, y=10)
        self.curve_coord_listbox = tk.Listbox(self.curve_tab, width=25, height=9)
        self.curve_coord_listbox.place(x=130, y=40)

        self.curve_opt = tk.StringVar(self.curve_tab, "bezier")
        tk.Radiobutton(self.curve_tab, text="B-Spline", variable=self.curve_opt, value="bspline").place(x=10, y=80)
        tk.Radiobutton(self.curve_tab, text="Bezier", variable=self.curve_opt, value="bezier").place(x=10, y=110)

        tk.Button(self.curve_tab, text="Add", command=self.add_curve).place(x=80, y=self.tab_height-45)
        tk.Button(self.curve_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.curve_tab, text="Curve")


    def add_wireframe_coord(self):
        coord_x = self.verify_num_entry(self.wireframe_coord_tuple[0])
        coord_y = self.verify_num_entry(self.wireframe_coord_tuple[1])
        coord_z = self.verify_num_entry(self.wireframe_coord_tuple[2])

        if (coord_x is not None) and (coord_y is not None) and (coord_z is not None):
            self.wireframe_coord_list.append((coord_x, coord_y, coord_z))
            self.wireframe_coord_listbox.insert(tk.END, "(%d, %d, %d)" % (coord_x, coord_y, coord_z))


    def del_wireframe_coord(self):
        tp = self.wireframe_coord_listbox.curselection()
        if (not tp):
            self.send_error("Select an item", "Please select an item to delete!")
            return

        id = tp[0]
        self.wireframe_coord_listbox.delete(id)
        self.wireframe_coord_list.pop(id)


    def add_polygon_coord(self):
        coord_x = self.verify_num_entry(self.polygon_coord_tuple[0])
        coord_y = self.verify_num_entry(self.polygon_coord_tuple[1])

        if (coord_x is not None) and (coord_y is not None):
            self.polygon_coord_list.append((coord_x, coord_y))
            self.polygon_coord_listbox.insert(tk.END, "(%d , %d)" % (coord_x, coord_y))


    def del_polygon_coord(self):
        tp = self.polygon_coord_listbox.curselection()
        if (not tp):
            self.send_error("Select an item", "Please select an item to delete!")
            return

        id = tp[0]
        self.polygon_coord_listbox.delete(id)
        self.polygon_coord_list.pop(id)


    def add_matrix(self):
        app = tk.Toplevel()
        app.title("Add Matrix")
        app.geometry("200x430")

        Label(app, "Ctrl. Points", 10).grid(row=0, column=0)
        Label(app, "X", 10).grid(row=0, column=1)
        Label(app, "Y", 10).grid(row=0, column=2)
        Label(app, "Z", 10).grid(row=0, column=3)

        entries: list[tuple[tk.Entry, tk.Entry, tk.Entry]] = list()
        for i in range(1, 17):
            tx = tk.Entry(app, width=4)
            ty = tk.Entry(app, width=4)
            tz = tk.Entry(app, width=4)
            entries.append((tx, ty, tz))

            Label(app, "%d" % i, 10).grid(row=i, column=0)
            tx.grid(row=i, column=1)
            ty.grid(row=i, column=2)
            tz.grid(row=i, column=3)

        tk.Button(app, text="Add", command=lambda: self.add_coord_matrix(app, entries)).grid(row=17, column=0, columnspan=2)
        tk.Button(app, text="Cancel", command=app.destroy).grid(row=17, column=2, columnspan=2)


    def add_coord_matrix(self, app, entries: list[tuple[tk.Entry, tk.Entry, tk.Entry]]):
        matrix = list()
        for (ex, ey, ez) in entries:
            x = self.verify_num_entry(ex)
            y = self.verify_num_entry(ey)
            z = self.verify_num_entry(ez)

            if (x is None) or (y is None) or (z is None):
                break

            matrix.append((x, y, z))
        else:
            self.curve_coord_list.append(matrix)
            for i in range(0, len(matrix), 4):
                message = "   (%d, %d, %d) (%d, %d, %d) (%d, %d, %d) (%d, %d, %d)" % (*matrix[i], *matrix[i+1], *matrix[i+2], *matrix[i+3])
                self.curve_coord_listbox.insert(0, message)
            self.curve_coord_listbox.insert(0, "%d ->" % len(self.curve_coord_list))
            app.destroy()



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

        if (len(self.wireframe_coord_list) < 2):
            self.send_error("More coordinates", "Please informe at least 2 coordinates!")
            return

        edges = list()
        for i in range(len(self.wireframe_coord_list)-1):
            edges.append((i, i+1))

        self.system.add_wireframe(name, color, self.wireframe_coord_list, edges)

        coords = ""
        edges_str = ""
        for (c1, c2) in edges: edges_str += "(%d, %d)" % (c1, c2)
        for v in self.wireframe_coord_list: coords += "(%d, %d, %d) " % v
        self.system.interface.add_message("    - Edges: %s" % edges_str)
        self.system.interface.add_message("    - Coord:  %s" % coords)
        self.system.interface.add_message("    - Color:  %s" % color)
        self.system.interface.add_message("    - Name:  %s" % name)
        self.system.interface.add_message("Wireframe added:")

        self.app.destroy()


    def add_polygon(self):
        name = self.obj_name_var.get()
        color = self.color_opt_var.get()

        self.system.add_polygon(name, color, self.polygon_coord_list)

        coords = ""
        for v in self.polygon_coord_list: coords += "(%d, %d) " % v
        self.system.interface.add_message("    - Coord:  %s" % coords)
        self.system.interface.add_message("    - Color:  %s" % color)
        self.system.interface.add_message("    - Name:  %s" % name)
        self.system.interface.add_message("Polygon added:")

        self.app.destroy()


    def add_curve(self):
        name = self.obj_name_var.get()
        color = self.color_opt_var.get()

        """
        minimum_num_coord = 3 if (self.curve_opt.get() == "bezier") else 4
        message = "Pleas insert at least %d coordinates to create a %s curve" % (minimum_num_coord, self.curve_opt.get())
        if (len(self.curve_coord_list) < minimum_num_coord):
            self.send_error("Minimum coordinates", message)
            return
        """

        self.system.add_curve(name, color, self.curve_coord_list, self.curve_opt.get())

        coords = ""
        for m in self.curve_coord_list:
            for c in m:
                coords += "(%d, %d, %d) " % c
        self.system.interface.add_message("    - Coord:  %s" % coords)
        self.system.interface.add_message("    - Color:  %s" % color)
        self.system.interface.add_message("    - Name:  %s" % name)
        self.system.interface.add_message("Curve added:")

        self.app.destroy()


    def cancel(self):
        self.app.destroy()


    def verify_num_entry(self, entry) -> int|float|None:
        try:
            value = float(entry.get())
        except Exception as e:
            self.send_error("Value Error", "Please enter a numeric value on entry")
        else:
            return value


    def send_error(self, title: str, message: str):
        messagebox.showerror(title, message)

