#!/usr/bin/python

'''tinyNotation -- a simple way of specifying single line melodies
that uses a notation somewhat similar to Lilypond but with WAY fewer 
examples.  Originally developed to notate trecento (medieval Italian)
music, but it's pretty useful for a lot of short examples.  

tinyNotation is not meant to expand to cover every single case.  Instead
it is meant to be subclassible to extend to the cases *your* project needs.
See for instance the harmony examples in HarmonyNotationLine and HarmonyNotationNote
or the Trecento specific examples in trecento/cadencebook.py
'''

import unittest, doctest
import copy
from re import compile, search, match
import collections

import music21
import music21.note
import music21.duration

from music21 import common
from music21 import stream
from music21 import notationMod
from music21 import meter

def lineToStream(line, timeSignature = None):
    tnl = TinyNotationLine(line, timeSignature)
    return tnl.stream

class TinyNotationLine(object):
    '''A TinyNotationLine begins as a string representation similar to Lilypond format
    but simplified somewhat.  This object holds the string representation and stores a
    Stream representation at .stream.
    
    example in 3/4:
    >>> stream1 = TinyNotationLine("E4 r f# g=lastG trip{b-8 a g} c", "3/4").stream
    >>> stream1.getElementById("lastG").step
    'G'
    >>> stream1.notes[1].isRest
    True
    >>> stream1.notes[0].octave
    3
    
    '''

    TRIP    = compile('trip\{')
    QUAD    = compile('quad\{')
    ENDBRAC = compile('\}')
    
    def __init__(self, stringRep = "", timeSignature = None):
        self.stringRep = stringRep
        noteStrs = self.stringRep.split()

        if (timeSignature is None):
            barDuration = music21.duration.Duration()
            barDuration.type = "whole"    ## assume 4/4
        elif (hasattr(timeSignature, "barDuration")): # is a TimeSignature object
            barDuration = timeSignature.barDuration
        else: # is a string
            timeSignature = meter.TimeSignature(timeSignature)
            barDuration = timeSignature.barDuration

        noteList = []
        dict1 = { 'inTrip': False,
                  'inQuad': False,
                  'beginTuplet': False,
                  'endTuplet': False,
                  'lastDuration': None, 
                  'barDuration': barDuration }

        for thisNoteStr in noteStrs:
            if self.TRIP.match(thisNoteStr):
                thisNoteStr = self.TRIP.sub('', thisNoteStr)
                dict1['inTrip'] = True
                dict1['beginTuplet'] = True
            elif self.QUAD.match(thisNoteStr):
                thisNoteStr = self.QUAD.sub('', thisNoteStr)
                dict1['inQuad'] = True
                dict1['beginTuplet'] = True
            elif self.ENDBRAC.search(thisNoteStr):
                thisNoteStr = self.ENDBRAC.sub('', thisNoteStr)
                dict1['endTuplet'] = True

            tN = None
            try:
                tN = self.getNote(thisNoteStr, dict1)
            except music21.duration.DurationException, (value):
                raise music21.duration.DurationException(str(value) + " in context " + str(thisNoteStr))
#            except Exception, (value):
#                raise Exception(str(value) + "in context " + str(thisNoteStr) + ": " + str(stringRep) )
            
            noteList.append(tN.note)

            if dict1['endTuplet'] == True:
                dict1['endTuplet'] = False
                
                if dict1['inTrip'] == True:
                    dict1['inTrip'] = False
                elif dict1['inQuad'] == True:
                    dict1['inQuad'] = False
                else:
                    raise TinyNotationException("unexpected end bracket in TinyNotationLine")

            dict1['beginTuplet'] = False

        self.stream = stream.Stream()
        if timeSignature is not None and hasattr(timeSignature, "barDuration"):
            self.stream.append(timeSignature)
        for thisNote in noteList:
            self.stream.append(thisNote)
        
    def getNote(self, stringRep, storedDict = {}):
        '''
        called out so as to be subclassable
        '''
        return TinyNotationNote(stringRep, storedDict)

