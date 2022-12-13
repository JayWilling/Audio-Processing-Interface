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

# sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../models/'))
# import utilFunctions as UF


class Combined_feedback_frame:

    def __init__(self, parent):
        self.parent = parent
        self.base_location = "audio/recordings/"
        self.initUI()

    def initUI(self):
        song_entry_text = "Name of the piece (no spaces or special characters:"
        Label(self.parent, text=song_entry_text).grid(row=0, column=0, sticky=W, padx=5, pady=(10, 2))

        # TEXTBOX TO PRINT PATH OF THE SOUND FILE
        # Displays the output filename/location
        self.songname = Entry(self.parent)
        self.songname.focus_set()
        self.songname["width"] = 25
        self.songname.grid(row=1, column=0, sticky=W, padx=10)
        self.songname.delete(0, END)
        self.songname.insert(0, 'cmajorscale')

        # TEXTBOX FOR INPUT OF INSTRUMENT BEING PLAYED
        instrument_entry_text = "The instrument being played:"
        Label(master=self.parent, text=instrument_entry_text).grid(row=2, column=0, sticky=W, padx=5, pady=(10,2))

        self.instrument = Entry(self.parent)
        self.instrument["width"] = 25
        self.instrument.grid(row=3, column=0, sticky=W, padx=10)
        self.instrument.delete(0, END)
        self.instrument.insert(0, 'piano')

        # DISPLAY OF FILENAME/LOCATION OUTPUT
        filename_text = "Filename:"
        Label(master=self.parent, text=filename_text).grid(row=4, column=0, sticky=W, padx=5, pady=(10,2))

        self.filename = Entry(self.parent)
        self.filename["width"] = 25
        self.filename.grid(row=5, column=0, sticky=W, padx=10)
        self.filename.delete(0, END)
        self.filename.insert(0, self.base_location + self.songname.get() + "-" + self.instrument.get() + ".wav")

        # BUTTON TO RECORD AUDIO
        self.record = Button(master=self.parent, text="Show Feedback", command=self.performance_feedback)
        self.record.grid(row=6, column=0, sticky=W, padx=(10, 6))

    def performance_feedback(self):
        print("Loading feedback")
        # Build a new frame beneath the controls
        feedback_frame = Frame(master=self.parent)
        feedback_frame.grid(row=7, column=0, sticky=W)

        performances = utils.get_multiple_performances(self.instrument.get(), self.songname.get())
        analysis.multi_performance_feedback(feedback_frame, performances)
        print(performances)
