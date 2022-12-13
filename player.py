import pyaudio
import wave
from threading import Lock, Thread

class player:
    chunk = 1024

    def __init__(self, file):
        """ Init audio stream """
        self.filename = file
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True
        )
        self.playing = False

    def start(self):
        """ Play entire file """

        # Load the file
        self.wf = wave.open(self.filename, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True
        )

        # Start playing
        self.stream.start_stream()
        self.playing = True
        data = self.wf.readframes(self.chunk)
        while data != b'':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def stop(self):
        """ Graceful shutdown """
        self.playing = False
        self.stream.close()
        self.p.terminate()

    def set_filename(self, filename):
        self.filename = filename
