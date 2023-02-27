import customtkinter as ctk
from view import GUI
from model import InterventionalRadiologyModel
from controller import Controller
from embedded_browser import cef

root = ctk.CTk()
ctk.set_appearance_mode("light")
root.title("Interventional Radiology Planner & Scheduler")
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),
                                   root.winfo_screenheight()))
root.state("zoomed")

model = InterventionalRadiologyModel()
view = GUI(root)
controller = Controller(model=model, view=view)
view.bind_controller(controller=controller)
view.initializeUI()

# disable gpu in order to avoid the pesky scaling issue
cef.Initialize(settings={}, switches={'disable-gpu': ""})
root.mainloop()
cef.Shutdown()
