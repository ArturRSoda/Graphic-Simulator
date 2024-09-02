import tkinter as tk
from tkinter import ttk

from objects import Object, Point, Line, WireFrame

class Frame(tk.Frame):
    def __init__(self, parent, width: int, height: int):
        super().__init__(parent, width=width, height=height, borderwidth=3, relief="groove")


class Label(tk.Label):
    def __init__(self, parent, text: str, size: int):
        super().__init__(parent, text=text, font=("Helvetica", size))

class Tab(ttk.Frame):
    def __init__(self, parent, width: int, height: int):
        super().__init__(parent, width=width, height=height, borderwidth=3, relief="ridge")

class NewObjWindow:
    def __init__(self, parent):
        self.parent = parent
        self.app = tk.Toplevel()
        self.app.title("New Object")
        self.app.geometry("400x400")

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
        coord = (self.wireframe_coord_tuple[0].get(), self.wireframe_coord_tuple[1].get())
        self.wireframe_coord_list.append(coord)
        self.wireframe_coord_listbox.insert(tk.END, "(%d , %d)" % (coord[0], coord[1]))


    def del_wireframe_coord(self):
        id = self.wireframe_coord_listbox.curselection()[0]
        self.wireframe_coord_listbox.delete(id)
        self.wireframe_coord_list.pop(id)


    def add_point(self):
        coord=(self.point_coord_tuple[0].get(), self.point_coord_tuple[1].get())
        self.parent.add_point(self.obj_name_var.get(), self.color_opt_var.get(), coord)
        self.app.destroy()

    def add_line(self):
        start_coord = (self.line_start_coord_tuple[0].get(), self.line_start_coord_tuple[1].get())
        end_coord = (self.line_end_coord_tuple[0].get(), self.line_end_coord_tuple[1].get())
        self.parent.add_line(self.obj_name_var.get(), self.color_opt_var.get(), start_coord, end_coord)
        self.app.destroy()

    def add_wireframe(self):
        self.parent.add_wireframe(self.obj_name_var.get(), self.color_opt_var.get(), self.wireframe_coord_list)
        self.app.destroy()

    def cancel(self):
        self.app.destroy()

