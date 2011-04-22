#-------------------------------------------------------------------------------
# Name:         features/base.py
# Purpose:      Feature extractors base classes.
#
# Authors:      Christopher Ariza
#
# Copyright:    (c) 2011 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------

import unittest
import os
import music21

from music21 import stream
from music21 import common
from music21 import corpus
from music21 import converter

from music21 import environment
_MOD = 'features/base.py'
environLocal = environment.Environment(_MOD)




#-------------------------------------------------------------------------------
class FeatureException(music21.Music21Exception):
    pass


class Feature(object):
    '''An object representation of a feature, capable of presentation in a variety of formats, and returned from FeatureExtractor objects.

    Feature objects are simple. It is FeatureExtractors that store all metadata and processing routines for creating Feature objects. 
    '''
    def __init__(self):
        # these values will be filled by the extractor
        self.name = None # string name representation
        self.description = None # string description
        self.isSequential = None # True or False
        self.dimensions = None # number of dimensions
        self.discrete = None # is discrete or continuous
        # data storage; possibly use numpy array
        self.vector = None

    def _getVectors(self):
        '''Prepare a vector of appropriate size and return
        '''
        return [0] * self.dimensions

    def prepareVectors(self):
        '''Prepare the vector stored in this feature.
        '''
        self.vector = self._getVectors()

    def normalize(self):
        '''Normalize the vector between 0 and 1, assuming there is more than one value.
        '''
        if self.dimensions == 1:
            return # do nothing
        m = max(self.vector)
        if max == 0:
            return # do nothing
        scalar = 1. / m # get floating point scalar for speed
        temp = self._getVectors()
        for i, v in enumerate(self.vector):
            temp[i] = v * scalar
        self.vector = temp






#-------------------------------------------------------------------------------
class FeatureExtractorException(music21.Music21Exception):
    pass

class FeatureExtractor(object):
    '''A model of process that extracts a feature from a Music21 Stream. The main public interface is the extract() method. 

    The extractor can be passed a Stream or a reference to a DataInstance. All Stream's are internally converted to a DataInstance if necessary. Usage of a DataInstance offers significant performance advantages, as common forms of the Stream are cached for easy processing. 

    '''
    def __init__(self, dataOrStream=None, *arguments, **keywords):
        self._src = None # the original Stream, or None
        self.data = None # a DataInstance object: use to get data
        self.setData(dataOrStream)

        self._feature = None # Feature object that results from processing

        self.name = None # string name representation
        self.description = None # string description
        self.isSequential = None # True or False
        self.dimensions = None # number of dimensions
        self.discrete = True # default
        self.normalize = False # default is no

    def setData(self, dataOrStream):
        '''Set the data that this FeatureExtractor will process. Either a Stream or a DataInstance object can be provided. 
        '''
        if dataOrStream is not None:
            # if a DataInstance, do nothing
            if isinstance(dataOrStream, DataInstance):
                self._src = None
                self.data = dataOrStream
            else:
                # if we are passed a stream, create a DataInstrance to 
                # manage the
                # its data; this is less efficient but is good for testing
                self._src = dataOrStream
                self.data = DataInstance(self._src)

    def getAttributeLabels(self): 
        '''Return a list of string in a form that is appropriate for data storage.
    
        >>> from music21 import *
        >>> fe = features.jSymbolic.AmountOfArpeggiationFeature()
        >>> fe.getAttributeLabels()
        ['Amount_of_Arpeggiation']

        >>> fe = features.jSymbolic.FifthsPitchHistogramFeature()
        >>> fe.getAttributeLabels()
        ['Fifths_Pitch_Histogram_0', 'Fifths_Pitch_Histogram_1', 'Fifths_Pitch_Histogram_2', 'Fifths_Pitch_Histogram_3', 'Fifths_Pitch_Histogram_4', 'Fifths_Pitch_Histogram_5', 'Fifths_Pitch_Histogram_6', 'Fifths_Pitch_Histogram_7', 'Fifths_Pitch_Histogram_8', 'Fifths_Pitch_Histogram_9', 'Fifths_Pitch_Histogram_10', 'Fifths_Pitch_Histogram_11']

        '''
        post = []
        if self.dimensions == 1:
            post.append(self.name.replace(' ', '_'))
        else:
            for i in range(self.dimensions):
                post.append('%s_%s' % (self.name.replace(' ', '_'), i))
        return post

    def _fillFeatureAttributes(self, feature=None):
        '''Fill the attributes of a Feature with the descriptors in the FeatureExtractor.
        '''
        # operate on passed-in feature or self._feature
        if feature is None:
            feature = self._feature
        feature.name = self.name
        feature.description = self.description
        feature.isSequential = self.isSequential
        feature.dimensions = self.dimensions
        feature.discrete = self.discrete
        return feature

    def _prepareFeature(self):
        '''Prepare a new Feature object for data acquisition.

        >>> from music21 import *
        >>> s = stream.Stream()
        >>> fe = features.jSymbolic.InitialTimeSignatureFeature(s)
        >>> fe._prepareFeature()
        >>> fe._feature.name
        'Initial Time Signature'
        >>> fe._feature.dimensions
        2
        >>> fe._feature.vector
        [0, 0]
        '''
        self._feature = Feature()
        self._fillFeatureAttributes() # will fill self._feature
        self._feature.prepareVectors() # will vector with necessary zeros


    def _process(self):
        '''Do processing necessary, storing result in _feature.
        '''
        # do work in subclass, calling on self.data
        pass

    def extract(self, source=None):
        '''Extract the feature and return the result. 
        '''
        if source is not None:
            self._src = source
        # preparing the feature always sets self._feature to a new instance
        self._prepareFeature()
        self._process() # will set Feature object to _feature
        # assume we always want to normalize?
        if self.normalize:
            self._feature.normalize()
        return self._feature    




