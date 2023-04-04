import customtkinter

import utils

try:
    # for Python2
    from Tkinter import *  ## notice capitalized T in Tkinter
    import tkFileDialog, tkMessageBox
except ImportError:
    # for Python3
    from tkinter import *  ## notice lowercase 't' in tkinter here
    from tkinter import filedialog as tkFileDialog
    from tkinter import messagebox as tkMessageBox
import sys, os
from scipy.io.wavfile import read
import analysis
import ctk_analysis_frame

# sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../models/'))
# import utilFunctions as UF


class Combined_feedback_frame:

    def __init__(self, parent):
        self.parent = parent
        self.base_location = "audio/recordings/"
        self.file_list_elements = []
        self.initUI()

    def initUI(self):
        song_entry_text = "Name of the piece (no spaces or special characters:"
        # Label(self.parent, text=song_entry_text).grid(row=0, column=0, sticky=W, padx=5, pady=(10, 2))

        # TEXTBOX TO PRINT PATH OF THE SOUND FILE
        # Displays the output filename/location
        # self.songname = Entry(self.parent)
        # self.songname.focus_set()
        # self.songname["width"] = 25
        # # self.songname.grid(row=1, column=0, sticky=W, padx=10)
        # self.songname.delete(0, END)
        # self.songname.insert(0, 'cmajorscale')
        # create navigation frame
        self.settings_frame = customtkinter.CTkFrame(self.parent, corner_radius=0)
        self.settings_frame.pack(side='left', anchor="w", fill='both')

        self.settings_frame_label = customtkinter.CTkLabel(self.settings_frame, text="Combined Performances",
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.settings_frame_label.pack(side='top',padx=20, pady=20)

        self.placeholder_btn = customtkinter.CTkButton(self.settings_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   anchor="w")
        self.placeholder_btn.pack(anchor="s")

        # Dropdown labels and input elements
        self.piece_dropdown_label = customtkinter.CTkLabel(self.settings_frame, text="1. Select Piece",
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.piece_dropdown_label.pack(side='top', anchor='w')
        piece_var = customtkinter.StringVar(value="cmajorscale")  # set initial value
        self.piece_dropdown = customtkinter.CTkOptionMenu(master=self.settings_frame,
                                                          values=["cmajorscale", "danishroll", "chromaticscale"],
                                                          command=self.performance_feedback,
                                                          variable=piece_var)
        self.piece_dropdown.pack(side='top', padx=20, pady=20, anchor='w')
        # self.piece_dropdown.pack(side='top', anchor=W)
        # TEXTBOX FOR INPUT OF INSTRUMENT BEING PLAYED
        # instrument_entry_text = "The instrument being played:"
        # # Label(master=self.parent, text=instrument_entry_text).grid(row=2, column=0, sticky=W, padx=5, pady=(10,2))
        #
        # self.instrument = Entry(self.parent)
        # self.instrument["width"] = 25
        # # self.instrument.grid(row=3, column=0, sticky=W, padx=10)
        # self.instrument.delete(0, END)
        # self.instrument.insert(0, 'piano')
        self.piece_dropdown_label = customtkinter.CTkLabel(self.settings_frame, text="2. Pick Instrument",
                                                           compound="left",
                                                           font=customtkinter.CTkFont(size=15, weight="bold"))
        self.piece_dropdown_label.pack(side='top', anchor='w')
        instrument_var = customtkinter.StringVar(value="Piano")  # set initial value
        self.instrument_dropdown = customtkinter.CTkOptionMenu(master=self.settings_frame,
                                                               values=["Trumpet", "Piano"],
                                                               command=self.performance_feedback,
                                                               variable=instrument_var)
        self.instrument_dropdown.pack(side='top', padx=20, pady=20, anchor='w')

        # Include scrollable frame to populate with recording filenames
        self.file_list = customtkinter.CTkScrollableFrame(self.settings_frame)
        self.file_list.pack(side='bottom', padx=20, pady=20, anchor='s')

        # self.instrument_dropdown.pack(side='top', anchor=W)
        # DISPLAY OF FILENAME/LOCATION OUTPUT
        # filename_text = "Filename:"
        # # Label(master=self.parent, text=filename_text).grid(row=4, column=0, sticky=W, padx=5, pady=(10,2))
        #
        # self.filename = Entry(self.parent)
        # self.filename["width"] = 25
        # # self.filename.grid(row=5, column=0, sticky=W, padx=10)
        # self.filename.delete(0, END)
        # self.filename.insert(0, self.base_location + self.songname.get() + "-" + self.instrument.get() + ".wav")
        #
        # # BUTTON TO RECORD AUDIO
        # self.record = Button(master=self.parent, text="Show Feedback", command=self.performance_feedback)
        # # self.record.grid(row=6, column=0, sticky=W, padx=(10, 6))
        # self.record.pack(side='bottom')

    def new_analysis_frame(self, filename):
        new = Toplevel(self.parent)
        ctk_analysis_frame.Analysis_frame(new, filename=filename)

    def performance_feedback(self, event):

        for index, element in enumerate(self.file_list_elements):
            self.file_list_elements[index].destroy()

        print("Loading feedback")
        # Build a new frame beneath the controls
        feedback_frame = Frame(master=self.parent)
        feedback_frame.pack(expand=True)
        # feedback_frame.grid(row=7, column=0, sticky=W)

        performances = utils.get_multiple_performances(self.instrument_dropdown.get().lower(),
                                                       self.piece_dropdown.get().lower())
        for performance in performances:
            file_button = customtkinter.CTkButton(self.file_list,
                                                  text=performance.filename,
                                                  command=lambda: self.new_analysis_frame(performance.get_filename()))
            file_button.pack(side='top')
            self.file_list_elements.append(file_button)
        analysis.multi_performance_feedback(feedback_frame, performances)
