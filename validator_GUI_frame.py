import tkinter
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

    def __init__(self, parent):
        self.parent = parent
        self.initUI()

    def initUI(self):

        # FILE SELECTION OPTIONS
        self.file_opt = options = {}
        options['defaultextension'] = '.wav'
        options['filetypes'] = [('All files', '.*'), ('Wav files', '.wav')]
        options['initialdir'] = '../../sounds/'
        options['title'] = 'Open a mono audio file .wav with sample frequency 44100 Hz'

        # FILE SELECTOR
        select_file_text = "Select a file (.wav)"
        Label(master=self.parent, text=select_file_text).grid(row=0, column=0, sticky=W, padx=5, pady=(10, 2))

        self.file_location = Entry(self.parent)
        self.file_location.focus_set()
        self.file_location["width"] = 25
        self.file_location.grid(row=1, column=0, sticky=W, padx=10)
        self.file_location.delete(0, END)
        self.file_location.insert(0, 'testing/data/Bock_Dataset-Onsets/audio/ah_development_guitar_2684_TexasMusicForge_Dandelion_pt1.flac')

        self.browse_btn = Button(master=self.parent, text="Browse", command=self.browse_file)
        self.browse_btn.grid(row=1, column=1, stick=W, padx=10)

        # PLAY AUDIO BUTTON
        self.play_btn_txt = tkinter.StringVar()
        self.play_btn_txt.set("Play Audio")
        self.play_btn = Button(master=self.parent, text=self.play_btn_txt.get(), command=self.play_audio)
        self.play_btn.grid(row=2, column=0, stick=W, padx=10)
        self.player = player.player(self.file_location.get())

        # VALIDATE SINGLE FILE BUTTON
        self.analyse_btn = Button(master=self.parent, text="Validate Selected", command=self.analyse_file)
        self.analyse_btn.grid(row=2, column=1, stick=W, padx=10)

        # VALIDATE ALL FILES BUTTON
        self.val_btn = Button(master=self.parent, text="Validate All", command=self.validate_models)
        self.val_btn.grid(row=2, column=2, stick=W, padx=10)
        self.validator = validator.validator()

    def browse_file(self):
        self.filename = tkFileDialog.askopenfilename(**self.file_opt)

        # set the text of the self.filelocation
        self.file_location.delete(0, END)
        self.file_location.insert(0, self.filename)

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
        feedback_frame = Frame(master=self.parent)
        feedback_frame.grid(row=3, column=0, sticky=W)

        # Pass the new frame as the parent/master for the matplotlib elements
        analysis.draw_single_performance_feedback(feedback_frame,
                                                  utils.get_performance_record(self.file_location.get()))

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

    def validate_models(self):
        """
        1. Call the validator, pass through the validation type as a parameter (i.e. onset detection, f0 curve, etc)
        2. Validator saves results to JSON
            2.1 Parameters for the function in question are also saved to the JSON file
        """
        self.validator.bock_validation()