#-------------------------------------------------------------------------------
class DataInstance(object):
    '''A data instance for analysis. This object prepares a Stream and stores multiple common-used stream representations once, providing rapid processing. 
    '''
    def __init__(self, streamObj=None):
        self._src = streamObj

        # perform basic operations that are performed on all
        # streams
        if self._src is not None:
            self._base = self._prepareStream(self._src)
        else:       
            self._base = None

        # the attribute name in the data set for this label
        self._classLabel = None
        # store the class value for this data instance
        self._classValue = None

        # store a dictionary of stream forms that are made and stored
        # on demand
        self._forms = {}

    def _prepareStream(self, streamObj):
        '''Common routines done on Streams prior to processing. Return a new Stream
        '''
        #TODO: add expand repeats
        src = streamObj.stripTies(retainContainers=True, inPlace=False)
        return src

    def setClassLabel(self, classLabel, classValue=None):
        '''Set the class label, as well as the class value if known. The class label is the attribute name used to define the class of this data instance.

        >>> from music21 import *
        >>> s = corpus.parse('bwv66.6')
        >>> di = features.DataInstance(s)
        >>> di.setClassLabel('Composer', 'Bach')
        '''
        self._classLabel = classLabel
        self._classValue = classValue

    def getClassValue(self):    
        if self._classValue is None:
            return ''
        else:
            return self._classValue

    def _getForm(self, form='flat'):
        '''Get a form of this Stream, using a cached version if available.

        >>> from music21 import *
        >>> s = corpus.parse('bwv66.6')
        >>> di = features.DataInstance(s)
        >>> len(di._getForm('flat'))
        192
        >>> len(di['flat'])
        192
        >>> len(di._getForm('flat.pitches'))
        163
        >>> len(di._getForm('flat.notes'))
        163
        >>> len(di._getForm('getElementsByClass.Measure'))
        40
        >>> len(di['getElementsByClass.Measure'])
        40
        >>> len(di._getForm('flat.getElementsByClass.TimeSignature'))
        4
        '''
        # get cached copy
        if form in self._forms.keys():
            return self._forms[form]

        # else, process, store, and return
        elif form in ['flat']:
            self._forms['flat'] = self._base.flat
            return self._forms['flat']

        elif form in ['flat.pitches']:
            self._forms['flat.pitches'] = self._base.flat.pitches
            return self._forms['flat.pitches']

        elif form in ['flat.notes']:
            self._forms['flat.notes'] = self._base.flat.notes
            return self._forms['flat.notes']

        elif form in ['getElementsByClass.Measure']:
            # need to determine if should concatenate
            # measure for all parts if a score?
            if 'Score' in self._base.classes:
                post = stream.Stream()
                for p in self._base.parts:
                    # insert in overlapping offset positions
                    for m in p.getElementsByClass('Measure'):
                        post.insert(m.getOffsetBySite(p), m)
            else:
                post = self._base.getElementsByClass('Measure')

            self._forms['getElementsByClass.Measure'] = post
            return self._forms['getElementsByClass.Measure']

        elif form in ['flat.getElementsByClass.TimeSignature']:
            self._forms['flat.getElementsByClass.TimeSignature'] = self._base.flat.getElementsByClass('TimeSignature')
            return self._forms['flat.getElementsByClass.TimeSignature']

        # data lists / histograms

        elif form in ['pitchClassHistogram']:
            histo = [0] * 12
            for p in self._getForm('flat.pitches'): # recursive call
                histo[p.pitchClass] += 1
            self._forms['pitchClassHistogram'] = histo
            return self._forms['pitchClassHistogram']

        elif form in ['midiPitchHistogram']:
            histo = [0] * 128
            for p in self._getForm('flat.pitches'): # recursive call
                histo[p.midi] += 1
            self._forms['midiPitchHistogram'] = histo
            return self._forms['midiPitchHistogram']

        else:
            raise AttributeError('no such attribute: %s' % form)


    def __getitem__(self, key):
        return self._getForm(key)


