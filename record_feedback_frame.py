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
import recorder
import customtkinter
# import dftModel_function

# sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../models/'))
# import utilFunctions as UF


class Record_frame:

    def __init__(self, parent):
        self.parent = parent
        self.base_location = "audio/recordings/"
        self.recorder = recorder.recorder("")
        self.initUI()

    def initUI(self):
        song_entry_text = "1. Select the piece:"
        Label(self.parent, text=song_entry_text).grid(row=0, column=0, sticky=W, padx=5, pady=(10, 2))

        # Selector for the piece
        #   Options to be pulled from the midi folder
        self.piece_dropdown = customtkinter.CTkOptionMenu(master=self.parent, values=["cmajorscale", "danishroll", "chromaticscale"])
        self.piece_dropdown.grid(row=1, column=0, sticky=W)

        instrument_text = "2. Pick your instrument:"
        Label(self.parent, text=instrument_text).grid(row=0, column=1, sticky=W, padx=5, pady=(10, 2))
        # Selector for the instrument
        #   Options restricted to piano and trumpet for now
        self.instrument_dropdown = customtkinter.CTkOptionMenu(master=self.parent, values=["Trumpet", "Piano"])
        self.instrument_dropdown.grid(row=1, column=1, sticky=W)

        # DISPLAY OF FILENAME/LOCATION OUTPUT
        filename_text = "Filename:"
        Label(master=self.parent, text=filename_text).grid(row=2, column=0, sticky=W, padx=5, pady=(10,2))

        self.filename = Entry(self.parent)
        self.filename["width"] = 25
        self.filename.grid(row=3, column=0, sticky=W, padx=10)
        self.filename.delete(0, END)
        self.filename.insert(0, self.base_location + self.piece_dropdown.get() + "-" + self.instrument_dropdown.get() + ".wav")

        # BUTTON TO RECORD AUDIO
        self.record = customtkinter.CTkButton(master=self.parent, text="Record", command=self.record_audio)
        # self.record = Button(master=self.parent, text="Record", command=self.record_audio)
        self.record.grid(row=4, column=1, sticky=W)

    def record_audio(self):

        # Start recording audio file here
        # Save the file
        # Run analysis and save JSON file

        self.recorder.start(self.piece_dropdown.get(), self.instrument_dropdown.get())

        recording_saved = tkMessageBox.askyesno(title="Recording", message="Recording in progress.\nYes to stop and save recording.")

        if recording_saved:
            self.recorder.stop()
            self.recorder.analyse_audio()
            tkMessageBox.showinfo("opts", message="Audio recording saved successfully")