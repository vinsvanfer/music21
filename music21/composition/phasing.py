# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         phasing.py
# Purpose:      Modeling musical phasing structures in MusicXML
#
# Authors:      Christopher Ariza
#               Michael Scott Cuthbert
#
# Copyright:    (c) 2010-11 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------

import sys
import copy
import unittest
import random

import music21
from music21 import bar
from music21 import clef
from music21 import converter
from music21 import duration
from music21 import key
from music21 import instrument
from music21 import meter
from music21 import note
from music21 import pitch
from music21 import scale
from music21 import stream
# DOENST WORK from music21 import *

def pitchedPhase(cycles=None, show=False):
    '''
    Creates a phase composition in the style of 
    1970s minimalism, but bitonally.
    
    The source code describes how this works.
    
    >>> from music21 import *
    >>> #_DOCS_SHOW composition.phasing.pitchedPhase(cycles = 4, show = True)
    
    .. image:: images/phasingDemo.*
            :width: 576

    '''

    sSrc = music21.parse("""E16 F# B c# d F# E c# B F# d c# 
                              E16 F# B c# d F# E c# B F# d c#""", '12/16')
    sPost = stream.Score()
    sPost.title = 'phasing experiment'
    sPost.insert(0, stream.Part())
    sPost.insert(0, stream.Part())

    durationToShift = duration.Duration('64th')
    increment = durationToShift.quarterLength
    if cycles == None:
        cycles = int(round(1/increment)) + 1

    for i in range(cycles):
        sPost.parts[0].append(copy.deepcopy(sSrc))
        sMod = copy.deepcopy(sSrc)
        # increment last note
        sMod.notesAndRests[-1].quarterLength += increment
        
        randInterval = random.randint(-12,12)
        #sMod.transpose(randInterval, inPlace=True)
        sPost.parts[1].append(sMod)


    if show:
        sPost.show('midi')
        sPost.show()
    else: # get musicxml
        post = sPost.musicxml



def partPari(show = True):
    '''
    generate the score of Arvo Pärt's "Pari Intervallo" algorithmically
    using music21.scale.ConcreteScale() to simulate Tintinabulation.
    '''
    s = stream.Score()
    cminor = key.Key('c')
    main = converter.parse("E-1 C D E- F G F E- D C D E- G A- F G E- F G F E- D F G c B- c G A- B- c B- A- B- G c e- d c d c B- A- G F E- F G c E- F G E- D E- F E- D C E- G F E- C F E- D C E- D C D C~ C", '4/4')
    main.__class__ = stream.Part
    main.transpose('P8', inPlace=True)
    main.insert(0, cminor)
    main.insert(0, instrument.Recorder())
    bass = copy.deepcopy(main.flat)
    for n in bass.notes:
        n.pitch.diatonicNoteNum = n.pitch.diatonicNoteNum - 9
        if (n.pitch.step == 'A' or n.pitch.step == 'B') and n.pitch.octave == 2:
            n.accidental = pitch.Accidental('natural')
        else:
            n.accidental = cminor.accidentalByStep(n.step)
        if n.offset == (2-1) * 4 or n.offset == (74-1) * 4:
            n.pitch = pitch.Pitch("C3") # exceptions to rule
        elif n.offset == (73 - 1) * 4:
            n.tie = None
            n.pitch = pitch.Pitch("C3") 
    top = copy.deepcopy(main.flat)
    main.insert(0, clef.Treble8vbClef())
    middle = copy.deepcopy(main.flat)
    cMinorArpeg = scale.ConcreteScale(pitches = ["C2","E-2","G2"])
    
    lastNote = top.notes[-1]
    top.remove(lastNote)
    for n in top:
        if 'Note' in n.classes:
            n.pitch = cMinorArpeg.next(n.pitch, stepSize=2)
            if n.offset != (73-1)*4.0:  # m. 73 is different
                n.duration.quarterLength = 3.0
                top.insert(n.offset + 3, note.Rest())
            else:
                n.duration.quarterLength = 6.0
                n.tie = None
    r1 = note.Rest(type = 'half')
    top.insertAndShift(0, r1)
    top.getElementsByClass(key.Key)[0].setOffsetBySite(top, 0)
    lastNote = middle.notes[-1]
    middle.remove(lastNote)
   
    for n in middle:
        if 'Note' in n.classes:
            n.pitch = cMinorArpeg.next(n.pitch, direction=scale.DIRECTION_DESCENDING, stepSize=2)
            if n.offset != (73-1)*4.0:  # m. 73 is different
                n.duration.quarterLength = 3.0
                middle.insert(n.offset + 3, note.Rest())
            else:
                n.duration.quarterLength = 5.0
                n.tie = None
    r2 = note.Rest(quarterLength = 3.0)
    middle.insertAndShift(0, r2)    
    middle.getElementsByClass(key.Key)[0].setOffsetBySite(middle, 0)

    ttied = top.makeMeasures().makeTies()
    mtied = middle.makeMeasures().makeTies()
    bass.makeMeasures(inPlace = True)
    main.makeMeasures(inPlace = True)
    
    s.insert(0, ttied)
    s.insert(0, main)
    s.insert(0, mtied)
    s.insert(0, bass)
    
    for p in s.parts:
        p.getElementsByClass(stream.Measure)[-1].rightBarline = bar.Barline('final')

    if show == True:
        s.show()

