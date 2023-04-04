import music21 as m21


def create_gt_midis(tempo = 80):
    # Define the tempo for each midi, default to 80
    mm = m21.tempo.MetronomeMark(number=tempo)

    # Cmajor Scale
    cmajor = m21.stream.Stream()
    cmajor = cmajor_midi(cmajor, mm)
    save_as_midi(cmajor, "cmajorscale")

    # Chromatic Scale starting on C
    cchromatic = m21.stream.Stream()
    cchromatic = chromatic_midi(cchromatic, mm)
    save_as_midi(cchromatic, "chromaticscale")

    # cmajor = m21.scale.MajorScale('B-3')
    # GEX = m21.musicxml.m21ToXml.GeneralObjectExporter()
    # m = GEX.fromStream(cmajor)
    # m.show('text')

    # print("Saving scale ground truth...")
    # cmajor.write('musicxml', fp='../testing/midi_files/cmajor.xml')
    # cmajor.write('midi', fp='../testing/midi_files/cmajor.mid')
    # print("Scale Saved.")

    # for note in cmajor:
    #     print(note.step)


def save_as_midi(m21_obj, filename):
    print("Saving " + filename + " ground truth...")
    m21_obj.write('midi', fp='testing/midi_files/' + filename + '.mid')
    print("New MIDI, " + filename + " saved.")


def load_gt(filename):
    m21.converter.parse('/../testing/midi_files/')

def cmajor_midi(cmajor, metronome):

    # C Major Scale

    cmajor.append(metronome)
    cmajor.append(m21.note.Note('C4', quarterLength=2.0))
    cmajor.append(m21.note.Note('D4'))
    cmajor.append(m21.note.Note('E4'))
    cmajor.append(m21.note.Note('F4'))
    cmajor.append(m21.note.Note('G4'))
    cmajor.append(m21.note.Note('A4'))
    cmajor.append(m21.note.Note('B4'))
    cmajor.append(m21.note.Note('C5', quarterLength=2.0))
    cmajor.append(m21.note.Note('B4'))
    cmajor.append(m21.note.Note('A4'))
    cmajor.append(m21.note.Note('G4'))
    cmajor.append(m21.note.Note('F4'))
    cmajor.append(m21.note.Note('E4'))
    cmajor.append(m21.note.Note('D4'))
    cmajor.append(m21.note.Note('C4', quarterLength=4.0))

    cmajor.append(m21.note.Note('C4'))
    cmajor.append(m21.note.Note('E4'))
    cmajor.append(m21.note.Note('G4'))
    cmajor.append(m21.note.Note('C5'))
    cmajor.append(m21.note.Note('B4'))
    cmajor.append(m21.note.Note('G4'))
    cmajor.append(m21.note.Note('F4'))
    cmajor.append(m21.note.Note('E4'))
    cmajor.append(m21.note.Note('D4'))
    cmajor.append(m21.note.Note('C4', quarterLength=4.0))
    return cmajor

def chromatic_midi(cchromatic, metronome):
    cchromatic.append(metronome)
    cchromatic.append(m21.note.Note('C4'))
    cchromatic.append(m21.note.Note('C#4'))
    cchromatic.append(m21.note.Note('D4'))
    cchromatic.append(m21.note.Note('D#4'))
    cchromatic.append(m21.note.Note('E4'))
    cchromatic.append(m21.note.Note('F4'))
    cchromatic.append(m21.note.Note('F#4'))
    cchromatic.append(m21.note.Note('G4'))
    cchromatic.append(m21.note.Note('G#4'))
    cchromatic.append(m21.note.Note('A4'))
    cchromatic.append(m21.note.Note('A#4'))
    cchromatic.append(m21.note.Note('B4'))
    cchromatic.append(m21.note.Note('C5', quarterLength=4.0))
    cchromatic.append(m21.note.Note('C#4'))
    cchromatic.append(m21.note.Note('B4'))
    cchromatic.append(m21.note.Note('B-4'))
    cchromatic.append(m21.note.Note('A4'))
    cchromatic.append(m21.note.Note('A-4'))
    cchromatic.append(m21.note.Note('G4'))
    cchromatic.append(m21.note.Note('G-4'))
    cchromatic.append(m21.note.Note('F4'))
    cchromatic.append(m21.note.Note('E4'))
    cchromatic.append(m21.note.Note('E-4'))
    cchromatic.append(m21.note.Note('D4'))
    cchromatic.append(m21.note.Note('D-4'))
    cchromatic.append(m21.note.Note('C4', quarterLength=4.0))
    return cchromatic

def interval_studies_midi(interval11, metronome):
    interval11.append(m21.note.Note('C4', quarterLength=1.0))
    interval11.append(m21.note.Note('F4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('G4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('A4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('B-4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('C5', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('D5', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('E5', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('F5', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('E5', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('D5', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('C5', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('B-4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('A4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('G4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('F4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('E4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))

    interval11.append(m21.note.Note('F4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('A4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('C5', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('A4', quarterLength=0.5))
    interval11.append(m21.note.Note('C4', quarterLength=0.5))
    interval11.append(m21.note.Note('F4', quarterLength=3.0))

def danish_roll_midi(danishroll, metronome):
    danishroll.append(m21.note.Note('G4'))
    danishroll.append(m21.note.Note('A4'))
    danishroll.append(m21.note.Note('B4'))
    danishroll.append(m21.note.Note('C5'))
    danishroll.append(m21.note.Note('D5', quarterLength=2.0))
    danishroll.append(m21.note.Note('B4'))
    danishroll.append(m21.note.Note('D5'))
    danishroll.append(m21.note.Note('C5', quarterLength=2.0))
    danishroll.append(m21.note.Note('A4'))
    danishroll.append(m21.note.Note('C5'))
    danishroll.append(m21.note.Note('B4', quarterLength=2.0))
    danishroll.append(m21.note.Note('B4'))
    danishroll.append(m21.note.Note('A4'))
    danishroll.append(m21.note.Note('G4'))
    danishroll.append(m21.note.Note('A4'))
    danishroll.append(m21.note.Note('B4'))
    danishroll.append(m21.note.Note('C5'))
    danishroll.append(m21.note.Note('D5', quarterLength=2.0))
    danishroll.append(m21.note.Note('B4'))
    danishroll.append(m21.note.Note('D5'))
    danishroll.append(m21.note.Note('C4'))
    danishroll.append(m21.note.Note('A4'))
    danishroll.append(m21.note.Note('F4'))
    danishroll.append(m21.note.Note('A4'))
    danishroll.append(m21.note.Note('G4', quarterLength=4.0))
