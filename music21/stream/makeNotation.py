# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Name:         makeNotation.py
# Purpose:      functionality for manipulating streams
#
# Authors:      Michael Scott Cuthbert
#               Christopher Ariza
#               Evan Lynch
#
# Copyright:    Copyright © 2008-2013 Michael Scott Cuthbert and the music21
#               Project
# License:      LGPL, see license.txt
#------------------------------------------------------------------------------

import copy
import unittest

from music21 import common
from music21 import defaults
from music21 import duration
from music21 import environment
from music21 import meter
from music21 import note

environLocal = environment.Environment(__file__)


#------------------------------------------------------------------------------


def makeBeams(s, inPlace=False):
    '''
    Return a new Measure, or Stream of Measures, with beams applied to all
    notes. Measures with Voices will process voices independently.

    In the process of making Beams, this method also updates tuplet types.
    This is destructive and thus changes an attribute of Durations in
    Notes.

    Note that `makeBeams()` is automatically called in show('musicxml') and
    other formats if there is no beaming information in the piece (see
    `haveBeamsBeenMade`).

    If `inPlace` is True, this is done in-place; if `inPlace` is False,
    this returns a modified deep copy.

    .. note: Before Version 1.6, `inPlace` default was `True`; now `False`
             like most `inPlace` options in music21.

    See :meth:`~music21.meter.TimeSignature.getBeams` for the algorithm used.

    ::

        >>> from music21 import meter
        >>> from music21 import stream

    ::

        >>> aMeasure = stream.Measure()
        >>> aMeasure.timeSignature = meter.TimeSignature('4/4')
        >>> aNote = note.Note()
        >>> aNote.quarterLength = .25
        >>> aMeasure.repeatAppend(aNote,16)
        >>> bMeasure = aMeasure.makeBeams(inPlace=False)

    ::

        >>> for i in range(0, 4):
        ...   print i, bMeasure.notes[i].beams
        0 <music21.beam.Beams <music21.beam.Beam 1/start>/<music21.beam.Beam 2/start>>
        1 <music21.beam.Beams <music21.beam.Beam 1/continue>/<music21.beam.Beam 2/stop>>
        2 <music21.beam.Beams <music21.beam.Beam 1/continue>/<music21.beam.Beam 2/start>>
        3 <music21.beam.Beams <music21.beam.Beam 1/stop>/<music21.beam.Beam 2/stop>>

    OMIT_FROM_DOCS
    TODO: inPlace=False does not work in many cases
    '''
    from music21 import stream

    #environLocal.printDebug(['calling Stream.makeBeams()'])
    if not inPlace:  # make a copy
        returnObj = copy.deepcopy(s)
    else:
        returnObj = s

    #if s.isClass(Measure):
    if 'Measure' in s.classes:
    #if s.isClassOrSubclass('Measure'):
        mColl = []  # store a list of measures for processing
        mColl.append(returnObj)
    elif len(s.getElementsByClass('Measure')) > 0:
        mColl = returnObj.getElementsByClass('Measure')  # a stream of measures
    else:
        raise stream.StreamException(
            'cannot process a stream that neither is a Measure nor has '
            'Measures')

    lastTimeSignature = None

    for m in mColl:
        # this means that the first of a stream of time signatures will
        # be used
        if m.timeSignature is not None:
            lastTimeSignature = m.timeSignature
        if lastTimeSignature is None:
            #environLocal.printDebug([
            #    'makeBeams(): lastTimeSignature is None: cannot process'])
            raise stream.StreamException(
                'cannot proces beams in a Measure without a time signature')
        noteGroups = []
        if m.hasVoices():
            for v in m.voices:
                noteGroups.append(v.notesAndRests)
        else:
            noteGroups.append(m.notesAndRests)

        #environLocal.printDebug([
        #    'noteGroups', noteGroups, 'len(noteGroups[0])',
        #    len(noteGroups[0])])

        for noteStream in noteGroups:
            if len(noteStream) <= 1:
                continue  # nothing to beam
            durList = []
            for n in noteStream:
                durList.append(n.duration)
            #environLocal.printDebug([
            #    'beaming with ts', lastTimeSignature, 'measure', m, durList,
            #    noteStream[0], noteStream[1]])

            # error check; call before sending to time signature, as, if this
            # fails, it represents a problem that happens before time signature
            # processing
            durSum = sum([d.quarterLength for d in durList])
            barQL = lastTimeSignature.barDuration.quarterLength

            if not common.almostEquals(durSum, barQL) and durSum > barQL:
                #environLocal.printDebug([
                #    'attempting makeBeams with a bar that contains durations
                #    that sum greater than bar duration (%s > %s)' %
                #    (durSum, barQL)])
                continue
            # getBeams can take a list of Durations; however, this cannot
            # distinguish a Note from a Rest; thus, we can submit a flat
            # stream of note or note-like entities; will return
            # the same list of beam objects

            offset = 0.0
            if m.paddingLeft != 0.0:
                offset = m.paddingLeft
            elif (noteStream.highestTime <
                lastTimeSignature.barDuration.quarterLength):
                offset = (lastTimeSignature.barDuration.quarterLength -
                    noteStream.highestTime)
            beamsList = lastTimeSignature.getBeams(
                noteStream, measureStartOffset=offset)

            for i in range(len(noteStream)):
                # this may try to assign a beam to a Rest
                noteStream[i].beams = beamsList[i]
            # apply tuple types in place; this modifies the durations
            # in dur list
            duration.updateTupletType(durList)

    del mColl  # remove Stream no longer needed
    if inPlace is not True:
        return returnObj