def pendulumMusic(show = True):
    from music21 import scale, pitch, stream, note, chord, clef, tempo, duration
    jMax = 400.0
    
    p = pitch.Pitch("C1")
    octo = scale.OctatonicScale(p)
    s = stream.Score()
    parts = [stream.Part(), stream.Part(), stream.Part(), stream.Part()]
    parts[0].insert(0, clef.Treble8vaClef())
    parts[1].insert(0, clef.TrebleClef())
    parts[2].insert(0, clef.BassClef())
    parts[3].insert(0, clef.Bass8vbClef())
    for i in range(8):
        j = 1.0
        while j < jMax:
            ps = p.ps
            if ps > 84:
                active = 0
            elif ps >= 60:
                active = 1
            elif ps >= 36:
                active = 2
            elif ps < 36:
                active = 3
            
            establishedChords = parts[active].getElementsByOffset(j)
            if len(establishedChords) == 0:
                c = chord.Chord([p])
                c.duration.type = '32nd'
                parts[active].insert(j, c)
            else:
                c = establishedChords[0]
                pitches = c.pitches
                pitches.append(p)
                c.pitches = pitches
            j += (8+(8-i))/8.0
        p = octo.next(p, stepSize = 7)
            

    parts[0].insert(0, tempo.MetronomeMark(number = 120, referent = duration.Duration(2.0)))
    for i in range(4):
        parts[i].insert(jMax + 4.0, note.Rest(quarterLength=4.0))
        parts[i].makeRests(fillGaps=True, inPlace=True)
        parts[i] = parts[i].makeNotation()
        s.insert(0, parts[i])
    
    if show == True:
        s.show('text')
        s.show('midi')
        s.show()
 

#-------------------------------------------------------------------------------
class Test(unittest.TestCase):
   
    def runTest(self):
        pass
   

    def testBasic(self, cycles=4, show=False):
        # run a reduced version
        pitchedPhase(cycles=cycles, show=show)

    def testArvoPart(self, show=False):
        partPari(show)


class TestExternal(unittest.TestCase):

    def runTest(self):
        pass
   

    def xtestBasic(self, cycles=8, show=True):
        # run a reduced version
        pitchedPhase(cycles=cycles, show=show)

    def xtestArvoPart(self, show=True):
        partPari(show)

    def testPendulumMusic(self, show=True):  
        pendulumMusic(show)
    
        
if __name__ == "__main__":
    if len(sys.argv) == 1: # normal conditions
        music21.mainTest(TestExternal)

    elif len(sys.argv) > 1:
        t = Test()
        t.testBasic(cycles=None, show=True)




#------------------------------------------------------------------------------
# eof