#-------------------------------------------------------------------------------
class OutputFormatException(music21.Music21Exception):
    pass

class OutputFormat(object):
    '''Provide storage classes for data input and output
    '''
    def __init__(self):
        # assume a two dimensional array
        self._rows = []
        self._ext = None # store a fiel extension if necessare
    
    def append(self, row):
        self._rows.append(row)

    def getString(self):
        # define in subclass
        return ''

    def getArray(self):
        '''Get data in a numeric array. 
        '''
        pass
    
    def write(self, fp=None):
        '''Write the file. If not file path is given, a temporary file will be written.
        '''
        if fp is None:
            fp = environment.getTempFile(suffix=self._ext)
        if not fp.endswith(self._ext):
            raise
        f = open(fp, 'w')
        f.write(self.getString())
        f.close()
        return fp

class OutputTabOrange(OutputFormat):
    '''Tab delimited file format used with Orange.

    http://orange.biolab.si/doc/reference/tabdelimited.htm
    '''
    def __init__(self):
        OutputFormat.__init__(self)
        self._ext = '.tab'

    def getString(self):
        msg = []
        for row in self._rows:
            sub = []
            for e in row:
                sub.append(str(e))
            msg.append('\t'.join(sub))
        return '\n'.join(msg)

class OutputCSV(OutputFormat):
    '''Comma-separated value list. 
    '''
    def __init__(self):
        OutputFormat.__init__(self)
        self._ext = '.csv'

    def getString(self):
        msg = []
        for row in self._rows:
            sub = []
            for e in row:
                sub.append(str(e))
            msg.append(','.join(sub))
        return '\n'.join(msg)

class OutputARFF(OutputFormat):
    '''An ARFF (Attribute-Relation File Format) file.

    http://weka.wikispaces.com/ARFF+(stable+version)

    >>> from music21 import *
    >>> oa = features.OutputARFF()
    >>> oa._ext
    '.arff'
    '''
    def __init__(self):
        OutputFormat.__init__(self)
        self._ext = '.arff'

    def getString(self):
        msg = []
        for row in self._rows:
            sub = []
            for e in row:
                sub.append(str(e))
            msg.append(','.join(sub))
        return '\n'.join(msg)



#-------------------------------------------------------------------------------
class DataSetException(music21.Music21Exception):
    pass