def makeMeasures(
    s,
    meterStream=None,
    refStreamOrTimeRange=None,
    searchContext=False,
    innerBarline=None,
    finalBarline='final',
    bestClef=False,
    inPlace=False,
    ):
    '''
    Takes a stream and places all of its elements into
    measures (:class:`~music21.stream.Measure` objects)
    based on the :class:`~music21.meter.TimeSignature` objects
    placed within
    the stream. If no TimeSignatures are found in the
    stream, a default of 4/4 is used.

    If `inPlace` is True, the original Stream is modified and lost
    if `inPlace` is False, this returns a modified deep copy.

    Many advanced features are available:

    (1) If a `meterStream` is given, the TimeSignatures in this
    stream are used instead of any found in the Stream.
    Alternatively, a single TimeSignature object
    can be provided in lieu of the stream. This feature lets you
    test out how a group of notes might be interpreted as measures
    in a number of different metrical schemes.

    (2) If `refStreamOrTimeRange` is provided, this Stream or List
    is used to give the span that you want to make measures for
    necessary to fill empty rests at the ends or beginnings of
    Streams, etc.  Say for instance you'd like to make a complete
    score from a short ossia section, then you might use another
    Part from the Score as a `refStreamOrTimeRange` to make sure
    that the appropriate measures of rests are added at either side.

    (3) If `innerBarline` is not None, the specified Barline object
    or string-specification of Barline style will be used to create
    Barline objects between every created Measure. The default is None.

    (4) If `finalBarline` is not None, the specified Barline object or
    string-specification of Barline style will be used to create a Barline
    objects at the end of the last Measure. The default is 'final'.

    The `searchContext` parameter determines whether or not context
    searches are used to find Clef and other notation objects.

    Here is a simple example of makeMeasures:

    A single measure of 4/4 is created by from a Stream
    containing only three quarter notes:

    ::

        >>> from music21 import articulations
        >>> from music21 import clef
        >>> from music21 import meter
        >>> from music21 import note
        >>> from music21 import stream

    ::

        >>> sSrc = stream.Stream()
        >>> sSrc.append(note.QuarterNote('C4'))
        >>> sSrc.append(note.QuarterNote('D4'))
        >>> sSrc.append(note.QuarterNote('E4'))
        >>> sMeasures = sSrc.makeMeasures()
        >>> sMeasures.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.note.Note C>
            {1.0} <music21.note.Note D>
            {2.0} <music21.note.Note E>
            {3.0} <music21.bar.Barline style=final>

    Notice that the last measure is incomplete -- makeMeasures
    does not fill up incomplete measures.

    We can also check that the measure created has
    the correct TimeSignature:

    ::

        >>> sMeasures[0].timeSignature
        <music21.meter.TimeSignature 4/4>

    Now let's redo this work in 2/4 by putting a TimeSignature
    of 2/4 at the beginning of the stream and rerunning
    makeMeasures. Now we will have two measures, each with
    correct measure numbers:

    ::

        >>> sSrc.insert(0.0, meter.TimeSignature('2/4'))
        >>> sMeasuresTwoFour = sSrc.makeMeasures()
        >>> sMeasuresTwoFour.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 2/4>
            {0.0} <music21.note.Note C>
            {1.0} <music21.note.Note D>
        {2.0} <music21.stream.Measure 2 offset=2.0>
            {0.0} <music21.note.Note E>
            {1.0} <music21.bar.Barline style=final>

    Let us put 10 quarter notes in a Part.

    After we run makeMeasures, we will have
    3 measures of 4/4 in a new Part object. This experiment
    demonstrates that running makeMeasures does not
    change the type of Stream you are using:

    ::

        >>> sSrc = stream.Part()
        >>> n = note.Note('E-4')
        >>> n.quarterLength = 1
        >>> sSrc.repeatAppend(n, 10)
        >>> sMeasures = sSrc.makeMeasures()
        >>> len(sMeasures.getElementsByClass('Measure'))
        3
        >>> sMeasures.__class__.__name__
        'Part'

    Demonstrate what makeMeasures will do with inPlace is True:

    ::

        >>> sScr = stream.Stream()
        >>> sScr.insert(0, clef.TrebleClef())
        >>> sScr.insert(0, meter.TimeSignature('3/4'))
        >>> sScr.append(note.Note('C4', quarterLength = 3.0))
        >>> sScr.append(note.Note('D4', quarterLength = 3.0))
        >>> sScr.makeMeasures(inPlace = True)
        >>> sScr.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 3/4>
            {0.0} <music21.note.Note C>
        {3.0} <music21.stream.Measure 2 offset=3.0>
            {0.0} <music21.note.Note D>
            {3.0} <music21.bar.Barline style=final>

    If after running makeMeasures you run makeTies, it will also split
    long notes into smaller notes with ties.  Lyrics and articulations
    are attached to the first note.  Expressions (fermatas,
    etc.) will soon be attached to the last note but this is not yet done:

    ::

        >>> p1 = stream.Part()
        >>> p1.append(meter.TimeSignature('3/4'))
        >>> longNote = note.Note("D#4")
        >>> longNote.quarterLength = 7.5
        >>> longNote.articulations = [articulations.Staccato()]
        >>> longNote.lyric = "hi"
        >>> p1.append(longNote)
        >>> partWithMeasures = p1.makeMeasures()
        >>> dummy = partWithMeasures.makeTies(inPlace = True)
        >>> partWithMeasures.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 3/4>
            {0.0} <music21.note.Note D#>
        {3.0} <music21.stream.Measure 2 offset=3.0>
            {0.0} <music21.note.Note D#>
        {6.0} <music21.stream.Measure 3 offset=6.0>
            {0.0} <music21.note.Note D#>
            {1.5} <music21.bar.Barline style=final>

    ::

        >>> allNotes = partWithMeasures.flat.notes
        >>> allNotes[0].articulations
        [<music21.articulations.Staccato>]

    ::

        >>> allNotes[1].articulations
        []

    ::

        >>> allNotes[2].articulations
        []

    ::

        >>> [allNotes[0].lyric, allNotes[1].lyric, allNotes[2].lyric]
        ['hi', None, None]

    '''
    from music21 import spanner
    from music21 import stream

    #environLocal.printDebug(['calling Stream.makeMeasures()'])

    # the srcObj shold not be modified or chagned
    # removed element copying below and now making a deepcopy of entire stream
    # must take a flat representation, as we need to be able to
    # position components, and sub-streams might hide elements that
    # should be contained

    if s.hasVoices():
        #environLocal.printDebug(['make measures found voices'])
        # cannot make flat here, as this would destroy stream partitions
        srcObj = copy.deepcopy(s.sorted)
        voiceCount = len(srcObj.voices)
    else:
        #environLocal.printDebug(['make measures found no voices'])
        # take flat and sorted version
        srcObj = copy.deepcopy(s.flat.sorted)
        voiceCount = 0

    #environLocal.printDebug([
    #    'Stream.makeMeasures(): passed in meterStream', meterStream,
    #    meterStream[0]])

    # may need to look in activeSite if no time signatures are found
    if meterStream is None:
        # get from this Stream, or search the contexts
        meterStream = srcObj.flat.getTimeSignatures(returnDefault=True,
                        searchContext=False,
                        sortByCreationTime=False)
        #environLocal.printDebug([
        #    'Stream.makeMeasures(): found meterStream', meterStream[0]])
    # if meterStream is a TimeSignature, use it
    elif isinstance(meterStream, meter.TimeSignature):
        ts = meterStream
        meterStream = stream.Stream()
        meterStream.insert(0, ts)

    #assert len(meterStream), 1

    #environLocal.printDebug([
    #    'makeMeasures(): meterStream', 'meterStream[0]', meterStream[0],
    #    'meterStream[0].offset',  meterStream[0].offset,
    #    'meterStream.elements[0].activeSite',
    #    meterStream.elements[0].activeSite])

    # need a SpannerBundle to store any found spanners and place
    # at the part level
    spannerBundleAccum = spanner.SpannerBundle()

    # get a clef for the entire stream; this will use bestClef
    # presently, this only gets the first clef
    # may need to store a clefStream and access changes in clefs
    # as is done with meterStream
    clefStream = srcObj.getClefs(searchActiveSite=True,
                    searchContext=searchContext,
                    returnDefault=True)
    clefObj = clefStream[0]

    #environLocal.printDebug([
    #    'makeMeasures(): first clef found after copying and flattening',
    #    clefObj])

    # for each element in stream, need to find max and min offset
    # assume that flat/sorted options will be set before procesing
    # list of start, start+dur, element
    offsetMap = srcObj.offsetMap
    #environLocal.printDebug(['makeMeasures(): offset map', offsetMap])
    #offsetMap.sort() not necessary; just get min and max
    if len(offsetMap) > 0:
        oMax = max([x['endTime'] for x in offsetMap])
    else:
        oMax = 0

    # if a ref stream is provided, get highest time from there
    # only if it is greater thant the highest time yet encountered
    if refStreamOrTimeRange is not None:
        if isinstance(refStreamOrTimeRange, stream.Stream):
            refStreamHighestTime = refStreamOrTimeRange.highestTime
        else:  # assume its a list
            refStreamHighestTime = max(refStreamOrTimeRange)
        if refStreamHighestTime > oMax:
            oMax = refStreamHighestTime

    # create a stream of measures to contain the offsets range defined
    # create as many measures as needed to fit in oMax
    post = s.__class__()
    post.derivesFrom = s
    post.derivationMethod = 'makeMeasures'

    o = 0.0  # initial position of first measure is assumed to be zero
    measureCount = 0
    lastTimeSignature = None
    while True:
        m = stream.Measure()
        m.number = measureCount + 1
        #environLocal.printDebug([
        #    'handling measure', m, m.number, 'current offset value', o,
        #    meterStream._reprTextLine()])
        # get active time signature at this offset
        # make a copy and it to the meter
        thisTimeSignature = meterStream.getElementAtOrBefore(o)
        #environLocal.printDebug([
        #    'm.number', m.number, 'meterStream.getElementAtOrBefore(o)',
        #    meterStream.getElementAtOrBefore(o), 'lastTimeSignature',
        #    lastTimeSignature, 'thisTimeSignature', thisTimeSignature ])

        if thisTimeSignature is None and lastTimeSignature is None:
            raise stream.StreamException(
                'failed to find TimeSignature in meterStream; '
                'cannot process Measures')
        if thisTimeSignature is not lastTimeSignature \
            and thisTimeSignature is not None:
            lastTimeSignature = thisTimeSignature
            # this seems redundant
            #lastTimeSignature = meterStream.getElementAtOrBefore(o)
            m.timeSignature = copy.deepcopy(thisTimeSignature)
            #environLocal.printDebug(['assigned time sig', m.timeSignature])

        # only add a clef for the first measure when automatically
        # creating Measures; this clef is from getClefs, called above
        if measureCount == 0:
            m.clef = clefObj
            #environLocal.printDebug(
            #    ['assigned clef to measure', measureCount, m.clef])

        # add voices if necessary (voiceCount > 0)
        for voiceIndex in range(voiceCount):
            v = stream.Voice()
            v.id = voiceIndex  # id is voice index, starting at 0
            m._insertCore(0, v)

        # avoid an infinite loop
        if thisTimeSignature.barDuration.quarterLength == 0:
            raise stream.StreamException(
                'time signature {0!r} has no duration'.format(
                    thisTimeSignature))
        post._insertCore(o, m)  # insert measure
        # increment by meter length
        o += thisTimeSignature.barDuration.quarterLength
        if o >= oMax:  # may be zero
            break  # if length of this measure exceedes last offset
        else:
            measureCount += 1

    # populate measures with elements
    for ob in offsetMap:
        start, end, e, voiceIndex = (
            ob['offset'],
            ob['endTime'],
            ob['element'],
            ob['voiceIndex'],
            )

        #environLocal.printDebug(['makeMeasures()', start, end, e, voiceIndex])
        # iterate through all measures, finding a measure that
        # can contain this element

        # collect all spanners and move to outer Stream
        if e.isSpanner:
            spannerBundleAccum.append(e)
            continue

        match = False
        lastTimeSignature = None
        for i in range(len(post)):
            m = post[i]
            if m.timeSignature is not None:
                lastTimeSignature = m.timeSignature
            # get start and end offsets for each measure
            # seems like should be able to use m.duration.quarterLengths
            mStart = m.getOffsetBySite(post)
            mEnd = mStart + lastTimeSignature.barDuration.quarterLength
            # if elements start fits within this measure, break and use
            # offset cannot start on end
            if start >= mStart and start < mEnd:
                match = True
                #environLocal.printDebug([
                #    'found measure match', i, mStart, mEnd, start, end, e])
                break
        if not match:
            raise stream.StreamException(
                'cannot place element %s with start/end %s/%s '
                'within any measures' % (e, start, end))

        # find offset in the temporal context of this measure
        # i is the index of the measure that this element starts at
        # mStart, mEnd are correct
        oNew = start - mStart  # remove measure offset from element offset

        # insert element at this offset in the measure
        # not copying elements here!

        # in the case of a Clef, and possibly other measure attributes,
        # the element may have already been placed in this measure
        # we need to only exclude elements that are placed in the special
        # first position
        if m.clef is e:
            continue
        # do not accept another time signature at the zero position: this
        # is handled above
        if oNew == 0 and 'TimeSignature' in e.classes:
            continue

        #environLocal.printDebug(['makeMeasures()', 'inserting', oNew, e])
        # NOTE: cannot use _insertCore here for some reason
        if voiceIndex is None:
            m.insert(oNew, e)
        else:  # insert into voice specified by the voice index
            m.voices[voiceIndex].insert(oNew, e)

    # add found spanners to higher-level; could insert at zero
    for sp in spannerBundleAccum:
        post.append(sp)

    post._elementsChanged()

    # clean up temporary streams to avoid extra site accumulation
    del srcObj
    del clefStream

    # set barlines if necessary
    lastIndex = len(post.getElementsByClass('Measure')) - 1
    for i, m in enumerate(post.getElementsByClass('Measure')):
        if i != lastIndex:
            if innerBarline not in ['regular', None]:
                m.rightBarline = innerBarline
        else:
            if finalBarline not in ['regular', None]:
                m.rightBarline = finalBarline
        if bestClef:
            m.clef = m.bestClef()  # may need flat for voices

    if not inPlace:
        return post  # returns a new stream populated w/ new measure streams
    else:  # clear the stored elements list of this Stream and repopulate
        # with Measures created above
        s._elements = []
        s._endElements = []
        s._elementsChanged()
        for e in post.sorted:
            # may need to handle spanners; already have s as site
            s.insert(e.getOffsetBySite(post), e)


