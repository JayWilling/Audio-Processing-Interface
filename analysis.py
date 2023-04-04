import math
import sys
import tkinter
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import librosa
import scipy.signal
import customtkinter

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import mir_eval.display
from models.performance_record import Performance_record
from models.transcriber import detectOnsets, loudnessAnalysis

def timing_display(y, sr):

    onset_samples, onset_times, times, onsetEnvelope, silence = detectOnsets(y=y, sr=sr)
    # onsetTimingLabels:
    #   Allow us to identify each onset as 'Early, 'On-time', or 'Late'
    # timingThreshold:
    #   A threshold in frames of when a note falls out of time or off-tempo
    tempo, beats = librosa.beat.beat_track(y=y,
                                           sr=sr,
                                           onset_envelope=onsetEnvelope,
                                           hop_length=512)
    newOnsets = []
    onsetTimingLabels = []
    timingThreshold = 0.3
    for i in onset_times:
        idx = (np.abs(beats - i)).argmin()
        newOnsets.append(beats[idx])
        if i <= beats[idx] - timingThreshold:
            onsetTimingLabels.append('Early')
        elif i >= beats[idx] + timingThreshold:
            onsetTimingLabels.append('Late')
        else:
            onsetTimingLabels.append('On-time')
    #
    return onsetEnvelope, newOnsets, onsetTimingLabels, times, beats

