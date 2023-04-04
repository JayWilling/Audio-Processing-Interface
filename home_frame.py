import datetime
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy
import numpy as np
import customtkinter
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from collections import defaultdict, Counter
from datetime import date
from operator import itemgetter

class Home_frame:
    def __init__(self, parent):
        self.parent = parent
        self.base_location = "audio/recordings/"
        self.initUI()

    def initUI(self):

        # Upper display
        #   Heading

        self.home_frame_label = customtkinter.CTkLabel(self.parent, text="This Month:",
                                                             font=customtkinter.CTkFont(size=20, weight="bold"))
        # self.home_frame_label.grid(row=0, column=0, padx=20, pady=(20, 0))
        self.home_frame_label.pack(side="top", expand=True, fill="both")
        # self.home_frame_label.place(relx=0.5, rely=0.1, anchor='center')

        #   Plot of performances over the month
        # EMPTY PLACEHOLDER PLOT BEFORE THERE IS DATA TO SHOW
        self.plot_frame = customtkinter.CTkFrame(master=self.parent,
                                            height=self.parent.winfo_height() * 0.5,
                                            width=self.parent.winfo_width() * 0.5,
                                            fg_color="darkblue")
        self.plot_frame.pack(side="top")
        # self.plot_frame.grid(row=1, column=0, padx=20, pady=20)
        # self.home_frame_label.place(relx=0.5, rely=0.1, anchor='center')
        self.plot_progress()
        # self.plot_frame.place(relx=0.33, rely=0.025)

        #   Summary for performances over the month
        # 1. Total no. of Performances
        self.performance_count_label = customtkinter.CTkLabel(master=self.parent, text="Total Performances:\n87",
                                                             font=customtkinter.CTkFont(size=14, weight="bold"))
        self.performance_count_label.pack(side="left", fill='both', expand=True, pady=(0, 20))

        # 2. Total time of Performances
        self.performance_time_label = customtkinter.CTkLabel(master=self.parent, text="Performance Time:\n5hrs",
                                                             font=customtkinter.CTkFont(size=14, weight="bold"))
        self.performance_time_label.pack(side="left", fill='both', expand=True, pady=(0, 20))

        # 3. No. of pieces played
        self.piece_count_label = customtkinter.CTkLabel(master=self.parent, text="Total Pieces Played:\n12",
                                                             font=customtkinter.CTkFont(size=14, weight="bold"))
        self.piece_count_label.pack(side="left", fill='both', expand=True, pady=(0, 20))

        # Lower affirmation

    def count_performances(self):
        path = 'audio/recordings/'
        date_counter = defaultdict(Counter)

        for name in os.listdir(path):
            print(name)
            fullpath = os.path.join(path, name)
            if os.path.isfile(fullpath):
                m_time = os.path.getmtime(fullpath)
                dt_m = datetime.datetime.fromtimestamp(m_time)

                print(dt_m.date())



    def plot_progress(self):
        # generate random numbers for the plot
        x, y, s, c = np.random.rand(4, 100)
        data = numpy.zeros(31)
        for i in range(31):
            data[i] = np.random.randint(0+i, 7+i)

        # generate the figure and plot object which will be linked to the root element
        fig, ax = plt.subplots(figsize=(10, 2), facecolor='#242424')
        ax.set_facecolor("#f2f2f2")
        ax.tick_params(labelcolor='white')
        ax.plot(data)
        ax.grid(True)
        ax.set_xticks(range(1, 31))

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
        self.plot_frame.pack(expand=True)

        self.count_performances()