def makeRests(s, refStreamOrTimeRange=None, fillGaps=False,
    timeRangeFromBarDuration=False, inPlace=True):
    '''
    Given a Stream with an offset not equal to zero,
    fill with one Rest preeceding this offset.
    This can be called on any Stream,
    a Measure alone, or a Measure that contains
    Voices.

    If `refStreamOrTimeRange` is provided as a Stream, this
    Stream is used to get min and max offsets. If a list is provided,
    the list assumed to provide minimum and maximum offsets. Rests will
    be added to fill all time defined within refStream.

    If `fillGaps` is True, this will create rests in any
    time regions that have no active elements.

    If `timeRangeFromBarDuration` is True, and the calling Stream
    is a Measure with a TimeSignature, the time range will be determined
    based on the .barDuration property.

    If `inPlace` is True, this is done in-place; if `inPlace` is False,
    this returns a modified deepcopy.

    ::

        >>> from music21 import note
        >>> from music21 import stream

    ::

        >>> a = stream.Stream()
        >>> a.insert(20, note.Note())
        >>> len(a)
        1

    ::

        >>> a.lowestOffset
        20.0

    ::

        >>> b = a.makeRests()
        >>> len(b)
        2

    ::

        >>> b.lowestOffset
        0.0

    OMIT_FROM_DOCS
    TODO: if inPlace is True, this should return None
    TODO: default inPlace = False
    '''
    from music21 import stream

    if not inPlace:  # make a copy
        returnObj = copy.deepcopy(s)
    else:
        returnObj = s

    #environLocal.printDebug([
    #    'makeRests(): object lowestOffset, highestTime', oLow, oHigh])
    if refStreamOrTimeRange is None:  # use local
        oLowTarget = 0
        if timeRangeFromBarDuration and returnObj.isMeasure:
            # NOTE: this will raise an exception if no meter can be found
            oHighTarget = returnObj.barDuration.quarterLength
        else:
            oHighTarget = returnObj.highestTime
    elif isinstance(refStreamOrTimeRange, stream.Stream):
        oLowTarget = refStreamOrTimeRange.lowestOffset
        oHighTarget = refStreamOrTimeRange.highestTime
        #environLocal.printDebug([
        #    'refStream used in makeRests', oLowTarget, oHighTarget,
        #    len(refStreamOrTimeRange)])
    # treat as a list
    elif common.isListLike(refStreamOrTimeRange):
        oLowTarget = min(refStreamOrTimeRange)
        oHighTarget = max(refStreamOrTimeRange)
        #environLocal.printDebug([
        #    'offsets used in makeRests', oLowTarget, oHighTarget,
        #    len(refStreamOrTimeRange)])
    if returnObj.hasVoices():
        bundle = returnObj.voices
    else:
        bundle = [returnObj]

    for v in bundle:
        v._elementsChanged()  # required to get correct offset times
        oLow = v.lowestOffset
        oHigh = v.highestTime

        # create rest from start to end
        qLen = oLow - oLowTarget
        if qLen > 0:
            r = note.Rest()
            r.duration.quarterLength = qLen
            #environLocal.printDebug(['makeRests(): add rests', r, r.duration])
            # place at oLowTarget to reach to oLow
            v._insertCore(oLowTarget, r)

        # create rest from end to highest
        qLen = oHighTarget - oHigh
        #environLocal.printDebug(['v', v, oHigh, oHighTarget, 'qLen', qLen])
        if qLen > 0:
            r = note.Rest()
            r.duration.quarterLength = qLen
            # place at oHigh to reach to oHighTarget
            v._insertCore(oHigh, r)
        v._elementsChanged()  # must update otherwise might add double r

        if fillGaps:
            gapStream = v.findGaps()
            if gapStream is not None:
                for e in gapStream:
                    r = note.Rest()
                    r.duration.quarterLength = e.duration.quarterLength
                    v._insertCore(e.offset, r)
        v._elementsChanged()
        #environLocal.printDebug(['post makeRests show()', v])
        # NOTE: this sorting has been found to be necessary, as otherwise
        # the resulting Stream is not sorted and does not get sorted in
        # preparing musicxml output
        if v.autoSort:
            v.sort()

    # with auto sort no longer necessary.

    #returnObj.elements = returnObj.sorted.elements
    #s.isSorted = False
    # changes elements
