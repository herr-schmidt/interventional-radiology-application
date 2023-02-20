from cefpython3 import cefpython as cef
import ctypes
import sys
import os
import platform
import logging as _logging
import tkinter as tk

# Fix for PyCharm hints warnings
WindowUtils = cef.WindowUtils()

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")

# Globals
logger = _logging.getLogger("tkinter_.py")


class MainBrowserFrame(tk.Frame):

    def __init__(self, root, file_path):
        self.browser_frame = None

        # Root
        root.geometry("900x506")

        # MainFrame
        tk.Frame.__init__(self, root)
        self.master.title("Tkinter example")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Configure>", self.on_root_configure)
        self.bind("<Configure>", self.on_configure)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        # BrowserFrame
        self.browser_frame = BrowserFrame(self, file_path)
        self.browser_frame.pack(expand=tk.YES, fill=tk.BOTH)

        # Pack MainFrame
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def on_root_configure(self, _):
        logger.debug("MainFrame.on_root_configure")
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        logger.debug("MainFrame.on_configure")
        if self.browser_frame:
            width = event.width
            height = event.height
            self.browser_frame.on_mainframe_configure(width, height)

    def on_focus_in(self, _):
        logger.debug("MainFrame.on_focus_in")

    def on_focus_out(self, _):
        logger.debug("MainFrame.on_focus_out")

    def on_close(self):
        if self.browser_frame:
            self.browser_frame.on_root_close()
        self.master.destroy()

    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None


class BrowserFrame(tk.Frame):

    def __init__(self, master, file_path):
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, master)
        self.file_path = file_path
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        self.focus_set()

    def embed_browser(self):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info,
                                             url="file:///" + self.file_path)
        assert self.browser
        self.browser.SetClientHandler(FocusHandler(self))
        self.message_loop_work()

    def get_window_handle(self):
        if self.winfo_id() > 0:
            return self.winfo_id()
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            if WINDOWS:
                ctypes.windll.user32.SetWindowPos(
                    self.browser.GetWindowHandle(), 0,
                    0, 0, width, height, 0x0002)
            elif LINUX:
                self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()

    def on_focus_in(self, _):
        logger.debug("BrowserFrame.on_focus_in")
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        logger.debug("BrowserFrame.on_focus_out")
        if self.browser:
            self.browser.SetFocus(False)

    def on_root_close(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        self.destroy()

    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.browser = None


class FocusHandler(object):

    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    def OnTakeFocus(self, next_component, **_):
        logger.debug("FocusHandler.OnTakeFocus, next={next}"
                     .format(next=next_component))

    def OnSetFocus(self, source, **_):
        logger.debug("FocusHandler.OnSetFocus, source={source}"
                     .format(source=source))
        return False

    def OnGotFocus(self, **_):
        """Fix CEF focus issues (#255). Call browser frame's focus_set
           to get rid of type cursor in url entry widget."""
        logger.debug("FocusHandler.OnGotFocus")
        self.browser_frame.focus_set()