def draw_single_performance_feedback(parent, performance_record):

    y, sr = librosa.load(performance_record.get_filename() + ".wav")
    # Pre-process the audio (Remove silence from start and end of recording)
    # trimmed, trimIndex = librosa.effects.trim(y=y, top_db=20)
    # y = y[trimIndex[0]:trimIndex[1]]

    # Get relevant data from the record
    intervals = []
    frequencies = []
    incorrect_intervals = []
    incorrect_frequencies = []
    missed_intervals = []
    missed_frequencies = []

    # Timing Variables
    timing_labels = []
    ideal_onsets = []

    inter_onsets_y = []
    inter_onsets_x = []
    min_ioi = sys.maxsize
    max_ioi = 0
    print("Note Display - Onset Offset IdealOn")
    for idx, note in enumerate(performance_record.note_list):
        print(note.get_onset_seconds(), note.get_offset_seconds(), note.get_ideal_onset_seconds())
        timing_labels.append(note.get_timing_label())
        ideal_onsets.append(note.get_onset_seconds() - note.get_ideal_onset_seconds())

        # Build piano roll
        # Correct notes
        if note.get_matching() == 'Correct' or note.get_matching() is None:
            intervals.append((note.get_onset_seconds(), note.get_offset_seconds()))
            frequencies.append(note.get_median_frequency())
        # Notes with incorrect pitch
        else:
            incorrect_intervals.append((note.get_onset_seconds(), note.get_offset_seconds()))
            incorrect_frequencies.append(note.get_median_frequency())

        # Calculate inter-onset intervals
        if (idx == 0):
            current_onset = performance_record.note_list[idx].get_onset_seconds()
        if idx != len(performance_record.note_list) - 1:
            next_onset = performance_record.note_list[idx + 1].get_onset_seconds()
            inter_onsets_y.append(next_onset - current_onset)
            inter_onsets_x.append(note.get_name())
            current_onset = next_onset
        else:
            inter_onsets_y.append(note.get_offset_seconds()-note.get_onset_seconds())
            # inter_onsets_y.append(note.get_duration_seconds())
            inter_onsets_x.append(note.get_name())
        if inter_onsets_y[idx] < min_ioi:
            min_ioi = inter_onsets_y[idx]
        elif inter_onsets_y[idx] > max_ioi:
            max_ioi = inter_onsets_y[idx]
    print("Ideal Onsets:")
    print(ideal_onsets)
    # Use the max and min ioi to shift the ideal onsets
    # Ensures that the inter onset visual is correct
    for index, value in enumerate(ideal_onsets):
        ideal_onsets[index] = math.fmod(value, min_ioi)


    # Build the frame for key attributes of the performance:
    #   - Filename
    #   - Tempo
    #   - Correct Notes
    #   - Subbed notes
    #   - Missed notes
    #   - Average timing offset (early or late)
    pitchAccuracy = len(frequencies) / len(performance_record.get_gt_note_list()) * 100

    settings_frame = customtkinter.CTkFrame(parent, corner_radius=0)
    settings_frame.pack(side='left', anchor="w", fill='both')

    filename_label = customtkinter.CTkLabel(settings_frame, text="Filename: " + performance_record.get_filename(),
                                                       compound="left",
                                                       font=customtkinter.CTkFont(size=15, weight="bold"))
    filename_label.pack(side='top', padx=20, pady=20, anchor="w")
    tempo_label = customtkinter.CTkLabel(settings_frame, text="Tempo: " + str(performance_record.get_tempo()),
                                                       compound="left",
                                                       font=customtkinter.CTkFont(size=15, weight="bold"))
    tempo_label.pack(side='top', padx=20, pady=20, anchor="w")
    pitch_label = customtkinter.CTkLabel(settings_frame, text="Pitch Accuracy: " + str(pitchAccuracy) + "%",
                                                       compound="left",
                                                       font=customtkinter.CTkFont(size=15, weight="bold"))
    pitch_label.pack(side='top', padx=20, pady=20, anchor="w")
    correct_label = customtkinter.CTkLabel(settings_frame, text="Correct Notes: " + str(len(frequencies)),
                                                       compound="left",
                                                       font=customtkinter.CTkFont(size=15, weight="bold"))
    correct_label.pack(side='top', padx=20, pady=20, anchor="w")
    incorrect_label = customtkinter.CTkLabel(settings_frame, text="Inccorect Notes: " + str(len(incorrect_frequencies)),
                                                       compound="left",
                                                       font=customtkinter.CTkFont(size=15, weight="bold"))
    incorrect_label.pack(side='top', padx=20, pady=20, anchor="w")
    missed_label = customtkinter.CTkLabel(settings_frame, text="Missed Notes: " + str(len(performance_record.get_gt_note_list()) - len(frequencies)),
                                                       compound="left",
                                                       font=customtkinter.CTkFont(size=15, weight="bold"))
    missed_label.pack(side='top', padx=20, pady=20, anchor="w")

    # Build piano roll for ground truth
    for idx in performance_record.missed_note_indexes:
        missed_intervals.append((performance_record.gt_note_list[idx].start, performance_record.gt_note_list[idx].end))
        missed_frequencies.append(librosa.midi_to_hz(performance_record.gt_note_list[idx].pitch))


    # Estimate tempo and provide note timing feedback
    onset_envelope, newOnsets, onsetTimingLabels, times, beats = timing_display(y, sr)
    # print(times)
    fig, ax = plt.subplots(nrows=3, figsize=(10, 6), facecolor='#242424')

    # Set the visuals
    ax[0].set_facecolor("#f2f2f2")
    ax[0].tick_params(which='both', labelcolor='white')
    ax[0].xaxis.label.set_color('white')
    ax[0].yaxis.label.set_color('white')
    ax[0].title.set_color('white')

    ax[1].set_facecolor("#f2f2f2")
    ax[1].tick_params(which='both', labelcolor='white')
    ax[1].xaxis.label.set_color('white')
    ax[1].yaxis.label.set_color('white')
    ax[1].title.set_color('white')

    ax[2].set_facecolor("#f2f2f2")
    ax[2].tick_params(which='both', labelcolor='white')
    ax[2].xaxis.label.set_color('white')
    ax[2].yaxis.label.set_color('white')
    ax[2].title.set_color('white')

    # Plot the piano roll
    print("Frequencies:")
    print(incorrect_frequencies)
    print(frequencies)
    ax[0].set_title("Piano Roll")
    ax[0].set_xlabel("Time (s)")
    ax[0].set_ylabel("Pitch")
    kwargs_correct = {'color': 'green'}
    kwargs_incorrect = {'color': 'red'}
    kwargs_missed = {'color': 'grey'}
    if frequencies is not None:
        mir_eval.display.piano_roll(intervals=intervals, pitches=frequencies, ax=ax[0], label='Correct Notes', alpha=0.5, **kwargs_correct)
    mir_eval.display.piano_roll(intervals=incorrect_intervals, pitches=incorrect_frequencies, ax=ax[0], label='Mistakes', alpha=0.5, **kwargs_incorrect)
    mir_eval.display.piano_roll(intervals=missed_intervals, pitches=missed_frequencies, ax=ax[0], label='Missed Notes', alpha=0.5, **kwargs_missed)
    plt.grid('on')
    mir_eval.display.ticker_notes(ax=ax[0])

    # Display timing markers as well for the transcribed notes
    # IMPOSSIBLE to work anything out from this display
    # ax[0].vlines(ideal_onsets, ymin=librosa.hz_to_midi(min(frequencies))-1, ymax=librosa.hz_to_midi(max(frequencies))+1)
    # ax[0].set_xticks(ticks=ideal_onsets, labels=timing_labels)

    # Calculate the loudness of the performance
    loudness, loudness_times = loudnessAnalysis(y, sr)

    # Select the peaks from the loudness curve
    peaks, properties = scipy.signal.find_peaks(loudness[0])
    min_peak = min(loudness[0][peaks])
    max_peak = max(loudness[0][peaks])

    # Calculate a line of best fit using the peaks
    res = scipy.stats.linregress(peaks, loudness[0][peaks])
    print('{0:.10f}'.format(res.slope))

    # Plot the inter-onset intervals
    ax[1].set_title("Inter Onset Intervals")
    ax[1].set_xlabel("Note names")
    ax[1].set_ylabel("Time (s)")
    ax[1].bar(range(len(inter_onsets_x)), inter_onsets_y, bottom=ideal_onsets)
    ax[1].set_xticks(range(0, len(inter_onsets_x)), inter_onsets_x)
    ax[1].grid(True)
    ax[1].set_yticks(np.arange(0, max_ioi, min_ioi))
    ax[1].set_ylim(-1)

    print(ideal_onsets)
    print(inter_onsets_y)
    # Changes to emphasise onset and offset timings
    ax[1].set_ylim(-min_ioi)

    # Plot the onsets alone and envelope
    # ax[1].plot(times, librosa.util.normalize(onset_envelope))
    # ax[1].vlines(times[beats], 0, 1, color='r', alpha=0.9, linestyle='--', label='Onsets')

    # Plot the loudness of the performance as well
    # ax[2].semilogy(loudness_times, loudness[0], label="Loudness")
    ax[2].set_title("Loudness")
    ax[2].set_xlabel("Time (s)")
    ax[2].set_ylabel("dbA (log10)")
    ax[2].plot(loudness[0], alpha=0.4)
    ax[2].plot(peaks, loudness[0][peaks], 'o', alpha=0.4)
    ax[2].plot(peaks, res.intercept + res.slope*peaks, '--k')
    ax[2].set_ylim([min_peak, max_peak])

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
    parent.pack(expand=True)
    toolbar = NavigationToolbar2Tk(canvas, parent)
    toolbar.update()