#         returnObj._elementsChanged()
#         if returnObj.autoSort:
#             returnObj.sort()

    return returnObj


def makeTies(
    s,
    meterStream=None,
    inPlace=True,
    displayTiedAccidentals=False,
    ):
    '''
    Given a stream containing measures, examine each element in the
    Stream. If the elements duration extends beyond the measure's boundary,
    create a tied entity, placing the split Note in the next Measure.

    Note that this method assumes that there is appropriate space in the
    next Measure: this will not shift Note objects, but instead allocate
    them evenly over barlines. Generally, makeMeasures is called prior to
    calling this method.

    If `inPlace` is True, this is done in-place;
    if `inPlace` is False, this returns a modified deep copy.

    ::

        >>> from music21 import stream

    ::

        >>> d = stream.Stream()
        >>> n = note.Note()
        >>> n.quarterLength = 12
        >>> d.repeatAppend(n, 10)
        >>> d.repeatInsert(n, [x+.5 for x in range(10)])
        >>> x = d.makeMeasures()
        >>> x = x.makeTies()

    OMIT_FROM_DOCS
    TODO: inPlace should be False
    TODO: inPlace = True should return None
    TODO: take a list of clases to act as filter on what elements are tied.

    configure ".previous" and ".next" attributes
    '''
    from music21 import stream

    #environLocal.printDebug(['calling Stream.makeTies()'])

    if not inPlace:  # make a copy
        returnObj = copy.deepcopy(s)
    else:
        returnObj = s
    if len(returnObj) == 0:
        raise stream.StreamException('cannot process an empty stream')

    # get measures from this stream
    measureStream = returnObj.getElementsByClass('Measure')
    if len(measureStream) == 0:
        raise stream.StreamException(
            'cannot process a stream without measures')

    #environLocal.printDebug([
    #    'makeTies() processing measureStream, length', measureStream,
    #    len(measureStream)])

    # may need to look in activeSite if no time signatures are found
    # presently searchContext is False to save time
    if meterStream is None:
        meterStream = returnObj.getTimeSignatures(sortByCreationTime=True,
                        searchContext=False)

    mCount = 0
    lastTimeSignature = None
    while True:
        # update measureStream on each iteration,
        # as new measure may have been added to the returnObj stream
        measureStream = returnObj.getElementsByClass('Measure')
        if mCount >= len(measureStream):
            break  # reached the end of all measures available or added
        # get the current measure to look for notes that need ties
        m = measureStream[mCount]
        if m.timeSignature is not None:
            lastTimeSignature = m.timeSignature

        # get next measure; we may not need it, but have it ready
        if mCount + 1 < len(measureStream):
            mNext = measureStream[mCount + 1]
            mNextAdd = False  # already present; do not append
        else:  # create a new measure
            mNext = stream.Measure()
            # set offset to last offset plus total length
            moffset = m.getOffsetBySite(measureStream)
            if lastTimeSignature is not None:
                mNext.offset = (moffset +
                                lastTimeSignature.barDuration.quarterLength)
            else:
                mNext.offset = moffset
            if len(meterStream) == 0:  # in case no meters are defined
                ts = meter.TimeSignature()
                ts.load('%s/%s' % (defaults.meterNumerator,
                    defaults.meterDenominatorBeatType))
            else:  # get the last encountered meter
                ts = meterStream.getElementAtOrBefore(mNext.offset)
            # only copy and assign if not the same as the last
            if lastTimeSignature is not None \
                and not lastTimeSignature.ratioEqual(ts):
                mNext.timeSignature = copy.deepcopy(ts)
            # increment measure number
            mNext.number = m.number + 1
            mNextAdd = True  # new measure, needs to be appended

        if mNext.hasVoices():
            mNextHasVoices = True
        else:
            mNextHasVoices = False

        #environLocal.printDebug([
        #    'makeTies() dealing with measure', m, 'mNextAdd', mNextAdd])
        # for each measure, go through each element and see if its
        # duraton fits in the bar that contains it

        # if there are voices, we must look at voice id values to only
        # connect ties to components in the same voice, assuming there
        # are voices in the next measure
        try:
            mEnd = lastTimeSignature.barDuration.quarterLength
        except AttributeError:
            ts = m.getContextByClass('TimeSignature')
            if ts is not None:
                lastTimeSignature = ts
                mEnd = lastTimeSignature.barDuration.quarterLength
            else:
                mEnd = 4.0  # Default
        if m.hasVoices():
            bundle = m.voices
            mHasVoices = True
        else:
            bundle = [m]
            mHasVoices = False
        # bundle components may be voices, or just a measure
        for v in bundle:
            for e in v:
                #environLocal.printDebug([
                #    'Stream.makeTies() iterating over elements in measure',
                #    m, e])
                #if hasattr(e, 'duration') and e.duration is not None:
                if e.duration is not None:
                    # check to see if duration is within Measure
                    eOffset = e.getOffsetBySite(v)
                    eEnd = eOffset + e.duration.quarterLength
                    # assume end can be at boundary of end of measure
                    overshot = eEnd - mEnd
                    # only process if overshot is greater than a minimum
                    # 1/64 is 0.015625
                    if overshot > .001:
                        if eOffset >= mEnd:
                            raise stream.StreamException(
                                'element (%s) has offset %s within a measure '
                                'that ends at offset %s' % (e, eOffset, mEnd))

                        qLenBegin = mEnd - eOffset
                        e, eRemain = e.splitAtQuarterLength(qLenBegin,
                            retainOrigin=True,
                            displayTiedAccidentals=displayTiedAccidentals)

                        # manage bridging voices
                        if mNextHasVoices:
                            if mHasVoices:  # try to match voice id
                                dst = mNext.voices[v.id]
                            # src does not have voice, but dst does
                            else:  # place in top-most voice
                                dst = mNext.voices[0]
                        else:
                            # mNext has no voices but this one does
                            if mHasVoices:
                                # internalize all components in a voice
                                mNext.internalize(container=stream.Voice)
                                # place in first voice
                                dst = mNext.voices[0]
                            else:  # no voices in either
                                dst = mNext

                        #eRemain.activeSite = mNext
                        # manually set activeSite
                        # cannot use _insertCore here
                        dst.insert(0, eRemain)

                        # we are not sure that this element fits
                        # completely in the next measure, thus, need to
                        # continue processing each measure
                        if mNextAdd:
                            #environLocal.printDebug([
                            #    'makeTies() inserting mNext into returnObj',
                            #    mNext])
                            returnObj.insert(mNext.offset, mNext)
                    elif overshot > 0:
                        environLocal.printDebug([
                            'makeTies() found and skipping extremely small '
                            'overshot into next measure', overshot])
        mCount += 1
    del measureStream  # clean up unused streams
    # changes elements
    returnObj._elementsChanged()
    if not inPlace:
        return returnObj
    else:
        return None


