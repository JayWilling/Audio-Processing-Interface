import scipy
import numpy as np
import librosa
import pretty_midi

class Note:
    def __init__(self,
                 time,
                 onset,
                 offset,
                 duration,
                 frequencyCurve,
                 sampleRate,
                 loudness,
                 timingLabel,
                 idealOnset):
        self.time = time
        self.onset = onset
        self.offset = offset
        self.duration = duration
        self.frequencyCurve = frequencyCurve
        self.sampleRate = sampleRate
        self.loudness = loudness
        self.matching = "unknown"
        self.ground_truth = None
        self.timingLabel = timingLabel
        self.idealOnset = idealOnset

    def clean_frequency(self):
        # Note trimming
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_widths.html

        # Replace NaN values with average (Treating NaN as silence overrides the onset detection approach)
        nanIndices = np.argwhere(np.isnan(self.frequencyCurve))
        average_frequency = np.nanmean(self.frequencyCurve)
        for i in range(len(nanIndices)):
            self.frequencyCurve[nanIndices[i]] = average_frequency
        # Change offset to occurence of first NaN value (if it exists)
        # if (nanIndices.size != 0):
        #     newDuration = nanIndices[0][0]
        #     newCurve = self.frequencyCurve[0:newDuration]
        #     newTime = self.time[0:newDuration]
        #     self.set_frequencyCurve(newCurve)
        #     self.set_time(newTime)
        #     self.set_offset(self.onset + newDuration)
        #     self.set_duration(newDuration)

        # Rollback offset if pitch change is included
        # Approach 1: Step back from end of frequency comparing frequency to median value until it is relatively close
        median = np.median(self.frequencyCurve)
        i = len(self.frequencyCurve) - 1
        while i >= 0:
            x = self.frequencyCurve[i]
            if (x > median - 1 or x < median + 1):
                newDuration = i
                newOffset = self.onset + newDuration
                self.set_offset(newOffset)
                self.set_frequencyCurve(self.frequencyCurve[0:newDuration])
                self.set_time(self.time[0:newDuration])
                self.set_duration(newDuration)
                break
            i -= 1

        # Clean peaks off the frequency curve
        noteROC = []
        # If statement checking if frequency at 0 or len exceeds some amount. If it does, set to np.nan
        for j in range(len(self.frequencyCurve) - 1):
            noteROC.append(np.abs(self.frequencyCurve[j + 1] - self.frequencyCurve[j]))
        notePeaks, _ = scipy.signal.find_peaks(noteROC, height=5)
        peakWidths = scipy.signal.peak_widths(noteROC, notePeaks, rel_height=0.8)  # Not necessary
        if len(notePeaks) > 0:
            for j in range(len(notePeaks)):
                if notePeaks[j] <= 5:
                    idx = notePeaks[j] + 1
                    for x in range(idx):
                        self.frequencyCurve[x] = np.NaN
        self.calculate_name()

    def calculate_name(self):
        # nonNanFrequency = ~np.isnan(self.frequencyCurve)
        # print(nonNanFrequency)
        avg = np.nanmean(self.frequencyCurve)
        # print("Average: ", avg)
        # print("Freq Curve: ", self.frequencyCurve)
        # Only calculate note names for notes, not the rests as well
        if avg > 0:
            # noteDurations.append(segmentedTimes[i][len(segmentedTimes[i]) - 1] - segmentedTimes[i][0])
            note = librosa.hz_to_note(avg, cents=True, unicode=False)
            name = []
            cents = 0
            if "+" in note:
                name = note.split("+")
                cents = + int(name[1])
            elif "-" in note:
                name = note.split("-")
                cents = - int(name[1])
            self.name = name[0]
            self.cents = cents
        elif avg == np.nan:
            self.name = 'Rest'
        else:
            self.name = ''
            self.cents = 0

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_time(self):
        return self.time

    def set_time(self, time):
        self.time = time

    def get_onset(self):
        return self.onset

    def get_onset_seconds(self):
        return librosa.frames_to_time(self.get_onset(), sr=self.sampleRate)

    def get_offset_seconds(self):
        return librosa.frames_to_time(self.get_offset(), sr=self.sampleRate)

    def set_onset(self, onset):
        self.onset = onset

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset

    def get_duration(self):
        return self.duration

    def get_duration_seconds(self):
        return librosa.frames_to_time(self.get_duration(), sr=self.sampleRate)

    def set_duration(self, duration):
        self.duration = duration

    def get_frequencyCurve(self):
        return self.frequencyCurve

    def set_frequencyCurve(self, frequencyCurve):
        self.frequencyCurve = frequencyCurve

    def get_avg_frequency(self):
        return np.nanmean(self.frequencyCurve)

    def get_median_frequency(self):
        return np.nanmedian(self.frequencyCurve)

    def get_midi_note(self):
        return round(librosa.hz_to_midi(self.get_median_frequency()))

    def get_cents(self):
        return self.cents

    def set_cents(self, cents):
        self.cents = cents

    def get_avg_loudness(self):
        return np.nanmean(self.loudness)

    '''
    Timing labels are used to identify each given note as being on-time, early, or late with respect to the tempo
    provided, and each subsequent note. This is not to outline discrepancies in timing with respect to the groundtruth.
    It is expected that the user will identify errors in timing when reviewing visual feedback.
    
    As such, this approach emphasises: Tempo first, individual note duration second.
    '''

    def get_timing_label(self):
        return self.timingLabel

    def get_ideal_onset(self):
        return self.idealOnset

    def get_ideal_onset_seconds(self):
        return librosa.frames_to_time(self.get_ideal_onset(), sr=self.sampleRate)

    '''
    Matching used to denote the correctness of a given note with respect to the ground truth
    Potential values include:
        - Correct       -> Pitch of the note was successfully matched
        - Substitute    -> Pitch was incorrect
        - Insertion     -> Unexpected note played
        - Missed        -> Note in ground truth could not be matched
    '''
    def set_matching(self, new_matching, ground_truth = None):
        self.matching = new_matching
        self.ground_truth = ground_truth

    def get_matching(self):
        return self.matching