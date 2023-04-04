import tkinter

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
import player
import validator
import analysis


class Analysis_frame:

    def __init__(self, parent, filename):
        self.parent = parent
        self.filename = filename
        self.initUI()

    def initUI(self):

        self.analyse_file()

        # PLAY AUDIO BUTTON
        self.play_btn_txt = tkinter.StringVar()
        self.play_btn_txt.set("Play Audio")
        self.play_btn = Button(master=self.parent, text=self.play_btn_txt.get(), command=self.play_audio)
        self.play_btn.grid(row=2, column=1, stick=W, padx=10)
        self.player = player.player(self.filename + '.wav')

    def analyse_file(self):
        print("Analysing")
        """
        ** This first part will be included in a utils file as I will use this function more than once **
            Check if JSON file for the selected file exists, if not, create it.
            If JSON file exists, load it in and display graphics

        ** Main functionality **
            Load JSON file for selected .wav
            Run analysis file, show new window with multiple graphs on the single performance

        ** Embed matplotlib in tkinter GUI **
            https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/
            To ensure the display is easy to understand and all information is coherent
            we want the graphs to be shown together on the one screen but can be done once
            the main graphs are setup and displaying 
        """
        # Build a new frame beneath the controls
        feedback_frame = customtkinter.CTkFrame(master=self.parent)
        # feedback_frame.grid(row=3, column=0, sticky=W)
        feedback_frame.pack(fill='both', expand=True)

        # Pass the new frame as the parent/master for the matplotlib elements
        analysis.draw_single_performance_feedback(feedback_frame,
                                                  utils.get_performance_record(self.filename))

    # Handles audio playback and stopping
    def play_audio(self):

        if (self.player.playing):
            self.play_btn_txt.set("Play Audio")
            self.player.stop()
        else:
            self.play_btn_txt.set("Stop Audio")
            self.player.set_filename(filename=self.file_location.get())
            self.player.start()
            print("Playing audio")
