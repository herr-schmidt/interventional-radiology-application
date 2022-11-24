import customtkinter as ctk


class Table(ctk.CTkFrame):
    def __init__(self, master, rows, columns, header_height=30, column_height=20, column_width=150):
        super().__init__(master=master)

        self.horizontal_scrollbar = ctk.CTkScrollbar(master=self,
                                                     orientation=ctk.HORIZONTAL)
        self.vertical_scrollbar = ctk.CTkScrollbar(master=self,
                                                   orientation=ctk.VERTICAL)
        self.canvas = ctk.CTkCanvas(master=self,
                                    xscrollcommand=self.horizontal_scrollbar.set,
                                    yscrollcommand=self.vertical_scrollbar.set,
                                    width=columns * column_width,
                                    height=rows * column_height + header_height,
                                    scrollregion=(0, 0, columns * column_width, rows * column_height + header_height),
                                    borderwidth=0,
                                    highlightthickness=0)

        self.vertical_scrollbar.command = self.canvas.yview
        self.horizontal_scrollbar.command = self.canvas.xview

        self.rows = rows
        self.header_height = header_height
        self.header_color = "#ffffff"
        self.separator_line_color = "gray75"
        self.column_height = column_height
        self.even_row_col = "#f2f2f2"
        self.odd_row_col = "#ffffff"
        self.draw_table()

    def draw_table(self):

        self.draw_header()

        y = self.header_height + 3
        for i in range(0, self.rows):

            self.canvas.create_line(0, y,
                                self.canvas.winfo_reqwidth(), y,
                                width=1, fill=self.separator_line_color)

            if i % 2 == 0:
                color = self.even_row_col
            else:
                color = self.odd_row_col
            self.canvas.create_rectangle(0, y + 1,
                                         self.canvas.winfo_reqwidth(), y + self.column_height + 1,
                                         fill=color,
                                         width=0)
            y += self.column_height

        # TODO: draw columns

    def draw_header(self):
        self.canvas.create_line(0, 0,
                                self.canvas.winfo_reqwidth(), 0,
                                width=1, fill=self.separator_line_color)

        y = 1
        self.canvas.create_rectangle(0, y,
                                     self.canvas.winfo_reqwidth(), y + self.header_height + 1,
                                     fill=self.header_color,
                                     width=0)

        self.canvas.create_line(0, y + self.header_height + 1,
                                self.canvas.winfo_reqwidth(), y + self.header_height + 1,
                                width=1, fill=self.separator_line_color)


    def pack(self, **kwargs):
        self.horizontal_scrollbar.pack(side=ctk.BOTTOM,
                                       expand=False,
                                       fill=ctk.X)
        self.vertical_scrollbar.pack(side=ctk.RIGHT,
                                     expand=False,
                                     fill=ctk.Y)
        self.canvas.pack(expand=True, fill=ctk.BOTH)

        ctk.CTkFrame.pack(self, **kwargs)

        #self.create_line(0, 0, self.winfo_width(), 0, width=1, fill=self.separator_line_color)
#
        #y = 1
        # for i in range(0, rows):
        #    if i % 2 == 0:
        #        color = even_row_col
        #    else:
        #        color = odd_row_col
        #    self.create_rectangle(0, y, self.winfo_width(),
        #                          y + col_height, fill=color, width=0)
        #    y += col_height
        # self.update()
        ## self.create_text(20,20, text="Hello!")


root = ctk.CTk()
root.title("Fancy table")

table = Table(master=root, rows=60, columns=6, column_height=20, header_height=20)
table.pack(expand=True, fill=ctk.BOTH)

root.mainloop()