class CGSystem():
    def __init__(self) -> None:
        self.app = tk.Tk()
        self.app.title("Computer Graphics System")
        self.app.geometry("1000x700")

        self.menu_frame        : Frame
        self.object_menu_frame : Frame
        self.window_menu_frame : Frame
        self.viewport_frame    : Frame
        self.messageBox_frame  : Frame
        self.messageBox        : tk.Listbox
        self.objects_listbox   : tk.Listbox
        self.canvas            : tk.Canvas
        self.offset_var          : tk.IntVar
        self.offset_entry        : tk.Entry

        self.Wcoord_min        : tuple[int, int]
        self.Wcoord_max        : tuple[int, int]
        self.VPcoord_min       : tuple[int, int]
        self.VPcoord_max       : tuple[int, int]

        self.Wcoord_min = (-100, -100)
        self.Wcoord_max = (100, 100)

        self.display_file = list()

        self.add_menu()
        self.add_viewport()
        self.add_messagesBox()

        #linha x e y
        self.display_file.append(Line("X", "black", [(-10000, 0), (10000, 0)]))
        self.display_file.append(Line("Y", "black", [(0, -10000), (0, 10000)]))
        self.update_viewport()

    def transform_coordinates(self, coord: tuple[int, int]) -> tuple[float, float]:
        Xw = coord[0]
        Yw = coord[1]

        Xwmin, Ywmin  = self.Wcoord_min
        Xwmax, Ywmax = self.Wcoord_max

        Xvpmin, Yvpmin = self.VPcoord_min
        Xvpmax, Yvpmax = self.VPcoord_max

        Xvp = ( (Xw - Xwmin) / (Xwmax - Xwmin) ) * (Xvpmax - Xvpmin)
        Yvp = ( 1 - ((Yw - Ywmin) / (Ywmax - Ywmin)) ) * (Yvpmax - Yvpmin)


        print("resultado: ", Xvp, Yvp)
        return (Xvp, Yvp)


    def run(self):
        self.app.mainloop()

    def add_viewport(self):
        self.app.update()

        self.viewport_frame = Frame(self.app, self.app.winfo_width()-self.menu_frame.winfo_width()-20, 500)
        self.viewport_frame.place(x=self.menu_frame.winfo_width()+20, y=10)

        Label(self.viewport_frame, "Viewport", 10).place(x=10, y=10)

        self.app.update()

        # sei la
        self.VPcoord_max = (self.viewport_frame.winfo_width()-35, self.viewport_frame.winfo_height()-70)
        self.VPcoord_min = (0, 0)

        self.canvas = tk.Canvas(self.viewport_frame, width=self.VPcoord_max[0], height=self.VPcoord_max[1], bg="white", borderwidth=5, relief="groove")
        self.canvas.place(x=10, y=30)

    def add_messagesBox(self):
        self.app.update()
        width = self.app.winfo_width()-self.menu_frame.winfo_width()-20
        height = self.app.winfo_height()-self.viewport_frame.winfo_height()-30
        self.messageBox_frame = Frame(self.app, width, height)
        self.messageBox_frame.place(x=self.menu_frame.winfo_width()+20, y=self.viewport_frame.winfo_height()+20)

        self.app.update()
        self.messageBox = tk.Listbox(self.messageBox_frame, width=72, height=8)
        self.messageBox.place(x=10, y=10)


    def add_menu(self):
        self.app.update()
        self.menu_frame = Frame(self.app, 300, self.app.winfo_height()-20)
        self.menu_frame.place(x=10, y=10)

        self.app.update()
        self.add_object_menu()
        self.add_window_menu()

    def add_object_menu(self):
        self.object_menu_frame = Frame(self.menu_frame, self.menu_frame.winfo_width()-26, 180)
        self.object_menu_frame.place(x=10, y=10)

        Label(self.object_menu_frame, "Objects", 10).place(x=10, y=10)

        self.objects_listbox = tk.Listbox(self.object_menu_frame, width=26, height=5)
        self.objects_listbox.place(x=10, y=30)

        tk.Button(self.object_menu_frame, text="Add", command=self.add_object).place(x=45, y=135)
        tk.Button(self.object_menu_frame, text="Del", command=self.del_object).place(x=145, y=135)

    def add_object(self):
        NewObjWindow(self)

    def del_object(self):
        id = self.objects_listbox.curselection()[0]

        self.objects_listbox.delete(id)
        self.display_file.pop(id+2)

        self.update_viewport()

        self.add_message("Object Deleted")

    def add_window_menu(self):
        self.window_menu_frame = Frame(self.menu_frame, self.menu_frame.winfo_width()-26, 180)
        self.window_menu_frame.place(x=10, y=200)

        Label(self.window_menu_frame, "Window", 10).place(x=10, y=10)

        tk.Button(self.window_menu_frame, text="Up", command=self.move_window_up).place(x=40, y=40)
        tk.Button(self.window_menu_frame, text="Left", command=self.move_window_left).place(x=10, y=70)
        tk.Button(self.window_menu_frame, text="Right", command=self.move_window_right).place(x=62, y=70)
        tk.Button(self.window_menu_frame, text="Down", command=self.move_window_down).place(x=30, y=100)

        tk.Button(self.window_menu_frame, text="Zoom In", command=self.zoom_window_in).place(x=150, y=50)
        tk.Button(self.window_menu_frame, text="Zoom Out", command=self.zoom_window_out).place(x=150, y=90)

        tk.Button(self.window_menu_frame, text="Set Coord", command=self.set_window_coord).place(x=150, y=135)

        Label(self.window_menu_frame, "offset", 10).place(x=10, y=145)
        self.offset_var = tk.IntVar()
        self.offset_var.set(10)
        self.offset_entry = tk.Entry(self.window_menu_frame, textvariable=self.offset_var, width=4)
        self.offset_entry.place(x=50, y=140)


    def update_viewport(self):
        self.canvas.delete("all")

        for obj in self.display_file:
            self.draw_object(obj)


    def draw_object(self, obj: Object):

        transformed_coordinates = []
        for coord in obj.coordinates:
            transformed_coordinates.append(self.transform_coordinates(coord))

        if (len(transformed_coordinates) == 1):
            coord = transformed_coordinates[0]
            self.canvas.create_oval(coord[0], coord[1], coord[0], coord[1], fill=obj.color, width=5)

        else:
            for i in range(len(transformed_coordinates)-1):
                start_coord = transformed_coordinates[i]
                end_coord = transformed_coordinates[i+1]

                self.canvas.create_line(start_coord[0], start_coord[1], end_coord[0], end_coord[1], fill=obj.color, width=2)


    def add_point(self,name: str, color: str, coord: tuple[int, int]):
        point = Point(name, color, [coord])

        self.display_file.append(point)
        self.objects_listbox.insert(tk.END, "%s [%s - Point]" % (name, color))

        self.add_message("    - Coord:  (%d, %d)" % coord)
        self.add_message("    - Color:  %s" % color)
        self.add_message("    - Name:  %s" % name)
        self.add_message("Point added:")

        self.update_viewport()

    def add_line(self, name: str, color: str, start_coord: tuple[int, int], end_coord: tuple[int, int]):
        line = Line(name, color, [start_coord, end_coord])

        self.display_file.append(line)
        self.objects_listbox.insert(tk.END, "%s [%s - Line]" % (name, color))

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
        self.objects_listbox.insert(tk.END, "%s [%s - Wireframe]" % (name, color))

        coords = ""
        for v in coord_list: coords += "(%d, %d) " % v
        self.add_message("    - Coord:  %s" % coords)
        self.add_message("    - Color:  %s" % color)
        self.add_message("    - Name:  %s" % name)
        self.add_message("Wireframe added:")

        self.update_viewport()

    def set_window_coord(self):
        app = tk.Toplevel()
        app.title("Set Coordinates")
        app.geometry("180x150")

        Label(app, "Coordinates", 10).place(x=10, y=10)

        fm = Frame(app, width=160, height=50)
        fm.place(x=10, y=30)

        coord = (tk.IntVar(), tk.IntVar())

        Label(fm, "X:", 10).place(x=10, y=15)
        tk.Entry(fm, textvariable=coord[0], width=4).place(x=30, y=10)
        Label(fm, "Y:", 10).place(x=80, y=15)
        tk.Entry(fm, textvariable=coord[1], width=4).place(x=100, y=10)

        tk.Button(app, text="Set", command=lambda: self.set_window_coord_command((coord[0].get(), coord[1].get())) ).place(x=20, y=90)
        tk.Button(app, text="Cancel", command=app.destroy).place(x=80, y=90)

    def set_window_coord_command(self, coord: tuple[int, int]):
        self.add_message("Window coordinates seted to (%d, %d)" % (coord[0], coord[1]))

    def move_window_up(self):
        offset = self.offset_var.get()

        self.Wcoord_min = (self.Wcoord_min[0], self.Wcoord_min[1]+offset)
        self.Wcoord_max = (self.Wcoord_max[0], self.Wcoord_max[1]+offset)
        self.update_viewport()
        
        self.add_message("window moved up by %d" % offset)

    def move_window_down(self):
        offset = self.offset_var.get()

        self.Wcoord_min = (self.Wcoord_min[0], self.Wcoord_min[1]-offset)
        self.Wcoord_max = (self.Wcoord_max[0], self.Wcoord_max[1]-offset)
        self.update_viewport()

        self.add_message("window moved down by %d" % offset)

    def move_window_left(self):
        offset = self.offset_var.get()

        self.Wcoord_min = (self.Wcoord_min[0]-offset, self.Wcoord_min[1])
        self.Wcoord_max = (self.Wcoord_max[0]-offset, self.Wcoord_max[1])
        self.update_viewport()

        self.add_message("window moved left by %d" % offset)

    def move_window_right(self):
        offset = self.offset_var.get()

        self.Wcoord_min = (self.Wcoord_min[0]+offset, self.Wcoord_min[1])
        self.Wcoord_max = (self.Wcoord_max[0]+offset, self.Wcoord_max[1])
        self.update_viewport()

        self.add_message("window moved right by %d" % offset)

    def zoom_window_in(self):
        offset = self.offset_var.get()

        self.Wcoord_min = (self.Wcoord_min[0]+offset, self.Wcoord_min[1]+offset)
        self.Wcoord_max = (self.Wcoord_max[0]-offset, self.Wcoord_max[1]-offset)
        self.update_viewport()

        self.add_message("window zoomed in by %d" % offset)

    def zoom_window_out(self):
        offset = self.offset_var.get()

        self.Wcoord_min = (self.Wcoord_min[0]-offset, self.Wcoord_min[1]-offset)
        self.Wcoord_max = (self.Wcoord_max[0]+offset, self.Wcoord_max[1]+offset)
        self.update_viewport()

        self.add_message("window zoomed out by %d" % offset)

    def add_message(self, message: str):
        self.messageBox.insert(0, message)



sys = CGSystem()
sys.run()
