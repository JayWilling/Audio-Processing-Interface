import sys
import matplotlib
matplotlib.use('TkAgg')
import customtkinter
try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter
except ImportError:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here
from notebook import *   # window with tabs
from ctk_record_frame import *
from analysis_GUI_frame import *
from ctk_combined_frame import *
from home_frame import *
from models.groundtruth_builder import create_gt_midis


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Performance Feedback")
        self.geometry("1000x450")
        create_gt_midis()

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Image Example",
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                      border_spacing=10, text="Play",
                                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                                      hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.play_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                      border_spacing=10, text="Review",
                                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                                      hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.review_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                                values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        home = Home_frame(self.home_frame)
        # self.home_frame.grid_columnconfigure(0, weight=1)
        #
        # self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="")
        # self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)
        #
        # self.home_frame_button_1 = customtkinter.CTkButton(self.home_frame, text="")
        # self.home_frame_button_1.grid(row=1, column=0, padx=20, pady=10)
        # self.home_frame_button_2 = customtkinter.CTkButton(self.home_frame, text="CTkButton", compound="right")
        # self.home_frame_button_2.grid(row=2, column=0, padx=20, pady=10)
        # self.home_frame_button_3 = customtkinter.CTkButton(self.home_frame, text="CTkButton", compound="top")
        # self.home_frame_button_3.grid(row=3, column=0, padx=20, pady=10)
        # self.home_frame_button_4 = customtkinter.CTkButton(self.home_frame, text="CTkButton", compound="bottom", anchor="w")
        # self.home_frame_button_4.grid(row=4, column=0, padx=20, pady=10)

        # create second frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        record = Record_frame(self.second_frame)

        # create third frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        comb = Combined_feedback_frame(self.third_frame)

        # select default frame
        self.select_frame_by_name("Home")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "Home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "Play":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "Review":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("Home")

    def play_button_event(self):
        self.select_frame_by_name("Play")

    def review_button_event(self):
        self.select_frame_by_name("Review")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    app = App()
    app.mainloop()

# root = customtkinter.CTk( )
# root.title('Performance Feedback GUI')
# nb = notebook(root, TOP) # make a few diverse frames (panels), each using the NB as 'master':

# uses the notebook's frame
# f1 = Frame(nb( ))
# record = Record_frame(f1)
#
# f2 = Frame(nb( ))
# analysis = Analysis_frame(f2)
#
# f3 = Frame(nb( ))
# sine = Combined_feedback_frame(f3)
#
# nb.add_screen(f1, "Record Audio")
# nb.add_screen(f2, "Analyse Recording")
# nb.add_screen(f3, "Combined Feedback")
#
# nb.display(f1)
#
# root.geometry('+0+0')
# root.mainloop( )