def multi_performance_feedback(parent, performances):

    # Retrieve relevant data
    note_dict = {}

    frequencies = []
    loudness = []
    tempo = []
    for performance in performances:
        tempo.append(performance.get_tempo())
        for note in performance.note_list:
            note_dict.setdefault(note.name, []).append(note.loudness)
            frequencies.append(note.get_avg_frequency())
            loudness.append(note.get_avg_loudness())
            print(note.loudness)

    fig, ax = plt.subplots(nrows=3, figsize=(10, 6), facecolor='#242424')

    ax[0].set_facecolor("#f2f2f2")
    ax[0].tick_params(which='both', labelcolor='white')
    ax[0].xaxis.label.set_color('white')
    ax[0].yaxis.label.set_color('white')
    ax[0].title.set_color('white')

    ax[1].set_facecolor("#f2f2f2")
    ax[1].tick_params(which='both', labelcolor='white')
    ax[1].xaxis.label.set_color('white')
    ax[1].yaxis.label.set_color('white')
    ax[1].title.set_color('white')

    ax[2].set_facecolor("#f2f2f2")
    ax[2].tick_params(which='both', labelcolor='white')
    ax[2].xaxis.label.set_color('white')
    ax[2].yaxis.label.set_color('white')
    ax[2].title.set_color('white')

    # Plot 1:
    #   Loudness vs Pitch scatter plot
    ax[0].set_title("Average loudness per Note")
    ax[0].set_xlabel("dbA (log10)")
    ax[0].set_ylabel("Frequency (Hz)")
    ax[0].scatter(loudness, frequencies, marker='o', alpha=0.5)
    ax[0].set_xscale('log')


    # Plot 2:
    #   Loudness over time per pitch
    ax[1].set_title("Loudness curve per pitch")
    ax[1].set_ylabel("dbA (log10)")
    ax[1].set_xlabel("Time (frames)")
    note_names = []
    for key, value in note_dict.items():
        note_names.append(key)
        for note in value:
            ax[1].plot(note, alpha=0.3)

    def pitch_loudness(label):
        ax[1].clear()
        data = note_dict[label]
        for value in data:
            ax[1].plot(value, alpha=0.3)
        plt.tight_layout()
        canvas.draw()

    rax = plt.axes([0.82, 0.25, 0.1, 0.2])
    rax.patch.set_alpha(0.5)
    rad_btn = matplotlib.widgets.RadioButtons(rax, note_names)
    rad_btn.on_clicked(pitch_loudness)

    # Plot 3:
    # Tempo consistency over time
    ax[2].set_title("Tempo over Time")
    ax[2].set_xlabel("Performance")
    ax[2].set_ylabel("Tempo")
    ax[2].plot(tempo)
    # ax[0].scatter(loudness, frequencies, marker='o', alpha=0.5)

    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
    parent.pack(expand=True)
    # toolbar = NavigationToolbar2Tk(canvas, parent)
    # toolbar.update()

