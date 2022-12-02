import ctypes
from PIL import Image
import tkinter as tk
import customtkinter as ctk
import tkinter.font as tkFont
import pandas as pd
import enum
from math import ceil, floor

class FitCriterion(enum.Enum):
    DEFAULT = 0
    FIT_COL_MAX_LENGTH = 1
    FIT_HEADER = 2
    FIT_HEADER_AND_COL_MAX_LENGTH = 3


class Background(enum.Enum):
    DEFAULT = 0
    SELECT = 1
    HOVER = 2


class Table(tk.Frame):

    ROW_TAG_PREFIX = "row_"
    EMPTY_SPACE_TAG_PREFIX = "empty_"
    FOOTER_SEPARATOR_TAG_PREFIX = "footer_"

    def __init__(self, master, width, data_frame: pd.DataFrame, header_height=30, row_height=20, fit_criterion=FitCriterion.DEFAULT, footer_height=50, footer_separator_width=1, row_separator_width=1, column_separator_width=0, pagination_size=5):
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
        super().__init__(master=master, width=width)

        self.horizontal_scrollbar = tk.Scrollbar(master=self,
                                                     orient=ctk.HORIZONTAL)
        self.vertical_scrollbar = tk.Scrollbar(master=self,
                                                   orient=ctk.VERTICAL)

        self.data_frame = data_frame
        self.header_font = tkFont.Font(family="Microsoft Tai Le Bold", size=12)
        self.font = tkFont.Font(family="Microsoft Tai Le", size=12)
        self.page_label_font = tkFont.Font(family="Microsoft Tai Le", size=10)
        self.cell_text_left_offset = 6 # px

        self.hover_row = None
        self.hover_row_color = "#e3f5ff"

        self.selected_row = None
        self.selected_row_color = "#e3ffe6"

        self.rows = data_frame.shape[0]
        self.columns = data_frame.shape[1]
        self.pagination_size = pagination_size
        self.current_page = 0
        self.current_page_label_var = tk.IntVar()
        self.current_page_label_var.initialize(1)
        self.header_height = header_height
        self.header_color = "#ffffff"
        self.separator_line_color = "gray75"
        self.row_height = row_height
        self.fit_criterion = fit_criterion
        self.default_column_width = 250
        self.column_widths = self.compute_column_widths()
        self.even_row_col = "#f2f2f2"
        self.odd_row_col = "#ffffff"

        self.footer_separator_width = footer_separator_width
        self.footer_height = footer_height

        self.row_separator_width = row_separator_width
        self.column_separator_width = column_separator_width

        self.table_canvas_width = sum(self.column_widths)
        self.table_canvas_height = self.compute_canvas_height()

        self.header_canvas = tk.Canvas(master=self,
                                           xscrollcommand=self.horizontal_scrollbar.set,
                                           width=self.table_canvas_width,
                                           height=self.header_height + 2 * self.row_separator_width,
                                           scrollregion=(0, 0, self.table_canvas_width, 0),
                                           borderwidth=0,
                                           highlightthickness=0
                                           )

        self.table_canvas = tk.Canvas(master=self,
                                          xscrollcommand=self.horizontal_scrollbar.set,
                                          yscrollcommand=self.vertical_scrollbar.set,
                                          width=self.table_canvas_width,
                                          height=self.table_canvas_height,
                                          scrollregion=(0, 0, self.table_canvas_width, self.table_canvas_height),
                                          borderwidth=0,
                                          highlightthickness=0,
                                          # yscrollincrement=3
                                          )

        self.footer = tk.Frame(master=self,
                                                width=self.table_canvas_width,
                                                height=self.footer_height,
                                                background=self.header_color
                                                )

        self.navigation_buttons_color = "#ffffff"
        self.navigation_buttons_hover_color = "gray95"


        next_icon = ctk.CTkImage(Image.open("resources/next_b.png"))
        prev_icon =ctk.CTkImage(Image.open("resources/prev_b.png"))
        first_icon = ctk.CTkImage(Image.open("resources/first_b.png"))
        last_icon = ctk.CTkImage(Image.open("resources/last_b.png"))

        self.next_page_button = ctk.CTkButton(master=self.footer,
                                              text="",
                                              image=next_icon,
                                              fg_color=self.navigation_buttons_color,
                                              hover_color=self.navigation_buttons_hover_color,
                                              width=32,
                                              height=32,
                                              command=self.next_page)
        self.previous_page_button = ctk.CTkButton(master=self.footer,
                                                  text="",
                                                  image=prev_icon,
                                                  fg_color=self.navigation_buttons_color,
                                                  hover_color=self.navigation_buttons_hover_color,
                                                  width=32,
                                                  height=32,
                                                  command=self.previous_page)
        self.first_page_button = ctk.CTkButton(master=self.footer,
                                              text="",
                                              image=first_icon,
                                              fg_color=self.navigation_buttons_color,
                                              hover_color=self.navigation_buttons_hover_color,
                                              width=32,
                                              height=32,
                                              command=self.first_page)
        self.last_page_button = ctk.CTkButton(master=self.footer,
                                              text="",
                                              image=last_icon,
                                              fg_color=self.navigation_buttons_color,
                                              hover_color=self.navigation_buttons_hover_color,
                                              width=32,
                                              height=32,
                                              command=self.last_page)

        self.page_number_label = tk.Label(master=self.footer,
                                              textvariable=self.current_page_label_var,
                                              width=5, #chars
                                              font=self.page_label_font,
                                              background=self.header_color)
                                              # border_color="gray75",
                                              # border_width=1)

        # self.pagination_combo_text = ctk.StringVar()
        # self.pagination_combo_text.initialize(str(self.pagination_size))
        # 
        # self.pagination_combo = ctk.CTkComboBox(master=self.footer,
        #                                         variable=self.pagination_combo_text,
        #                                         values=["5", "10", "25", "50", "100"],
        #                                         border_width=1,
        #                                         height=50,
        #                                         fg_color=self.header_color,
        #                                         bg_color=self.header_color,
        #                                         border_color=self.header_color,
        #                                         button_color=self.header_color,
        #                                         button_hover_color=self.navigation_buttons_hover_color
        #                                         )

        self.vertical_scrollbar.config(command=self.table_canvas.yview)
        self.horizontal_scrollbar.config(command=self.horizontal_scroll)

        self.draw_header()
        self.draw_header_text()
        self.draw_table()
        self.do_bindings()

    def do_bindings(self):
        self.table_canvas.bind("<Button-1>", func=self.on_left_click)
        self.table_canvas.bind("<Motion>", func=self.on_hover)
        self.table_canvas.bind("<Leave>", func=self.on_leave)

        self.bind("<Configure>", func=self.on_resize)

    def on_resize(self, event):
        self.update_idletasks()
        self.pack_vertical_scrollbar()
        self.pack_horizontal_scrollbar()

    def pack_vertical_scrollbar(self):
        page_height = self.pagination_size * (self.row_height + self.row_separator_width)
        if self.table_canvas.winfo_height() >= page_height:
            self.vertical_scrollbar.pack_forget()
        else:
            self.vertical_scrollbar.pack(side=tk.RIGHT, expand=False, fill=tk.Y, before=self.header_canvas)

    def pack_horizontal_scrollbar(self):
        page_width = sum(self.column_widths) + self.columns * self.column_separator_width
        if self.header_canvas.winfo_width() >= page_width:
            self.horizontal_scrollbar.pack_forget()
        else:
            self.horizontal_scrollbar.pack(side=tk.BOTTOM,
                                       expand=False,
                                       fill=tk.X,
                                       before=self.footer)

    def first_page(self):
        self.current_page = 0
        self.current_page_label_var.set(self.current_page + 1)
        self.table_canvas.delete("all")
        self.selected_row = None
        self.hover_row = None
        self.draw_table()

    def last_page(self):
        self.current_page = self.compute_last_page_index()
        self.current_page_label_var.set(self.current_page + 1)
        self.table_canvas.delete("all")
        self.selected_row = None
        self.hover_row = None
        self.draw_table()

    def compute_last_page_index(self):
        return ceil(self.rows / self.pagination_size) - 1

    def next_page(self):
        if self.current_page == self.compute_last_page_index():
            return
        self.current_page += 1
        self.current_page_label_var.set(self.current_page + 1)
        self.table_canvas.delete("all")
        self.selected_row = None
        self.hover_row = None
        self.draw_table()

    def previous_page(self):
        if self.current_page == 0:
            return
        self.current_page -= 1
        self.current_page_label_var.set(self.current_page + 1)
        self.table_canvas.delete("all")
        self.selected_row = None
        self.hover_row = None
        self.draw_table()

    def compute_canvas_height(self):
        df_rows = self.get_current_page_rows()

        return len(df_rows) * (self.row_height + self.row_separator_width) + self.footer_separator_width

    def compute_column_widths(self):
        column_widths = []

        if self.fit_criterion == FitCriterion.FIT_HEADER:
            column_widths = self.compute_header_column_widths()
        elif self.fit_criterion == FitCriterion.FIT_COL_MAX_LENGTH:
            column_widths = self.compute_table_column_widths()
        elif self.fit_criterion == FitCriterion.FIT_HEADER_AND_COL_MAX_LENGTH:
            header_column_widths = self.compute_header_column_widths()
            entries_column_widths = self.compute_table_column_widths()

            comparison = zip(header_column_widths, entries_column_widths)
            column_widths = list(map(lambda e: max(e), comparison))
        else:
            column_widths = [self.default_column_width] * self.columns

        self.update_idletasks()
        requested_width = self.winfo_reqwidth()
        available_width = requested_width - sum(column_widths)
        
        if available_width > 0:
            pad = floor(available_width / self.columns)
        else:
            pad = 0

        return [col + pad for col in column_widths]

    # compute column widths in order to fit each one of the header's labels
    def compute_header_column_widths(self):
        column_widths = []
        columns_labels = self.data_frame.columns.values

        for label in columns_labels:
            text_width = self.header_font.measure(
                label) + self.cell_text_left_offset
            column_widths.append(text_width)

        return column_widths

    # compute column widths in order to fit the longest entry in each column
    # if column label is shorter, it will be truncated
    def compute_table_column_widths(self):
        column_widths = []
        columns_labels = self.data_frame.columns.values

        # no data in dataframe
        if self.data_frame.size == 0:
            return [0] * self.columns

        for label in columns_labels:
            column_values = self.data_frame[label].values
            column_values_pixels = map(lambda e: self.font.measure(
                e) + self.cell_text_left_offset, column_values)
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
            max_displayable_text = self.compute_max_displayable(
                text, column, header=True)
            self.header_canvas.create_text(
                (x, y), text=max_displayable_text, font=self.header_font, anchor=tk.W)
            x = x + self.column_widths[column]

    def get_current_page_rows(self):
        first_row = self.current_page * self.pagination_size
        last_row = self.pagination_size * (self.current_page + 1)

        return self.data_frame[first_row:last_row].values

    def draw_table(self):
        df_rows = self.get_current_page_rows()
        for absolute_row in range(self.current_page * self.pagination_size, self.current_page * self.pagination_size + len(df_rows)):
            self.draw_row(absolute_row)

        # fill empty space with default background
        if len(df_rows) < self.pagination_size:
            self.fill_empty_space(len(df_rows))

        self.draw_footer_separator()

    def draw_footer_separator(self):
        footer_separator_tag = self.FOOTER_SEPARATOR_TAG_PREFIX
        self.table_canvas.delete(footer_separator_tag)

        y = (self.row_separator_width + self.row_height) * self.pagination_size
        y_bottom = (self.row_separator_width + self.row_height) * self.pagination_size + self.footer_separator_width

        self.table_canvas.create_rectangle(0, y,
                                           self.table_canvas.winfo_reqwidth(), y + y_bottom,
                                           width=0,
                                           fill=self.separator_line_color,
                                           tags=footer_separator_tag)

    def fill_empty_space(self, last_page_rows):
        empty_space_tag = self.EMPTY_SPACE_TAG_PREFIX
        self.table_canvas.delete(empty_space_tag)

        y = (self.row_separator_width + self.row_height) * last_page_rows
        y_bottom = (self.row_separator_width + self.row_height) * self.pagination_size

        self.table_canvas.create_rectangle(0, y,
                                           self.table_canvas.winfo_reqwidth(), y + y_bottom,
                                           width=0,
                                           fill=self.header_color,
                                           tags=empty_space_tag)


    def draw_row(self, absolute_row, background_type=Background.DEFAULT):
        # delete by tag all objects associated to row, if they exist
        # this prevents Tkinter from having to keep track of too many useless objects for the same row
        row_tag = self.ROW_TAG_PREFIX + str(absolute_row)
        self.table_canvas.delete(row_tag)

        self.draw_row_background(absolute_row, background_type)
        self.draw_row_text(absolute_row)

    def draw_row_background(self, absolute_row, background_type):
        row_tag = self.ROW_TAG_PREFIX + str(absolute_row)
        relative_row = absolute_row % self.pagination_size
        y = relative_row * (self.row_height + self.row_separator_width)
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
        elif relative_row % 2 == 0:
            color = self.even_row_col
        else:
            color = self.odd_row_col

        self.table_canvas.create_rectangle(0, y,
                                           self.table_canvas.winfo_reqwidth(), y + self.row_height,
                                           fill=color,
                                           width=0,
                                           tags=row_tag)

    def draw_row_text(self, absolute_row):
        row_tag = self.ROW_TAG_PREFIX + str(absolute_row)
        relative_row = absolute_row % self.pagination_size

        y = (self.row_separator_width + self.row_height / 2) + \
            (self.row_height + self.row_separator_width) * relative_row
        x = self.cell_text_left_offset
        row_elements = self.data_frame.iloc[absolute_row].values
        for column in range(0, self.columns):
            text = row_elements[column]
            max_displayable_text = self.compute_max_displayable(text, column)
            self.table_canvas.create_text(
                (x, y), text=max_displayable_text, font=self.font, anchor=tk.W, tags=row_tag)
            x = x + self.column_widths[column]

    def compute_max_displayable(self, text, column, header=False):
        if header:
            font = self.header_font
        else:
            font = self.font
        text_width = font.measure(text)
        text_height = self.font.metrics("linespace")

        while text_width > self.column_widths[column] - self.cell_text_left_offset:
            text = text[:-1]  # remove last char
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
        hover_row = self.get_cell(event)[0] + self.current_page * self.pagination_size
        previously_hovered_row = self.hover_row

        # when on last page we do not want to hover on a non-existing line (empty space)
        if hover_row >= self.data_frame.shape[0]:
            return

        if hover_row == previously_hovered_row:
            return
        if hover_row == self.selected_row and previously_hovered_row is not None:
            self.draw_row(previously_hovered_row, background_type=Background.DEFAULT)
            return
        if hover_row == self.selected_row and previously_hovered_row is None:
            return

        self.draw_row(hover_row, background_type=Background.HOVER)

        if previously_hovered_row is not None and previously_hovered_row != self.selected_row:
            self.draw_row(previously_hovered_row,
                          background_type=Background.DEFAULT)

        self.hover_row = hover_row

    def on_left_click(self, event):
        new_selected_row = self.get_cell(event)[0] + self.current_page * self.pagination_size

        # when on last page we do not want to select a non-existing line (empty space)
        if new_selected_row >= self.data_frame.shape[0]:
            return

        if self.selected_row is None:
            self.draw_row(new_selected_row, background_type=Background.SELECT)
            self.selected_row = new_selected_row
        elif self.selected_row != new_selected_row:  # switch to the newly selected row
            self.draw_row(self.selected_row,
                          background_type=Background.DEFAULT)

            self.draw_row(new_selected_row, background_type=Background.SELECT)
            self.selected_row = new_selected_row
        else:  # click on already selected row: deselect row
            self.draw_row(new_selected_row, background_type=Background.HOVER)
            self.selected_row = None

    def get_cell(self, event):
        row = 0
        column = 0

        vertical_scrollbar_offset = self.table_canvas.winfo_reqheight() * self.vertical_scrollbar.get()[0]
        horizontal_scrollbar_offset = self.table_canvas.winfo_reqwidth() * self.horizontal_scrollbar.get()[0]

        y = self.row_height + self.row_separator_width
        x = self.column_widths[column]

        while y < event.y + vertical_scrollbar_offset:
            y += self.row_height + self.row_separator_width
            row += 1
        while x < event.x + horizontal_scrollbar_offset:
            x += self.column_widths[column]
            column += 1

        return (row, column)

    # both the header and the table must scroll simultaneously along the x-axis
    def horizontal_scroll(self, *args):
        self.header_canvas.xview(*args)
        self.table_canvas.xview(*args)

    def pack(self, **kwargs):
        # self.horizontal_scrollbar.pack(side=ctk.BOTTOM,
        #                                expand=False,
        #                                fill=ctk.X)
        # self.vertical_scrollbar.pack(side=ctk.RIGHT,
        #                              expand=False,
        #                              fill=ctk.Y
        #                              )
        self.header_canvas.pack(side=tk.TOP, expand=False, fill=tk.Y)

        self.footer.pack(side=tk.BOTTOM, expand=False, fill=tk.X)

        self.last_page_button.pack(side=tk.RIGHT, anchor=tk.E, padx=(0, 10), pady=(5, 5))
        self.next_page_button.pack(side=tk.RIGHT, anchor=tk.E)
        self.previous_page_button.pack(side=tk.RIGHT, anchor=tk.W)
        self.first_page_button.pack(side=tk.RIGHT, anchor=tk.W)

        self.page_number_label.pack(side=tk.RIGHT, anchor=tk.W, padx=(0, 40), pady=(1, 0))
        # self.pagination_combo.pack(side=ctk.RIGHT, anchor=ctk.W, padx=(0, 40), pady=(1, 0))

        self.table_canvas.pack(side=tk.TOP, expand=False, fill=tk.Y)

        tk.Frame.pack(self, **kwargs)
        self.update_idletasks()

        self.pack_vertical_scrollbar()
        self.pack_horizontal_scrollbar()