def makeTupletBrackets(s, inPlace=True):
    '''
    Given a Stream of mixed durations, the first and last tuplet of any group
    of tuplets must be designated as the start and end.

    Need to not only look at Notes, but components within Notes, as these might
    contain additional tuplets.

    TODO: inPlace default should become False -- like all inPlace arguments
    TODO: if inPlace is True, return None
    '''

    if not inPlace:  # make a copy
        returnObj = copy.deepcopy(s)
    else:
        returnObj = s

    isOpen = False
    tupletCount = 0
    lastTuplet = None

    # only want to look at notes
    notes = returnObj.notesAndRests
    durList = []
    for e in notes:
        for d in e.duration.components:
            durList.append(d)

    eCount = len(durList)

    #environLocal.printDebug([
    #    'calling makeTupletBrackets, lenght of notes:', eCount])

    for i in range(eCount):
        e = durList[i]
        if e is not None:
            if e.tuplets is None:
                continue
            tContainer = e.tuplets
            #environLocal.printDebug(['makeTupletBrackets', tContainer])
            if len(tContainer) == 0:
                t = None
            else:
                t = tContainer[0]  # get first?

            # end case: this Note does not have a tuplet
            if t is None:
                if isOpen is True:  # at the end of a tuplet span
                    isOpen = False
                    # now have a non-tuplet, but the tuplet span was only
                    # one tuplet long; do not place a bracket
                    if tupletCount == 1:
                        lastTuplet.type = 'startStop'
                        lastTuplet.bracket = False
                    else:
                        lastTuplet.type = 'stop'
                tupletCount = 0
            else:  # have a tuplet
                tupletCount += 1
                # store this as the last tupelt
                lastTuplet = t

                #environLocal.printDebug([
                #    'makeTupletBrackets', e, 'existing typlet type', t.type,
                #    'bracket', t.bracket, 'tuplet count:', tupletCount])

                # already open bracket
                if isOpen:
                    # end case: this is the last element and its a tuplet
                    # since this is an open bracket, we know we have more
                    # than one tuplet in this span
                    if i == eCount - 1:
                        t.type = 'stop'
                    # if this the middle of a span, do nothing
                    else:
                        pass
                else:  # need to open
                    isOpen = True
                    # if this is the last event in this Stream
                    # do not create bracket
                    if i == eCount - 1:
                        t.type = 'startStop'
                        t.bracket = False
                    # normal start of tuplet span
                    else:
                        t.type = 'start'

