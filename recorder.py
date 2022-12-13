import os
from multiprocessing.pool import ThreadPool

import librosa
import pyaudio as pyaudio
import time
from pathlib import Path
import wave as wave

import models.transcriber as transcriber
from models.performance_record import Performance_record
import utils

class recorder:
    def __init__(self,
                 wavfile,
                 chunksize=8192,
                 dataformat=pyaudio.paInt16,
                 channels=2,
                 rate=44100):
        self.filename = wavfile
        self.chunksize = chunksize
        self.dataformat = dataformat
        self.channels = channels
        self.rate = rate
        self.recording = False
        self.pa = pyaudio.PyAudio()

    def start(self, performance_name, instrument):
        # we call start and stop from the keyboard listener, so we use the asynchronous
        # version of pyaudio streaming. The keyboard listener must regain control to
        # begin listening again for the key release.
        if not self.recording:
            self.recording = True
            time.sleep(0.5)
            # performance_name = input("What piece are you playing? (No spaces or special characters)\n")
            # instrument = input("What instrument are you using?\n")

            default_folder = "audio/recordings/"
            extension = ".wav"
            base_path = default_folder + performance_name + "-" + instrument
            self.filename = base_path
            i = 0

            # Check if file exists
            file = Path(base_path + extension)
            new_filename = base_path
            while Path.exists(file):
                # If file exists, increment i by 1
                i += 1
                # While each successive filename (including i) does not exists, then save the next filename
                new_filename = base_path + "-" + str(i)
                file = Path(new_filename + extension)

            print(str(file))
            self.filename = new_filename

            self.wf = wave.open(str(file), 'wb')
            self.wf.setnchannels(self.channels)
            self.wf.setsampwidth(self.pa.get_sample_size(self.dataformat))
            self.wf.setframerate(self.rate)

            def callback(in_data, frame_count, time_info, status):
                # file write should be able to keep up with audio data stream (about 1378 Kbps)
                self.wf.writeframes(in_data)
                return (in_data, pyaudio.paContinue)

            self.stream = self.pa.open(format=self.dataformat,
                                       channels=self.channels,
                                       rate=self.rate,
                                       input=True,
                                       stream_callback=callback)
            self.stream.start_stream()
            print('Recording started')
            return self.filename

    def stop(self):
        print(self.recording)
        if self.recording:
            self.stream.stop_stream()
            self.stream.close()
            self.wf.close()

            self.recording = False
            print('Recording finished')

    def analyse_audio(self):
        print("Analysing recording - Please wait")
        utils.get_performance_record(str(self.filename) + ".wav")
        # c_time = os.path.getctime(self.filename + ".wav")
        # print(c_time)
        #
        # pool = ThreadPool(processes=1)
        #
        # async_result = pool.apply_async(transcriber.extractFeatures, (y, sr))
        #
        # new_performance = Performance_record(filename=self.filename,
        #                                      note_list=async_result.get(),
        #                                      sampling_rate=44100,
        #                                      date_time=c_time)
        # new_performance.save_as_json()
        # print("Analysis saved")