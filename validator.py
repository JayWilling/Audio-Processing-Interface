import pyaudio
import wave
import analysis
import models.transcriber
import os
from pathlib import Path
import sklearn

class validator:

    def bock_validation(self):
        file_location = "testing/data/Bock_Dataset-Onsets/"
        results_location = "testing/results/"

        # 1. Loop over dataset audio files
        print("Loading validation datasets...")
        default_folder = os.path.dirname(os.path.realpath(__file__)) + "/testing/data/Bock_Dataset-Onsets/audio/"
        annotations_folder = os.path.dirname(os.path.realpath(__file__)) + "/testing/data/Bock_Dataset-Onsets/annotations/"
        extension = ".flac"

        # Track true/false positives/negatives
        tp = 0
        fp = 0
        fn = 0

        # USING OS
        onsets = []

        directory = os.fsencode(default_folder)
        print(directory)

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            annotation = annotations_folder + filename.split(".")[0] + ".onsets"
            anno_path = Path(annotation)
            # Grab audio filename and see if a matching annotation exists for it
            if Path.exists(anno_path):
                if filename.endswith(".flac") or filename.endswith(".wav"):
                    # 1.1 Load audio into librosa and retrieve onsets
                    print(filename)
                    onsets = models.transcriber.extractFeatures_validation(default_folder + filename)
                    annotations = []
                    with open(annotation) as file:
                        annotations = [float(line.rstrip()) for line in file]
                    tp, fp, fn = self.onset_fmeasure(onsets, annotations, evaluation_window=0.025)


        recall = tp / (tp + fn)
        precision = tp / (tp + fp)
        fmeasure = 2 * recall * precision / (recall + precision)
        print(fmeasure)

    def onset_fmeasure(self, onsets, annotations, evaluation_window = 0.025):
        # Runner approach to comparison
        # Given 2 lists of potentially variable length
        # 1. Look at onset, compare to first annotation
        #       If falls within evaluation window add true positive
        # 2. Next onset if falls within evaluation window add false negative
        #       Else increment the annotation and continue
        onsets_validated = False
        i = 0
        j = 0

        tp = 0
        fn = 0
        fp = 0

        while (not onsets_validated):
            if (i < len(onsets) and j < len(annotations)):
                if (onsets[i] <= annotations[j] + evaluation_window and onsets[i] >= annotations[j] - evaluation_window):
                    tp += 1
                    i += 1
                    j += 1
                else:
                    if (onsets[i] > annotations[j]):
                        fn += 1
                        j += 1
                    else:
                        fp += 1
                        i += 1
            else:
                fn = len(onsets) - i + len(annotations) - j
                onsets_validated = True

        print(tp, fp, fn)
        return tp, fp, fn
