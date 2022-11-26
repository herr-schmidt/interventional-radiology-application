import customtkinter as ctk
import tkinter.font as tkFont
import pandas as pd
import enum

class FitCriterion(enum.Enum):
    FIT_HEADER = 0
    FIT_COL_MAX_LENGTH = 1
    DEFAULT = 2

class Table(ctk.CTkFrame):
    def __init__(self, master, data_frame: pd.DataFrame, header_height=30, row_height=20, fit_criterion=FitCriterion.DEFAULT, row_separator_width=0, column_separator_width=1):
        """Constructs a Table for displaying data.

        Args:
            master (_type_): _description_
            data_frame (pd.DataFrame): A pandas DataFrame on which the table is based.
            header_height (int, optional): Height of the table's header. Defaults to 30.
            row_height (int, optional): Height of each row in the table. Defaults to 20.
            column_width (int, optional): _description_. Defaults to 150.
            fit_header_labels (bool, optional): Columns are created wide enough to fit their respective label. Defaults to False.
            row_separator_width (int, optional): Width of row separators. Defaults to 1.
            column_separator_width (int, optional): Width of column separators. Defaults to 1.
        """
        super().__init__(master=master)

        self.horizontal_scrollbar = ctk.CTkScrollbar(master=self,
                                                     orientation=ctk.HORIZONTAL)
        self.vertical_scrollbar = ctk.CTkScrollbar(master=self,
                                                   orientation=ctk.VERTICAL)

        self.data_frame = data_frame
        self.header_font = tkFont.Font(family="Microsoft Tai Le", size=16, weight=tkFont.BOLD)
        self.font = tkFont.Font(family="Microsoft Tai Le", size=14)
        self.cell_text_left_offset = 2 #px

        self.rows = data_frame.shape[0]
        self.columns = data_frame.shape[1]
        self.header_height = header_height
        self.header_color = "#ffffff"
        self.separator_line_color = "gray75"
        self.row_height = row_height
        self.fit_criterion = fit_criterion
        self.default_column_width = 250
        self.column_widths = self.compute_column_widths()
        self.even_row_col = "#f2f2f2"
        self.odd_row_col = "#ffffff"


        self.row_separator_width = row_separator_width
        self.column_separator_width = column_separator_width

        self.table_canvas_width = sum(self.column_widths)
        self.table_canvas_height = self.rows * (row_height + self.row_separator_width)

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
        self.horizontal_scrollbar.command = self.horizontal_scroll

        self.draw_header()
        self.draw_header_text()
        self.draw_table()
        self.draw_table_text()
        self.bind_left_click()

    def compute_column_widths(self):
        if self.fit_criterion == FitCriterion.FIT_HEADER:
            return self.compute_header_column_widths()
        elif self.fit_criterion == FitCriterion.FIT_COL_MAX_LENGTH:
            return self.compute_table_column_widths()
        else:
            return [self.default_column_width] * self.columns

    # compute column widths in order to fit each one of the header's labels
    def compute_header_column_widths(self):
        column_widths = []
        columns_labels = self.data_frame.columns.values

        for label in columns_labels:
            text_width = self.header_font.measure(label) + self.cell_text_left_offset
            column_widths.append(text_width)

        return column_widths

    # compute column widths in order to fit the longest entry in each column
    def compute_table_column_widths(self):
        column_widths = []
        columns_labels = self.data_frame.columns.values

        for label in columns_labels:
            column_values = data_frame[label].values
            column_values_pixels = map(lambda e: self.font.measure(e) + self.cell_text_left_offset, column_values)
            column_widths.append(max(column_values_pixels))

        return column_widths





 
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

    def draw_header_text(self):
        y = self.row_separator_width + self.header_height / 2
        x = self.cell_text_left_offset
        for column in range(0, self.columns):
            text = self.data_frame.columns.values[column]
            max_displayable_text = self.compute_max_displayable(text, column, header=True)
            self.header_canvas.create_text((x, y), text=max_displayable_text, font=self.header_font, anchor=ctk.W)
            x = x + self.column_widths[column]

    def draw_table(self):
        y = 0
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

    def draw_table_text(self):
        
        y = self.row_separator_width + self.row_height / 2
        for row in range(0, self.rows):
            x = self.cell_text_left_offset
            row_elements = self.data_frame.iloc[row].values
            for column in range(0, self.columns):
                text = row_elements[column]
                max_displayable_text = self.compute_max_displayable(text, column)
                self.table_canvas.create_text((x, y), text=max_displayable_text, font=self.font, anchor=ctk.W)
                x = x + self.column_widths[column]
            y = y + self.row_height + self.row_separator_width

    def compute_max_displayable(self, text, column, header=False):
        if header:
            font = self.header_font
        else:
            font = self.font
        text_width = font.measure(text)
        text_height = self.font.metrics("linespace")

        while text_width > self.column_widths[column] - self.cell_text_left_offset: 
            text = text[:-1] # remove last char
            text_width = font.measure(text)
        return text
        


    def bind_left_click(self):
        self.table_canvas.bind("<Button-1>", func=self.on_left_click)

    def bind_vertical_scroll(self):
        self.table_canvas.bind("<MouseWheel>", func=self.table_canvas.yview, add="+")

    # get cell
    def on_left_click(self, event):
        row = 0
        column = 0

        vertical_scrollbar_offset = self.table_canvas.winfo_reqheight() * self.vertical_scrollbar.get()[0]
        horizontal_scrollbar_offset = self.table_canvas.winfo_reqwidth() * self.horizontal_scrollbar.get()[0]

        y = 0
        x = 0
        while y < event.y + vertical_scrollbar_offset:
            y += self.row_height + self.row_separator_width
            row += 1
        while x < event.x + horizontal_scrollbar_offset:
            x += self.column_widths[column]
            column += 1

        print(str((row, column)) + " " + str(self.vertical_scrollbar.get()))

    # both the header and the table must scroll simultaneously along the x-axis
    def horizontal_scroll(self, *args):
        self.header_canvas.xview(*args)
        self.table_canvas.xview(*args)

    def pack(self, **kwargs):
        self.horizontal_scrollbar.pack(side=ctk.BOTTOM,
                                       expand=False,
                                       fill=ctk.X)
        self.vertical_scrollbar.pack(side=ctk.RIGHT,
                                     expand=False,
                                     fill=ctk.Y)
        self.header_canvas.pack(side=ctk.TOP, expand=True, fill=ctk.Y)
        self.table_canvas.pack(side=ctk.TOP, expand=True, fill=ctk.Y)

        ctk.CTkFrame.pack(self, **kwargs)



data_dict = {'Ciaoooooooooo1': ["hello", "hello!", "HELLO!", "hello", "hello!", "HELLO!", "hello", "hello!", "HELLO!", "hello", "hello!", "HELLO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo2': ["ciaooooooooooooooooooooooo", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo3': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo4': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo5': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo6': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo7': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo8': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo9': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo10': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo101': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo102': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo103': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo104': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo105': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo106': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo10sd': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo10g': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo10d': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],
 'Ciaoooooooooo11': ["ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciao", "ciao!", "CIAO!", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo", "ciaooooooooooo"],}
data_frame = pd.DataFrame(data=data_dict)


root = ctk.CTk()
root.title("Fancy table")

table = Table(master=root, data_frame=data_frame, row_height=70, header_height=90, fit_criterion=FitCriterion.FIT_COL_MAX_LENGTH)
table.pack(expand=False, fill=ctk.BOTH)

root.mainloop()