class TinyNotationNote(object):
    ''' 
    >>> tcN = TinyNotationNote("AA-4.~=aflat_hel-")
    >>> note1 = tcN.note
    >>> note1.name
    'A-'
    >>> note1.octave
    2
    >>> note1.lyric
    'hel-'
    >>> note1.id
    'aflat'
    '''
    
    REST    = compile('r')
    OCTAVE2 = compile('([A-G])[A-G]')
    OCTAVE3 = compile('([A-G])')
    OCTAVE5 = compile('([a-g])\'') 
    OCTAVE4 = compile('([a-g])')
    EDSHARP = compile('\(\#\)')
    EDFLAT  = compile('\(\-\)')
    EDNAT   = compile('\(n\)')
    SHARP   = compile('^[A-Ga-g]+\#')  # simple notation has 
    FLAT    = compile('^[A-Ga-g]+\-')  # no need for double sharps etc
    TYPE    = compile('(\d+)')
    TIE     = compile('.\~') # not preceding ties
    PRECTIE = compile('\~')  # front ties
    DBLDOT  = compile('\.\.') 
    DOT     = compile('\.')
    ID_EL   = compile('\=([A-Za-z0-9]*)')
    LYRIC   = compile('\_(.*)')

    debug = False

    def __init__(self, stringRep, storedDict = common.defHash(default = False)):
        noteObj = None
        storedtie = None
        
        if self.PRECTIE.match(stringRep):
            if self.debug is True: print "FOUND FRONT TIE"
            stringRep = self.PRECTIE.sub("", stringRep)
            storedtie = music21.note.Tie("stop")

        x = self.customPitchMatch(stringRep, storedDict)
        
        if x is not None:
            noteObj = x
        elif (self.REST.match(stringRep) is not None): # rest
            noteObj = music21.note.Rest()
        elif (self.OCTAVE2.match(stringRep)): # BB etc.
            noteObj = self._getPitch(self.OCTAVE2.match(stringRep), 2)
        elif (self.OCTAVE3.match(stringRep)):
            noteObj = self._getPitch(self.OCTAVE3.match(stringRep), 3)
        elif (self.OCTAVE5.match(stringRep)): # must match octave 5 then 4!
            noteObj = self._getPitch(self.OCTAVE5.match(stringRep), 5)
        elif (self.OCTAVE4.match(stringRep)): 
            noteObj = self._getPitch(self.OCTAVE4.match(stringRep), 4)
        else:
            raise TinyNotationException("could not get pitch information from " + str(stringRep))

        if storedtie: noteObj.tie = storedtie

        ## get duration
        usedLastDuration = False
        
        if (self.TYPE.search(stringRep)):
            typeNum = self.TYPE.search(stringRep).group(1)
            if (typeNum == "0"): ## special case = full measure + fermata
                noteObj.duration = storedDict['barDuration']
                newFerm = notationMod.Fermata()
                noteObj.notations.append(newFerm)
            else:
                noteObj.duration.type = music21.duration.typeFromNumDict[int(typeNum)]
        else:
            noteObj.duration = copy.deepcopy(storedDict['lastDuration'])
            usedLastDuration = True
            if (noteObj.duration.tuplets):
                noteObj.duration.tuplets[0].type = ""
                # if it continues a tuplet it cannot be start; maybe end

        ## get dots; called out because subclassable
        self.getDots(stringRep, noteObj)
        
        ## get ties
        if self.TIE.search(stringRep):
            if self.debug is True: print "FOUND TIE"
            noteObj.tie = music21.note.Tie("start")
        
        ## use dict to set tuplets
        if (storedDict['inTrip'] == True or storedDict['inQuad'] == True) and usedLastDuration == False:
            newTup = music21.duration.Tuplet()
            newTup.durationActual.type = noteObj.duration.type
            newTup.durationNormal.type = noteObj.duration.type
            if storedDict['inQuad'] == True:
                newTup.numNotesActual = 4.0
                newTup.numNotesNormal = 3.0            
            if storedDict['beginTuplet']:
                newTup.type = "start"
            noteObj.duration.appendTuplet(newTup)

        if (storedDict['inTrip'] == True and storedDict['endTuplet']):
            noteObj.duration.tuplets[0].type = "stop"
        if (storedDict['inQuad'] == True and storedDict['endTuplet']):
            noteObj.duration.tuplets[0].type = "stop"
        
        storedDict['lastDuration'] = noteObj.duration

        ## get accidentals
        if (isinstance(noteObj, music21.note.Note)):
            if (self.EDSHARP.search(stringRep)): # must come before sharp
                acc1 = music21.note.Accidental("sharp")
                noteObj.editorial.ficta = acc1
                noteObj.editorial.misc['pmfc-ficta'] = acc1
            elif (self.EDFLAT.search(stringRep)): # must come before flat
                acc1 = music21.note.Accidental("flat")
                noteObj.editorial.ficta = acc1
                noteObj.editorial.misc['pmfc-ficta'] = acc1
            elif (self.EDNAT.search(stringRep)):
                acc1 = music21.note.Accidental("natural")
                noteObj.editorial.ficta = acc1
                noteObj.editorial.misc['pmfc-ficta'] = acc1
                noteObj.accidental = acc1
            elif (self.SHARP.search(stringRep)):
                noteObj.accidental = "sharp"
            elif (self.FLAT.search(stringRep)):
                noteObj.accidental = "flat"

        self.customNotationMatch(noteObj, stringRep, storedDict)

        if self.ID_EL.search(stringRep):
            noteObj.id = self.ID_EL.search(stringRep).group(1)
        
        if self.LYRIC.search(stringRep):
            noteObj.lyric = self.LYRIC.search(stringRep).group(1)
            
        self.note = noteObj

    def getDots(self, stringRep, noteObj):
        if (self.DBLDOT.search(stringRep)):
            noteObj.duration.dots = 2
        elif (self.DOT.search(stringRep)):
            noteObj.duration.dots = 1
        
    def _getPitch(self, matchObj, octave):
        noteObj = music21.note.Note()
        noteObj.step = matchObj.group(1).upper()
        noteObj.octave = octave
        return noteObj

    def customPitchMatch(self, stringRep, storedDict):
        '''
        method to create a note object in sub classes of tiny notation.  
        Should return a Note-like object or None
        '''
        return None

    def customNotationMatch(self, m21NoteObject, stringRep, storedDict):
        return None

