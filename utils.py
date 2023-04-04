from pathlib import Path
import jsonpickle
import os
import ntpath
from multiprocessing.pool import ThreadPool

import numpy as np
import pretty_midi

import models.transcriber as transcriber
from models.performance_record import Performance_record
import models.groundtruth_builder as groundtruth_builder

""" Returns JSON counterpart of given .wav file. Inclusive of the file extension"""
def get_performance_record(filename):
    name = filename.split('.wav')[0]
    file = Path(name + ".json")
    new_filename = name

    groundtruth_builder.create_gt_midis()

    print("Filename : " + filename)

    if not (Path.exists(file)):
        print("Transcribing recording")
        c_time = os.path.getctime(filename)
        print(c_time)
        midi_name_head, midi_name_tail = ntpath.split(filename)
        midi_name_tail = midi_name_tail.split('-')[0]

        print("Midi tail: " + midi_name_tail)

        pool = ThreadPool(processes=1)

        async_result = pool.apply_async(transcriber.extractFeatures, kwds={'filename': filename})

        # Build the corresponding midi file using the performance tempo
        if async_result.get()[1] != 0:
            groundtruth_builder.create_gt_midis(async_result.get()[1])
        else:
            groundtruth_builder.create_gt_midis()
        gt_notes = pool.apply_async(transcription_alignment, kwds={'note_list': async_result.get()[0], 'midi_name': midi_name_tail})
        print(gt_notes.get()[0])

        new_performance = Performance_record(filename=name,
                                             note_list=gt_notes.get()[0],
                                             gt_note_list=gt_notes.get()[1],
                                             missed_note_indexes=gt_notes.get()[2],
                                             sampling_rate=44100,
                                             date_time=c_time,
                                             tempo=async_result.get()[1])
        new_performance.save_as_json()
        print("Transcription saved")
        return new_performance
        # Create the JSON file and return the performance record
    f = open(name + ".json")
    print("File available")
    return jsonpickle.decode(f.read())

def get_test_files():
    print("Loading validation datasets...")
    default_folder = os.path.dirname(os.path.realpath(__file__)) + "/audio/recordings/"
    extension = ".flac"

    directory = os.fsencode(default_folder)

    for file in os.listdir(directory):
        filename = os.fsencode(file)
        if filename.endswith(".flac") or filename.endswith(".wav"):
            print("Doing stuff")

def get_multiple_performances(song_name, instrument):
    print("Loading performances...")
    # default_folder = "audio/recordings/"

    default_folder = os.path.dirname(os.path.realpath(__file__)) + "/audio/recordings/"
    extension = ".wav"
    base_path = default_folder + instrument + "-" + song_name
    i = 0

    # Initialise list of performance objects
    performances = []

    # Check if file exists
    file = Path(base_path + extension)
    new_filename = base_path
    print(str(file))

    while Path.exists(file):
        print("Getting performance")
        performances.append(get_performance_record(new_filename + ".wav"))
        # Increment the file name by 1
        i += 1
        # While each successive filename (including i) does not exist, then save the next filename
        new_filename = base_path + "-" + str(i)
        file = Path(new_filename + extension)
        print("New filename : ", new_filename)

    print("Performances loaded")
    return performances

def transcription_alignment(note_list, midi_name = "testing/midi_files/bflatmajor"):
    # MAKE SURE WE'RE USING PRETTY MIDI FOR GROUNDTRUTH
    #   - A pretty_midi note has the following:
    #       note.start
    #       note.end
    #       note.pitch  -> This is a midi note value
    #   - We can convert the transcribed note frequencies to midi
    #       If the midi notes are off, maybe we check median rather than mean
    #       We can also compare the two by difference rather than a direct comparison of notes
    #   - No need to construct two sequences/arrays/strings
    #       The objects will already be in order
    # :)
    groundtruth = pretty_midi.PrettyMIDI("testing/midi_files/" + midi_name + ".mid")
    # notes = [58, 60, 62, 63, 65, 67, 69, 70, 69, 67, 65, 63, 62, 60, 58]

    # 1. Calculate the Levenshtein cost matrix
    gt_note_list = groundtruth.instruments[0].notes
    missed_notes = []

    transcription_length = len(note_list) + 1
    groundtruth_length = len(gt_note_list) + 1
    print(transcription_length, groundtruth_length)

    #       Initialise n*m matrix to 0
    cost_matrix = np.zeros((groundtruth_length, transcription_length))

    #       Set the initial row to incrementing values
    for i in range(groundtruth_length):
        cost_matrix[i, 0] = i

    for j in range(transcription_length):
        cost_matrix[0, j] = j

    for j in range(1, transcription_length):
        for i in range(1, groundtruth_length):
            substitution_cost = 0
            print(i, j)
            if note_list[j-1].get_midi_note() != gt_note_list[i-1].pitch:
                substitution_cost = 1

            substitution = cost_matrix[i-1, j-1] + substitution_cost
            match = cost_matrix[i-1, j-1]
            insertion = cost_matrix[i, j-1] + 1
            deletion = cost_matrix[i - 1, j] + 1

            cost_matrix[i, j] = min(substitution, insertion, deletion)

            minimum = min(substitution, insertion, deletion)

    # 2. Perform a second pass over the cost matrix to identify the correct and incorrect notes by tracing the path

    print("Performance Alignment:")
    print(cost_matrix)
    transcription_notes = ""
    midi_notes = ""
    for i in range(transcription_length-1):
        transcription_notes += ", " + str(note_list[i].get_midi_note())
    print(transcription_notes)
    for i in range(groundtruth_length-1):
        midi_notes += ", " + str(gt_note_list[i].pitch)
    print(midi_notes)

    # Mark the first note:
    # Consider the first note was missed. Then the first note is actually the second


    i, j = groundtruth_length-1, transcription_length-1
    previous_cost = cost_matrix[0, 0]

    checked = False
    print("Minimums: ")
    while not checked:
        current = cost_matrix[i, j]
        diagonal = cost_matrix[i - 1, j - 1]
        insertion = cost_matrix[i, j - 1]
        deletion = cost_matrix[i - 1, j]

        minimum = min(diagonal, insertion, deletion)
        print(i, ", ", j)


        if minimum == diagonal:
            if diagonal < current:
                # mark notes[j] as correct
                note_list[j-1].set_matching("Substitute", i-1)
            else:
                # mark notes[j] pitch as incorrect
                note_list[j-1].set_matching("Correct", i-1)
            j -= 1
            i -= 1
        elif minimum == insertion:
            note_list[j-1].set_matching("Insertion")
            j -= 1
        # WE WILL HANDLE MISSED NOTES ONCE THE ABOVE IS WORKING
        elif minimum == deletion:
            missed_notes.append(i-1)
            i -= 1

        if i == 0 and j == 0:
            checked = True

    return note_list, gt_note_list, missed_notes