#                 if t is not None:
#                     environLocal.printDebug([
#                         'makeTupletBrackets', e, 'final type', t.type,
#                         'bracket', t.bracket])

    return returnObj


def realizeOrnaments(s):
    '''
    Realize all ornaments on a stream

    Creates a new stream that contains all realized ornaments in addition
    to other elements in the original stream.

    ::

        >>> from music21 import expressions
        >>> from music21 import meter
        >>> from music21 import note
        >>> from music21 import stream

    ::

        >>> s1 = stream.Stream()
        >>> m1 = stream.Measure()
        >>> m1.timeSignature = meter.TimeSignature("4/4")
        >>> n1 = note.WholeNote("C4")
        >>> n1.expressions.append(expressions.Mordent())
        >>> m1.append(n1)
        >>> m2 = stream.Measure()
        >>> n2 = note.WholeNote("D4")
        >>> m2.append(n2)
        >>> s1.append(m1)
        >>> s1.append(m2)
        >>> for x in s1.recurse():
        ...     x
        ...
        <music21.stream.Stream ...>
        <music21.stream.Measure 0 offset=0.0>
        <music21.meter.TimeSignature 4/4>
        <music21.note.Note C>
        <music21.stream.Measure 0 offset=4.0>
        <music21.note.Note D>

    ::

        >>> s2 = s1.realizeOrnaments()
        >>> for x in s2.recurse():
        ...     x
        ...
        <music21.stream.Stream ...>
        <music21.stream.Measure 0 offset=0.0>
        <music21.meter.TimeSignature 4/4>
        <music21.note.Note C>
        <music21.note.Note B>
        <music21.note.Note C>
        <music21.stream.Measure 0 offset=4.0>
        <music21.note.Note D>

    '''
    newStream = s.__class__()
    newStream.offset = s.offset

    # If this streamObj contains more streams (i.e., a Part that contains
    # multiple measures):
    recurse = s.recurse(streamsOnly=True)

    if len(recurse) > 1:
        i = 0
        for innerStream in recurse:
            if i > 0:
                newStream.append(innerStream.realizeOrnaments())
            i = i + 1
    else:
        for element in s:
            if hasattr(element, "expressions"):
                realized = False
                for exp in element.expressions:
                    if hasattr(exp, "realize"):
                        newNotes = exp.realize(element)
                        realized = True
                        for n in newNotes:
                            newStream.append(n)
                if not realized:
                    newStream.append(element)
            else:
                newStream.append(element)

    return newStream


#------------------------------------------------------------------------------


class Test(unittest.TestCase):
    '''
    Note: all Stream tests are found in test/testStream.py
    '''

    def runTest(self):
        pass


#------------------------------------------------------------------------------


if __name__ == "__main__":
    import music21
    music21.mainTest(Test)

