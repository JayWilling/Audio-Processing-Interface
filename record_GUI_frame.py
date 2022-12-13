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
        self.record = Button(master=self.parent, text="Record", command=self.record_audio)
        self.record.grid(row=5, column=1, sticky=W, padx=(306, 6))

    def record_audio(self):

        # Start recording audio file here
        # Save the file
        # Run analysis and save JSON file

        self.recorder.start(self.songname.get(), self.instrument.get())

        recordingSaved = tkMessageBox.askyesno(title="Recording", message="Recording in progress.\nYes to stop and save recording.")

        if recordingSaved:
            self.recorder.stop()
            self.recorder.analyse_audio()
            tkMessageBox.showinfo("opts", message="Audio recording saved successfully")