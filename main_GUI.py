import sys
import matplotlib
matplotlib.use('TkAgg')
try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter
except ImportError:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here
from notebook import *   # window with tabs
from record_GUI_frame import *
from analysis_GUI_frame import *
from combined_feedback_GUI_frame import *

root = Tk( )
root.title('Performance Feedback GUI')
nb = notebook(root, TOP) # make a few diverse frames (panels), each using the NB as 'master':

# uses the notebook's frame
f1 = Frame(nb( ))
record = Record_frame(f1)

f2 = Frame(nb( ))
analysis = Analysis_frame(f2)

f3 = Frame(nb( ))
sine = Combined_feedback_frame(f3)

# f4 = Frame(nb( ))
# harmonic = HarmonicModel_frame(f4)
#
# f5 = Frame(nb( ))
# stochastic = StochasticModel_frame(f5)
#
# f6 = Frame(nb( ))
# spr = SprModel_frame(f6)
#
# f7 = Frame(nb( ))
# sps = SpsModel_frame(f7)
#
# f8 = Frame(nb( ))
# hpr = HprModel_frame(f8)
#
# f9 = Frame(nb( ))
# hps = HpsModel_frame(f9)

nb.add_screen(f1, "Record Audio")
nb.add_screen(f2, "Analyse Recording")
nb.add_screen(f3, "Combined Feedback")
# nb.add_screen(f4, "Harmonic")
# nb.add_screen(f5, "Stochastic")
# nb.add_screen(f6, "SPR")
# nb.add_screen(f7, "SPS")
# nb.add_screen(f8, "HPR")
# nb.add_screen(f9, "HPS")

nb.display(f1)

root.geometry('+0+0')
root.mainloop( )