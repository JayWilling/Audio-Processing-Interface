from pathlib import Path
import jsonpickle
import os
from multiprocessing.pool import ThreadPool

import models.transcriber as transcriber
from models.performance_record import Performance_record

""" Returns JSON counterpart of given .wav file. Inclusive of the file extension"""
def get_performance_record(filename):
    name = filename.split('.wav')[0]
    file = Path(name + ".json")
    new_filename = name

    if not (Path.exists(file)):
        print("Transcribing recording")
        c_time = os.path.getctime(filename)
        print(c_time)

        pool = ThreadPool(processes=1)

        async_result = pool.apply_async(transcriber.extractFeatures, kwds={'filename': filename})

        new_performance = Performance_record(filename=name,
                                             note_list=async_result.get(),
                                             sampling_rate=44100,
                                             date_time=c_time)
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
        performances.append(get_performance_record(new_filename + ".wav"))
        # Increment the file name by 1
        i += 1
        # While each successive filename (including i) does not exist, then save the next filename
        new_filename = base_path + "-" + str(i)
        file = Path(new_filename + extension)

    print("Performances loaded")
    return performances
