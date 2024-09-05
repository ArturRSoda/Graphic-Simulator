import tkinter as tk
from tkinter import ttk, messagebox

from CGSystemInterface import Label, Frame

class Tab(ttk.Frame):
    def __init__(self, parent, width: int, height: int):
        super().__init__(parent, width=width, height=height, borderwidth=3, relief="ridge")

class NewObjWindow:
    def __init__(self, system):
        self.tab_menu                : ttk.Notebook
        self.point_tab               : Tab
        self.line_tab                : Tab
        self.wireframe_tab           : Tab
        self.color_opt_frame         : Frame
        self.wireframe_coord_list    : list[tuple[int, int]]
        self.wireframe_coord_listbox : tk.Listbox
        self.color_opt_var           : tk.StringVar
        self.obj_name_var            : tk.StringVar
        self.tab_width               : int
        self.tab_height              : int

        self.point_coord_tuple       : tuple[tk.IntVar, tk.IntVar]
        self.line_start_coord_tuple  : tuple[tk.IntVar, tk.IntVar]
        self.line_end_coord_tuple    : tuple[tk.IntVar, tk.IntVar]
        self.wireframe_coord_tuple   : tuple[tk.IntVar, tk.IntVar]

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

    def add_tabs(self):
        self.tab_menu = ttk.Notebook(self.app)

        self.tab_width = self.app.winfo_width()-20
        self.tab_height = self.app.winfo_height()-self.color_opt_frame.winfo_height()-135

        self.add_point_tab()
        self.add_line_tab()
        self.add_wireframe_tab()

        self.tab_menu.place(x=10, y=105)

    def add_coord_frame(self, parent, x: int, y: int, variables: tuple[tk.IntVar, tk.IntVar]):
        fm = Frame(parent, width=160, height=50)
        fm.place(x=x, y=y)

        Label(fm, "X:", 10).place(x=10, y=15)
        tk.Entry(fm, textvariable=variables[0], width=4).place(x=30, y=10)
        
        Label(fm, "Y:", 10).place(x=80, y=15)
        tk.Entry(fm, textvariable=variables[1], width=4).place(x=100, y=10)


    def add_point_tab(self):
        self.point_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.point_coord_tuple = (tk.IntVar(), tk.IntVar())

        ttk.Label(self.point_tab, text="Coordinates").place(x=10, y=10)
        self.add_coord_frame(self.point_tab, 10, 30, self.point_coord_tuple)

        tk.Button(self.point_tab, text="Add", command=self.add_point).place(x=80, y=self.tab_height-45)
        tk.Button(self.point_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.point_tab, text="Point")

    def add_line_tab(self):
        self.line_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        ttk.Label(self.line_tab, text="Start Coordinates").place(x=10, y=10)
        ttk.Label(self.line_tab, text="End Coordinates").place(x=10, y=90)

        self.line_start_coord_tuple = (tk.IntVar(), tk.IntVar())
        self.line_end_coord_tuple = (tk.IntVar(), tk.IntVar())

        self.add_coord_frame(self.line_tab, 10, 30, self.line_start_coord_tuple)
        self.add_coord_frame(self.line_tab, 10, 110, self.line_end_coord_tuple)

        tk.Button(self.line_tab, text="Add", command=self.add_line).place(x=80, y=self.tab_height-45)
        tk.Button(self.line_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.line_tab, text="Line")

    def add_wireframe_tab(self):
        self.wireframe_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.wireframe_coord_list = list()
        self.wireframe_coord_tuple = (tk.IntVar(), tk.IntVar())

        ttk.Label(self.wireframe_tab, text="Coordinates").place(x=10, y=10)
        self.add_coord_frame(self.wireframe_tab, 10, 30, self.wireframe_coord_tuple)

        ttk.Label(self.wireframe_tab, text="Added Coordinates").place(x=200, y=10)
        self.wireframe_coord_listbox = tk.Listbox(self.wireframe_tab, width=10, height=7)
        self.wireframe_coord_listbox.place(x=200, y=30)

        tk.Button(self.wireframe_tab, text="Add Coord", command=self.add_wireframe_coord).place(x=10, y=90)
        tk.Button(self.wireframe_tab, text="Del Coord", command=self.del_wireframe_coord).place(x=10, y=130)
        tk.Button(self.wireframe_tab, text="Add", command=self.add_wireframe).place(x=80, y=self.tab_height-45)
        tk.Button(self.wireframe_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)


        self.tab_menu.add(self.wireframe_tab, text="WireFrame")

    def add_wireframe_coord(self):
        coord_x = self.verify_int_entry(self.wireframe_coord_tuple[0])
        coord_y = self.verify_int_entry(self.wireframe_coord_tuple[1])

        if (coord_x is not None) and (coord_y is not None):
            self.wireframe_coord_list.append((coord_x, coord_y))
            self.wireframe_coord_listbox.insert(tk.END, "(%d , %d)" % (coord_x, coord_y))

    def del_wireframe_coord(self):
        id = self.wireframe_coord_listbox.curselection()[0]
        self.wireframe_coord_listbox.delete(id)
        self.wireframe_coord_list.pop(id)

    def add_point(self):
        coord_x = self.verify_int_entry(self.point_coord_tuple[0])
        coord_y = self.verify_int_entry(self.point_coord_tuple[1])

        if (coord_x is not None) and (coord_y is not None):
            self.system.add_point(self.obj_name_var.get(), self.color_opt_var.get(), (coord_x, coord_y))
            self.app.destroy()

    def add_line(self):
        start_coord_x = self.verify_int_entry(self.line_start_coord_tuple[0])
        start_coord_y = self.verify_int_entry(self.line_start_coord_tuple[1])

        end_coord_x = self.verify_int_entry(self.line_end_coord_tuple[0])
        end_coord_y = self.verify_int_entry(self.line_end_coord_tuple[1])

        if (start_coord_x is not None) and (start_coord_y is not None) and (end_coord_x is not None):
            start_coord = (start_coord_x, start_coord_y)
            end_coord = (end_coord_x, end_coord_y)
            self.system.add_line(self.obj_name_var.get(), self.color_opt_var.get(), start_coord, end_coord)
            self.app.destroy()

    def add_wireframe(self):
        self.system.add_wireframe(self.obj_name_var.get(), self.color_opt_var.get(), self.wireframe_coord_list)
        self.app.destroy()

    def cancel(self):
        self.app.destroy()

    def verify_int_entry(self, entry) -> int|None:
        try:
            value = entry.get()
        except Exception as e:
            self.send_error("Value Error", "Please enter a integer value on entry")
        else:
            return value

    def send_error(self, title: str, message: str):
        messagebox.showerror(title, message)
