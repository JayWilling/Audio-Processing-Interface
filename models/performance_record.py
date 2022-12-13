import json
import numpy as np
from json import JSONEncoder
import jsonpickle
import mir_eval.display

class Performance_encoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            if obj.flags['C_CONTIGUOUS']:
                obj_data = obj.data
            else:
                cont_obj = np.ascontiguousarray(obj)
                assert (cont_obj.flags['C_CONTIGUOUS'])
                obj_data = cont_obj.data
            return obj.tolist()
        try:
            print(obj)
            my_dict = obj.__dict__
        except TypeError:
            pass
        else:
            return my_dict
        return json.JSONEncoder.default(self, obj)

class Performance_record:

    # Filename Convention:
    # 'song or item played' - 'instrument'- 'iteration'
    # Storing instrument in the recording name makes it faster to analyse larger sets of data from one folder

    def __init__(self,
                 filename,
                 note_list,
                 sampling_rate,
                 date_time):
        self.filename = filename
        self.note_list = note_list
        self.sampling_rate = sampling_rate
        self.date_time = date_time

    def toJSON(self):
        # encoded_obj = Performance_encoder.encode(o=self)
        return json.dumps(self, default=lambda o: o.__dict__)

    def save_as_json(self):
        new_json = open(self.filename + ".json", 'w')
        # json_string = self.toJSON()
        # json_encoding = json.dumps(json_string, indent=4)
        # encoder = Performance_encoder()
        json_encoding = jsonpickle.encode(self)
        new_json.write(json_encoding)
        new_json.close()

    def get_filename(self):
        return self.filename

    def get_note_list(self):
        return self.note_list

    def get_sampling_rate(self):
        return self.sampling_rate

    def get_date_time(self):
        return self.date_time

    def show_pianoroll(self):
        intervals = []
        frequencies = []
        for note in self.note_list:
            intervals.append((note.get_onset_seconds(), note.get_offset_seconds()))
            frequencies.append(note.get_avg_frequency())
        mir_eval.display.piano_roll(intervals=intervals, pitches=frequencies)
