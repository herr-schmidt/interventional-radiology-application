import sys
import threading
from tkinter import *
from tkinter.ttk import *

from click import command


class StdoutRedirector(object):
    def __init__(self, textWidget):
        self.textSpace = textWidget

    def write(self, string):
        self.textSpace.insert("end", string)
        self.textSpace.see("end")

    def flush(self):
        pass


class GUI(object):
    def __init__(self, master):
        self.master = master

        # notebooks and command panel
        self.upper_frame = Frame(master=self.master)
        self.upper_frame.pack(side=TOP)
        
        # log output
        self.lower_frame = Frame(master=self.master)
        self.lower_frame.pack(side=BOTTOM)

        self.initializeUI()

    def initializeUI(self):
        self.create_upper_menus()
        self.create_notebooks()
        self.create_command_panel()
        self.create_log_text_box()

    def create_command_panel(self):
        self.buttons_frame = Labelframe(master=self.upper_frame, text="", width=100)
        self.buttons_frame.pack(side=RIGHT, fill=BOTH, anchor=E, padx=10)

        self.test_button = Button(master=self.buttons_frame,
                                  width=12,
                                  text="Test")
        self.test_button.pack(padx=10)

    def create_upper_menus(self):
        menu = Menu(self.master)
        self.master.config(menu=menu)

        file_menu = Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menu)
        menu.add_cascade(label="Edit", menu=edit_menu)

    def create_notebooks(self):
        self.notebook_frame = Frame(self.upper_frame)
        self.notebook_frame.pack(side=LEFT, fill=X, anchor=W, padx=10)

        notebook = Notebook(self.notebook_frame)
        notebook.pack(pady=10, side=TOP, expand=True, fill=BOTH, padx=10)

        tab_1 = Frame(notebook, width=900, height=500)
        tab_2 = Frame(notebook, width=900, height=500)

        tab_1.pack(fill=BOTH, expand=True)
        tab_2.pack(fill=BOTH, expand=True)

        notebook.add(tab_1, text='Tab 1')
        notebook.add(tab_2, text='Tab 2')

    def create_log_text_box(self):
        self.output_frame = Frame(master=self.lower_frame)
        self.output_frame.pack(fill=BOTH)

        self.scroll_bar = Scrollbar(self.output_frame)
        self.scroll_bar.pack(side=RIGHT, fill=Y)

        self.text_box = Text(master=self.output_frame, width=50, height=16)
        self.text_box.pack(fill=X)
        self.text_box.config(background="#000000", fg="#ffffff")
        # to correctly resize the scroll bar
        self.text_box.config(yscrollcommand=self.scroll_bar.set)

        self.scroll_bar.config(command=self.text_box.yview)

        sys.stdout = StdoutRedirector(self.text_box)


ws = Tk()
ws.title("Interventional Radiology Planner & Scheduler")

# Create a style
style = Style(ws)

# Set the theme with the theme_use method
style.theme_use('winnative')  # put the theme name here, that you want to use

gui = GUI(ws)

ws.mainloop()
