import customtkinter as ctk


class Table(ctk.CTkFrame):
    def __init__(self, master, rows, columns, header_height=30, row_height=20, column_width=150, row_separator_width=2, column_separator_width=1):
        super().__init__(master=master)

        self.horizontal_scrollbar = ctk.CTkScrollbar(master=self,
                                                     orientation=ctk.HORIZONTAL)
        self.vertical_scrollbar = ctk.CTkScrollbar(master=self,
                                                   orientation=ctk.VERTICAL)

        self.rows = rows
        self.header_height = header_height
        self.header_color = "#ffffff"
        self.separator_line_color = "gray75"
        self.row_height = row_height
        self.column_width = column_width
        self.even_row_col = "#f2f2f2"
        self.odd_row_col = "#ffffff"

        self.row_separator_width = row_separator_width
        self.column_separator_width = column_separator_width

        self.table_canvas_width = columns * column_width
        self.table_canvas_height = rows * (row_height + self.row_separator_width) + header_height + 2 * self.row_separator_width

        self.header_canvas = ctk.CTkCanvas(master=self,
                                           xscrollcommand=self.horizontal_scrollbar.set,
                                           width=self.table_canvas_width,
                                           height=self.header_height + 2 * self.row_separator_width,
                                           scrollregion=(0, 0, self.table_canvas_width, self.header_height + 2 * self.row_separator_width),
                                           borderwidth=0,
                                           highlightthickness=0
                                           )

        self.table_canvas = ctk.CTkCanvas(master=self,
                                          xscrollcommand=self.horizontal_scrollbar.set,
                                          yscrollcommand=self.vertical_scrollbar.set,
                                          width=self.table_canvas_width,
                                          height=self.table_canvas_height,
                                          scrollregion=(0, 0, self.table_canvas_width, self.table_canvas_height),
                                          borderwidth=0,
                                          highlightthickness=0,
                                          # yscrollincrement=3
                                          )

        self.vertical_scrollbar.command = self.table_canvas.yview
        self.horizontal_scrollbar.command = self.table_canvas.xview

        self.draw_header()
        self.draw_table()
        self.bind_left_click()
 
    def draw_header(self):
        self.header_canvas.create_rectangle(0, 0,
                                           self.table_canvas.winfo_reqwidth(), self.row_separator_width,
                                           width=0, fill=self.separator_line_color)

        y = self.row_separator_width
        self.header_canvas.create_rectangle(0, y,
                                           self.table_canvas.winfo_reqwidth(), y + self.header_height,
                                           fill=self.header_color,
                                           width=0)

        y += self.header_height
        self.header_canvas.create_rectangle(0, y,
                                      self.table_canvas.winfo_reqwidth(), y + self.row_separator_width,
                                      width=0, fill=self.separator_line_color)

    def draw_table(self):

        y = 0  # self.header_height + 2 * self.row_separator_width + 1
        for i in range(0, self.rows):

            self.table_canvas.create_rectangle(0, y,
                                               self.table_canvas.winfo_reqwidth(), y + self.row_separator_width,
                                               width=0,
                                               fill=self.separator_line_color)

            y += self.row_separator_width

            if i % 2 == 0:
                color = self.even_row_col
            else:
                color = self.odd_row_col
            self.table_canvas.create_rectangle(0, y,
                                               self.table_canvas.winfo_reqwidth(), y + self.row_height,
                                               fill=color,
                                               width=0)
            y += self.row_height

        # TODO: draw columns

    def bind_left_click(self):
        self.table_canvas.bind("<Button-1>", func=self.on_left_click)

    # get cell
    def on_left_click(self, event):
        row = 0
        column = 0

        vertical_scrollbar_offset = self.table_canvas.winfo_reqheight() * self.vertical_scrollbar.get()[0]

        y = 0 # self.header_height + 2 * self.row_separator_width
        x = 0
        while y < event.y + vertical_scrollbar_offset:
            y += self.row_height + self.row_separator_width
            row += 1
        while x < event.x:
            x += self.column_width
            column += 1

        print(str((row, column)) + " " + str(self.vertical_scrollbar.get()))

    def pack(self, **kwargs):
        self.horizontal_scrollbar.pack(side=ctk.BOTTOM,
                                       expand=False,
                                       fill=ctk.X)
        self.vertical_scrollbar.pack(side=ctk.RIGHT,
                                     expand=False,
                                     fill=ctk.Y)
        self.header_canvas.pack(side=ctk.TOP, expand=True, fill=ctk.BOTH)
        self.table_canvas.pack(expand=True, fill=ctk.BOTH)

        ctk.CTkFrame.pack(self, **kwargs)


root = ctk.CTk()
root.title("Fancy table")

table = Table(master=root, rows=60, columns=6, row_height=20, header_height=40)
table.pack(expand=True, fill=ctk.BOTH)

root.mainloop()