class HarmonyLine(TinyNotationLine):
    '''
    example of subclassing TinyNotationLine to include a possible harmonic representation of the note
    '''
    def getNote(self, stringRep, storedDict = {}):
        return HarmonyNote(stringRep, storedDict)

class HarmonyNote(TinyNotationNote):
    HARMONY   = compile('\*(.*)\*')
    
    def customNotationMatch(self, m21NoteObject, stringRep, storedDict):
        if self.HARMONY.search(stringRep):
            harmony = self.HARMONY.search(stringRep).group(1)
            m21NoteObject.editorial.misc['harmony'] = harmony


class TinyNotationException(Exception):
    pass

###### test routines
class Test(unittest.TestCase):

    def runTest(self):
        pass
    
    def testTinyNotationNote(self):
        cn = TinyNotationNote('AA-4.~')
        a = cn.note
        self.assertEqual(a.compactNoteInfo(), "A- A 2 flat (Tie: start) quarter 1.5")
    
    def testTinyNotationLine(self):
        tl = TinyNotationLine('e2 f#8 r f trip{g16 f e-} d8 c B trip{d16 c B}')
        st = tl.stream
        ret = ""
        for thisNote in st:
            ret += thisNote.compactNoteInfo() + "\n"
        
        d1 = st.duration
        l1 = d1.quarterLength
        self.assertAlmostEquals(st.duration.quarterLength, 6.0)
        
        ret += "Total duration of Stream: " + str(st.duration.quarterLength) + "\n"
        canonical = '''
E E 4 half 2.0
F# F 4 sharp eighth 0.5
rest eighth 0.5
F F 4 eighth 0.5
G G 4 16th 0.166666666667 & is a tuplet (in fact STARTS the tuplet)
F F 4 16th 0.166666666667 & is a tuplet
E- E 4 flat 16th 0.166666666667 & is a tuplet (in fact STOPS the tuplet)
D D 4 eighth 0.5
C C 4 eighth 0.5
B B 3 eighth 0.5
D D 4 16th 0.166666666667 & is a tuplet (in fact STARTS the tuplet)
C C 4 16th 0.166666666667 & is a tuplet
B B 3 16th 0.166666666667 & is a tuplet (in fact STOPS the tuplet)
Total duration of Stream: 6.0
'''
        self.assertTrue(common.basicallyEqual(canonical, ret))
    
    def testConvert(self):
        st1 = lineToStream('e2 f#8 r f trip{g16 f e-} d8 c B trip{d16 c B}')
        self.assertEqual(st1[1].offset, 2.0) 
        self.assertTrue(isinstance(st1[2], music21.note.Rest))     

    def testHarmonyNotation(self):
        hnl = HarmonyLine("c2*F*_Mi- c_chelle r4*B-m7* d-_ma A-2_belle G4*E-*_these c_are A-_words G_that F*Ddim*_go A-_to- Bn_geth- A-_er", "4/4")
        nst1 = hnl.stream.notes
        self.assertEqual(nst1[0].step, "C")
        self.assertEqual(nst1[0].editorial.misc['harmony'], "F")
        self.assertEqual(nst1[0].lyric, "Mi-")
        self.assertEqual(nst1[2].isRest, True)
        self.assertEqual(nst1[5].name, "G")
        self.assertEqual(nst1[7].name, "A-")
    
class TestExternal(unittest.TestCase):    

    def xtestCreateEasyScale(self):
        myScale = "d8 e f g a b"
        time1 = meter.TimeSignature("3/4")
        tinyNotation = TinyNotationLine(myScale, time1)
        s1 = tinyNotation.stream
        s1.lily.showPDF()
    
    def testMusicXMLExt(self):
        cadB = lineToStream("c8 B- B- A c trip{d16 c B-} A8 B- A0", "2/4")
#        last = cadB[10]
#        cadB = stream.Stream()
#        n1 = music21.note.Note()
#        n1.duration.type = "whole"
#        cadB.append(n1)
#        cadB.lily.showPDF()
        cadB.show()


if __name__ == "__main__":
    music21.mainTest(TestExternal, Test)