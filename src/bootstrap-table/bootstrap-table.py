import customtkinter as ctk
import tkinter.font as tkFont
import pandas as pd
import enum

class FitCriterion(enum.Enum):
    DEFAULT = 0
    FIT_COL_MAX_LENGTH = 1
    FIT_HEADER = 2
    FIT_HEADER_AND_COL_MAX_LENGTH = 3

class Background(enum.Enum):
    DEFAULT = 0
    SELECT = 1
    HOVER = 2

class Table(ctk.CTkFrame):

    ROW_TAG_PREFIX = "row_"

    def __init__(self, master, data_frame: pd.DataFrame, header_height=30, row_height=20, fit_criterion=FitCriterion.DEFAULT, row_separator_width=1, column_separator_width=1):
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
        self.header_font = tkFont.Font(family="Microsoft Tai Le", size=14, weight=tkFont.BOLD)
        self.font = tkFont.Font(family="Microsoft Tai Le", size=12)
        self.cell_text_left_offset = 6 #px

        self.hover_row = None
        self.hover_row_color = "#e3f5ff"

        self.selected_row = None
        self.selected_row_color = "#e3ffe6"

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
                                           scrollregion=(0, 0, self.table_canvas_width, 0),
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
        self.do_bindings()

    def do_bindings(self):
        self.table_canvas.bind("<Button-1>", func=self.on_left_click)
        self.table_canvas.bind("<Motion>", func=self.on_hover)
        self.table_canvas.bind("<Leave>", func=self.on_leave)

    def compute_column_widths(self):
        if self.fit_criterion == FitCriterion.FIT_HEADER:
            return self.compute_header_column_widths()
        elif self.fit_criterion == FitCriterion.FIT_COL_MAX_LENGTH:
            return self.compute_table_column_widths()
        elif self.fit_criterion == FitCriterion.FIT_HEADER_AND_COL_MAX_LENGTH:
            header_column_widths = self.compute_header_column_widths()
            entries_column_widths = self.compute_table_column_widths()
            
            comparison = zip(header_column_widths, entries_column_widths)
            return list(map(lambda e: max(e), comparison))
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
    # if column label is shorter, it will be truncated
    def compute_table_column_widths(self):
        column_widths = []
        columns_labels = self.data_frame.columns.values

        for label in columns_labels:
            column_values = self.data_frame[label].values
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
        for row in range(0, self.rows):
            self.draw_row(row)

    def draw_row(self, row, background_type=Background.DEFAULT):
        # delete by tag all objects associated to row, if they exist
        # this prevents Tkinter from having to keep track of too many useless objects for the same row
        row_tag = self.ROW_TAG_PREFIX + str(row)
        self.table_canvas.delete(row_tag)

        self.draw_row_background(row, background_type)
        self.draw_row_text(row)

    def draw_row_background(self, row, background_type):
        row_tag = self.ROW_TAG_PREFIX + str(row)
        y = row * (self.row_height + self.row_separator_width)
        self.table_canvas.create_rectangle(0, y,
                                               self.table_canvas.winfo_reqwidth(), y + self.row_separator_width,
                                               width=0,
                                               fill=self.separator_line_color,
                                               tags=row_tag)

        y += self.row_separator_width

        if background_type == Background.HOVER:
            color = self.hover_row_color
        elif background_type == Background.SELECT:
            color = self.selected_row_color
        elif row % 2 == 0:
            color = self.even_row_col
        else:
            color = self.odd_row_col

        self.table_canvas.create_rectangle(0, y,
                                            self.table_canvas.winfo_reqwidth(), y + self.row_height,
                                            fill=color,
                                            width=0,
                                            tags=row_tag)

    def draw_table_text(self):
        for row in range(0, self.rows):
            self.draw_row_text(row)

    def draw_row_text(self, row):
        row_tag = self.ROW_TAG_PREFIX + str(row)

        y = (self.row_separator_width + self.row_height / 2) + (self.row_height + self.row_separator_width) * row
        x = self.cell_text_left_offset
        row_elements = self.data_frame.iloc[row].values
        for column in range(0, self.columns):
            text = row_elements[column]
            max_displayable_text = self.compute_max_displayable(text, column)
            self.table_canvas.create_text((x, y), text=max_displayable_text, font=self.font, anchor=ctk.W, tags=row_tag)
            x = x + self.column_widths[column]

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

    def on_leave(self, event):
        if self.hover_row == self.selected_row:
            self.hover_row = None
            return
        if self.hover_row is not None:
            self.draw_row(self.hover_row, background_type=Background.DEFAULT)
            self.hover_row = None
        

    def on_hover(self, event):
        hover_row = self.get_cell(event)[0]
        previously_hovered_row = self.hover_row

        if hover_row == previously_hovered_row:
            return
        if hover_row == self.selected_row and previously_hovered_row is not None:
            self.draw_row(previously_hovered_row, background_type=Background.DEFAULT)
            return
        if hover_row == self.selected_row and previously_hovered_row is None:
            return

        self.draw_row(hover_row, background_type=Background.HOVER)

        if previously_hovered_row is not None and previously_hovered_row != self.selected_row:
            self.draw_row(previously_hovered_row, background_type=Background.DEFAULT)

        self.hover_row = hover_row

    def on_left_click(self, event):
        new_selected_row = self.get_cell(event)[0]

        if self.selected_row is None:
            self.draw_row(new_selected_row, background_type=Background.SELECT)
            self.selected_row = new_selected_row
        elif self.selected_row != new_selected_row: # switch to the newly selected row
            self.draw_row(self.selected_row, background_type=Background.DEFAULT)

            self.draw_row(new_selected_row, background_type=Background.SELECT)
            self.selected_row = new_selected_row
        else: # click on already selected row: deselect row
            self.draw_row(new_selected_row, background_type=Background.HOVER)
            self.selected_row = None

    def get_cell(self, event):
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

        return (row - 1, column - 1)

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
                                     fill=ctk.Y
                                     )
        self.header_canvas.pack(side=ctk.TOP, expand=False, fill=ctk.Y)
        self.table_canvas.pack(side=ctk.TOP, expand=False, fill=ctk.Y)

        ctk.CTkFrame.pack(self, **kwargs)

        self.update_idletasks()


data_dict = {"Colonna 1" : ["Mario", "Marco", "Giovanni"],
             "Colonna 3" : ["Mario", "Marco", "Giovanni"],
             "Colonna 4" : ["Mario", "Marco", "Giovanni"],
             "Colonna 5" : ["Mario", "Marco", "Giovanni"],
             "Colonna 6" : ["Mario", "Marco", "Giovanni"],
             "Colonna 7" : ["Mario", "Marco", "Giovanni"],
             "Colonna 8" : ["Mario", "Marco", "Giovanni"],}
data_frame = pd.DataFrame(data=data_dict)


root = ctk.CTk()
root.title("Fancy table")

table = Table(master=root,
 data_frame=data_frame,
  row_height=30,
   header_height=40,
    fit_criterion=FitCriterion.FIT_HEADER_AND_COL_MAX_LENGTH,
    row_separator_width=0)
table.pack()

root.mainloop()
