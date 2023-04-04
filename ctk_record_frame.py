import time
import tkinter

import librosa

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
import pretty_midi
import matplotlib.pyplot as plt
import mir_eval.display
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import ctk_analysis_frame
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

        # TEXTBOX TO PRINT PATH OF THE SOUND FILE
        # Displays the output filename/location
        # self.songname = Entry(self.parent)
        # self.songname.focus_set()
        # self.songname["width"] = 25
        # self.songname.grid(row=1, column=0, sticky=W, padx=10)
        # self.songname.delete(0, END)
        # self.songname.insert(0, 'cmajorscale')
        self.labels_frame = customtkinter.CTkFrame(self.parent, corner_radius=0)
        self.labels_frame.pack(side='top', anchor=N, fill='both')

        self.settings_frame = customtkinter.CTkFrame(self.parent)
        self.settings_frame.pack(side='top', anchor=N, fill='both')

        song_entry_text = "1. Pick the name of the piece"
        customtkinter.CTkLabel(self.labels_frame, text=song_entry_text).pack(side='left', padx=20, pady=10, anchor='center')

        self.performance_options = customtkinter.CTkComboBox(self.settings_frame, values=['cmajorscale', 'chromaticscale'], command=self.load_midi_pianoroll)
        self.performance_options.pack(side='left', padx=20, pady=10)

        # TEXTBOX FOR INPUT OF INSTRUMENT BEING PLAYED
        instrument_entry_text = "2. Pick your instrument:"
        customtkinter.CTkLabel(master=self.labels_frame, text=instrument_entry_text).pack(side='left', padx=20, pady=10)

        self.instrument_options = customtkinter.CTkComboBox(self.settings_frame, values=['Piano', 'Trumpet'])
        self.instrument_options.pack(side='left', padx=20, pady=10)

        # self.instrument = Entry(self.parent)
        # self.instrument["width"] = 25
        # self.instrument.pack()
        # # self.instrument.grid(row=3, column=0, sticky=W, padx=10)
        # self.instrument.delete(0, END)
        # self.instrument.insert(0, 'piano')

        # DISPLAY OF FILENAME/LOCATION OUTPUT
        filename_text = "Filename:"
        customtkinter.CTkLabel(master=self.labels_frame, text=filename_text).pack(side='left', padx=20, pady=10)

        self.filename = customtkinter.CTkEntry(self.settings_frame)
        self.filename["width"] = 25
        # self.filename.grid(row=5, column=0, sticky=W, padx=10)
        self.filename.pack(side='left', padx=20, pady=10)
        self.filename.delete(0, END)
        self.filename.insert(0, self.base_location + self.performance_options.get().lower() + "-" + self.instrument_options.get().lower() + ".wav")

        # FRAME CONTAINER FOR PIANO ROLL PLOT
        self.plot_frame = customtkinter.CTkFrame(master=self.parent,
                                            height=self.parent.winfo_height() * 0.5,
                                            width=self.parent.winfo_width() * 0.5,
                                            fg_color="darkblue")
        self.plot_frame.pack(side='top', padx=20, pady=20)

        # BUTTON TO RECORD AUDIO
        self.record = customtkinter.CTkButton(master=self.parent, text="Record", command=self.record_audio)
        self.record.pack(side='bottom', padx=20, pady=10)
        # self.record = Button(master=self.parent, text="Record", command=self.record_audio)
        # self.record.grid(row=5, column=1, sticky=W, padx=(306, 6))
        self.load_midi_pianoroll()

    def new_analysis_frame(self, filename):
        new = Toplevel(self.parent)
        ctk_analysis_frame.Analysis_frame(new, filename=filename)
    def load_midi_pianoroll(self):
        groundtruth = pretty_midi.PrettyMIDI("testing/midi_files/" + self.performance_options.get().lower() + ".mid")

        frequencies = []
        intervals = []

        for idx, note in enumerate(groundtruth.instruments[0].notes):
            frequencies.append(note.pitch)
            intervals.append((note.start, note.end))

        fig, ax = plt.subplots(nrows=1, figsize=(10, 2), facecolor='#242424')

        # Plot the piano roll
        ax.set_title("Piano Roll", color='white')
        ax.set_xlabel("Time (s)", color='white')
        ax.set_ylabel("Pitch", color='white')
        # Set colours
        ax.set_facecolor("#f2f2f2")
        ax.tick_params(labelcolor='white')
        kwargs_correct = {'color': 'green'}
        if frequencies is not None:
            mir_eval.display.piano_roll(intervals=intervals, pitches=librosa.midi_to_hz(frequencies), ax=ax, label='Correct Notes',
                                        alpha=0.5, **kwargs_correct)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
        self.plot_frame.pack(expand=True)

    def record_audio(self):

        # Start recording audio file here
        # Save the file
        # Run analysis and save JSON file

        processing_message = tkinter.Toplevel()

        self.recorder.start(self.performance_options.get().lower(), self.instrument_options.get().lower())
        recordingSaved = tkMessageBox.askyesno(title="Recording", message="Recording in progress.\nYes to stop and save recording.")

        if recordingSaved:
            processing_message.focus_set()
            processing_message.transient()
            processing_message.title("Processing")
            tkinter.Label(processing_message, text="Processing audio\nPlease wait...").pack()

            self.recorder.stop()
            self.recorder.analyse_audio()

            processing_message.destroy()
            self.new_analysis_frame(self.filename)