class DataSet(object):
    '''A set of features, as well as a collection of data to opperate on

    Multiple DataInstance objects, a FeatureSet, and an OutputFormat. 

    >>> from music21 import *
    >>> ds = features.DataSet(classLabel='Composer')
    >>> f = [features.jSymbolic.PitchClassDistributionFeature, features.jSymbolic.ChangesOfMeterFeature, features.jSymbolic.InitialTimeSignatureFeature]
    >>> ds.addFeatureExtractors(f)
    >>> ds.addData('bwv66.6', classValue='Bach')
    >>> ds.addData('bach/bwv324.xml', classValue='Bach')
    >>> ds.process()
    >>> ds.getFeaturesAsList()[0]
    [0.0, 1.0, 0.375, 0.03125, 0.5, 0.1875, 0.90625, 0.0, 0.4375, 0.6875, 0.09375, 0.875, 0, 4, 4, 'Bach']
    >>> ds.getFeaturesAsList()[1]
    [0.12, 0.0, 1.0, 0.12, 0.560..., 0.0, 0.599999..., 0.52000..., 0.0, 0.680000..., 0.0, 0.5600000..., 0, 4, 4, 'Bach']

    '''

    def __init__(self, classLabel=None, featureExtractors=[]):
        # assume a two dimensional array
        self._dataInstances = []
        # order of feature extractors is the order used in the presentaitons
        self._featureExtractors = []
        # the label of the class
        self._classLabel = classLabel

        # store a multidimensional storage of all features
        self._features = [] 

        # set extractors
        self.addFeatureExtractors(featureExtractors)
        
    def addFeatureExtractors(self, values):
        '''Add one or more FeatureExtractor objects, either as a list or as an individual object. 
        '''
        # features are instantiated here
        # however, they do not have a data assignment
        if common.isListLike(values):
            # need to create instances
            for sub in values:
                self._featureExtractors.append(sub())
        else:
            self._featureExtractors.append(values())

    def getAttributeLabels(self, includeClassLabel=True):
        '''
        >>> from music21 import *
        >>> f = [features.jSymbolic.PitchClassDistributionFeature, features.jSymbolic.ChangesOfMeterFeature]
        >>> ds = features.DataSet(classLabel='Composer', featureExtractors=f)
        >>> ds.getAttributeLabels()
        ['Pitch_Class_Distribution_0', 'Pitch_Class_Distribution_1', 'Pitch_Class_Distribution_2', 'Pitch_Class_Distribution_3', 'Pitch_Class_Distribution_4', 'Pitch_Class_Distribution_5', 'Pitch_Class_Distribution_6', 'Pitch_Class_Distribution_7', 'Pitch_Class_Distribution_8', 'Pitch_Class_Distribution_9', 'Pitch_Class_Distribution_10', 'Pitch_Class_Distribution_11', 'Changes_of_Meter', 'Composer']

        '''
        post = []
        for fe in self._featureExtractors:
            post += fe.getAttributeLabels()
        if self._classLabel is not None:
            post.append(self._classLabel.replace(' ', '_'))
        return post

    def addData(self, dataOrStreamOrPath, classValue=None):
        '''Add a Stream, DataInstance, or path to a corpus or local file to this data set.

        The class value passed here is assumed to be the same as the classLable assigned at startup. 
        '''
        if self._classLabel is None:
            raise DataSetException('cannot add data unless a class label for this DataSet has been set.')

        if isinstance(dataOrStreamOrPath, DataInstance):
            di = dataOrStream
        elif common.isStr(dataOrStreamOrPath):
            # could be corpus or file path
            if os.path.exists(dataOrStreamOrPath):
                s = converter.parse(dataOrStreamOrPath)
            else: # assume corpus
                s = corpus.parse(dataOrStreamOrPath)
            di = DataInstance(s)
        else:        
            # for now, assume all else are streams
            di = DataInstance(dataOrStream)

        di.setClassLabel(self._classLabel, classValue)
        self._dataInstances.append(di)


    def process(self):
        '''Process all Data with all FeatureExtractors.
        '''
        # clear features; this stores Feature objects that result from
        # processing
        self._features = []

        for data in self._dataInstances:
            row = []
            for fe in self._featureExtractors:
                fe.setData(data)
                row.append(fe.extract()) # get feature and store
            # rows will allign with data the order of DataInstances
            self._features.append(row)


    def getFeaturesAsList(self, includeClassLabel=True):
        '''Get processed data as a list of lists.
        '''
        post = []
        for i, row in enumerate(self._features):
            v = []
            di = self._dataInstances[i]
            for f in row:
                v += f.vector
            v.append(di.getClassValue())
            post.append(v)
        return post


    def write(self, fp=None, format='tab'):
        '''Set the output format object. 
        '''
        if format.lower() in ['tab', 'orange', 'taborange', None]:
            outputFormat = OutputTabOrange()
        elif format.lower() in ['csv', 'comma']:
            outputFormat = OutputCSV()
        elif format.lower() in ['arff', 'attribute']:
            outputFormat = OutputARFF()







#-------------------------------------------------------------------------------
class Test(unittest.TestCase):
    
    def runTest(self):
        pass

    def testComposerClassification(self):
        from music21 import stream, note, features, corpus

        features = [
            features.jSymbolic.PitchClassDistributionFeature, features.jSymbolic.FifthsPitchHistogramFeature, 
            features.jSymbolic.BasicPitchHistogramFeature, 
            features.jSymbolic.ChangesOfMeterFeature
            ]
        worksBach = [
            'bwv3.6.xml', 'bwv5.7.xml', 'bwv32.6.xml',
            ]
        worksMonteverdi = [
            'madrigal.3.1.xml', 'madrigal.3.2.xml', 'madrigal.3.9.xml',
            ]


if __name__ == "__main__":
    music21.mainTest(Test)

#------------------------------------------------------------------------------
# eof





