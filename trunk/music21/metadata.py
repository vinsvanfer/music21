#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:         duration.py
# Purpose:      music21 classes for representing score and work meta-data
#
# Authors:      Christopher Ariza
#
# Copyright:    (c) 2010 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------
'''Classes and functions for creating and processing score meta data, such as titles, movements, authors, publishers, and regions.
'''


import unittest, doctest
import datetime

from music21 import common


from music21 import environment
_MOD = "metadata.py"
environLocal = environment.Environment(_MOD)




class MetadataException(Exception):
    pass


# error can be designated
APPROXIMATE = ['~', 'x']
UNCERTAIN = ['?', 'z']

def errorToSymbol(value):
    '''
    >>> errorToSymbol('approximate')
    '~'
    >>> errorToSymbol('uncertain')
    '?'
    '''
    if value.lower() in APPROXIMATE + ['approximate']:
        return APPROXIMATE[0]
    if value.lower() in UNCERTAIN + ['uncertain']:
        return UNCERTAIN[0]

# contributors can have roles
ROLES = ['com', 'coa', 'cos', 'col', 'coc', 'lyr', 'lib', 'lar', 'lor', 'trn']
# !!!COM: Composer's name.
# !!!COA: Attributed composer.
# !!!COS: Suspected composer.
# !!!COL: Composer abbreviated, alias, 
# !!!COC: Composer(s) corporate name.
# !!!LYR: Lyricist. 
# !!!LIB: Librettist. 
# !!!LAR: Arranger. 
# !!!LOR: Orchestrator. 
# !!!TRN: Translator of text. 

def roleToStr(value):
    '''Get roles as string-like attributes, used for Contributors. 

    >>> roleToStr('com')
    'composer'
    >>> roleToStr('lib')
    'librettist'
    >>> for id in ROLES: 
    ...    post = roleToStr(id)
    '''
    value = value.lower()
    if value in ['com']:
        return 'composer'
    elif value in ['coa']:
        return 'attributedComposer'
    elif value in ['cos']:
        return 'suspectedComposer'
    elif value in ['col']:
        return 'composerAlias'
    elif value in ['coc']:
        return 'composerCorporate'
    elif value in ['lyr']:
        return 'lyricist'
    elif value in ['lib']:
        return 'librettist'
    elif value in ['lar']:
        return 'arranger'
    elif value in ['lor']:
        return 'orchestrator'
    elif value in ['trn']:
        return 'translator'
    else:
        raise MetadataException('no such role: %s' % value)

ROLE_STRINGS = [roleToStr(x) for x in ROLES]

def strToRole(value):
    '''Get a role id from a string representation.

    >>> strToRole('composer')
    'com'
    >>> for n in ROLE_STRINGS:
    ...     post = strToRole(n)
    '''
    # note: probably not the fastest way to do this
    for id in ROLES:
        if value.lower() == roleToStr(id).lower():
            return id
    raise MetadataException('no such role: %s' % value)


# contributors can have roles
WORK_IDS = ['otl', 'otp', 'ota', 'opr', 'oac', 
            'osc', 'omv', 'omd', 'ops', 'onm', 
            'ovm', 'ode', 'oco', 'gtl', 'gaw', 
            'gco', 'txo', 'txl', 'ocy', 'opc']
# !!!OTL: Title. 
# !!!OTP: Popular Title.
# !!!OTA: Alternative title.
# !!!OPR: Title of larger (or parent) work 
# !!!OAC: Act number.
# !!!OSC: Scene number.
# !!!OMV: Movement number.
# !!!OMD: Movement designation or movement name. 
# !!!OPS: Opus number. 
# !!!ONM: Number.
# !!!OVM: Volume.
# !!!ODE: Dedication. 
# !!!OCO: Commission
# !!!GTL: Group Title. 
# !!!GAW: Associated Work. 
# !!!GCO: Collection designation. 
# !!!TXO: Original language of vocal/choral text. 
# !!!TXL: Language of the encoded vocal/choral text. 
# !!!OCY: Country of composition. 
# !!!OPC: City, town or village of composition. 

def workIdToStr(value):
    '''Get roles as string-like attributes, used for Contributors. 

    >>> workIdToStr('otl')
    'title'
    >>> for id in WORK_IDS: 
    ...    post = workIdToStr(id)
    '''
    value = value.lower()
    if value in ['otl']:
        return 'title'
    elif value in ['otp']:
        return 'popularTitle'
    elif value in ['ota']:
        return 'alternativeTitle'
    elif value in ['opr']:
        return 'parentTitle'
    elif value in ['oac']:
        return 'actNumber'
    elif value in ['osc']:
        return 'sceneNumber'
    elif value in ['omv']:
        return 'movementNumber'
    elif value in ['omd']:
        return 'movementName'
    elif value in ['ops']:
        return 'opusNumber'
    elif value in ['onm']:
        return 'number'
    elif value in ['ovm']:
        return 'volume'
    elif value in ['ode']:
        return 'dedication'
    elif value in ['oco']:
        return 'commission'
    elif value in ['gtl']:
        return 'groupTitle'
    elif value in ['gaw']:
        return 'associatedWork'
    elif value in ['gco']:
        return 'collectionDesignation'
    elif value in ['txo']:
        return 'textOriginalLanguage'
    elif value in ['txl']:
        return 'textLanguage'
    elif value in ['ocy']:
        return 'countryOfComposition'
    elif value in ['opc']:
        return 'localeOfComposition'
    else:
        raise MetadataException('no such work id: %s' % value)

WORK_ID_STRINGS = [workIdToStr(x) for x in WORK_IDS]

def strToWorkId(value):
    '''Get a role id from a string representation.

    >>> strToWorkId('localeOfComposition')
    'opc'
    >>> for n in WORK_ID_STRINGS:
    ...     post = strToWorkId(n)
    '''
    # note: probably not the fastest way to do this
    for id in WORK_IDS:
        if value.lower() == workIdToStr(id).lower():
            return id
    raise MetadataException('no such role: %s' % value)


#-------------------------------------------------------------------------------
class Text(object):
    '''One unit of text data: a title, a name, or some other text data. Store the string and a language name or code.
    '''
    def __init__(self, data='', language=None):
        '''
        >>> td = Text('concerto in d', 'en')
        >>> str(td)
        'concerto in d'
        '''
        self._data = data
        self._language = language

    def __str__(self):
        return str(self._data)


#-------------------------------------------------------------------------------
class Date(object):
    '''A single date value, specified by year, month, day, hour, minute, and second. 

    Additionally, each value can be specified as `uncertain` or `approximate`; if None, assumed to be certain.
    '''
    def __init__(self, *args, **keywords):
        '''
        >>> a = Date(year=1843, yearError='approximate')
        >>> a.year
        1843
        >>> a.yearError
        'approximate'

        >>> a = Date(year='1843?')
        >>> a.yearError
        'uncertain'

        '''
        self.year = None
        self.month = None
        self.day = None
        self.hour = None
        self.minute = None
        self.second = None

        # error: can be 'approximate', 'uncertain'
        # None is assumed to be certain
        self.yearError = None
        self.monthError = None
        self.dayError = None
        self.hourError = None
        self.minuteError = None
        self.secondError = None

        self.attrNames = ['year', 'month', 'day', 'hour', 'minute', 'second']
        # format strings for data components
        self.attrStrFormat = ['%04.i', '%02.i', '%02.i', 
                              '%02.i', '%02.i', '%006.2f']

        # set any keywords supplied
        for attr in self.attrNames:
            if attr in keywords.keys():
                value, error = self._stripError(keywords[attr])
                setattr(self, attr, value)
                if error != None:
                    setattr(self, attr+'Error', error)            
        for attr in self.attrNames:
            attr = attr + 'Error'
            if attr in keywords.keys():
                setattr(self, attr, keywords[attr])

    def _stripError(self, value):
        '''Strip error symbols from a numerical value. Return cleaned source and sym. Assumed to only be one per string.

        >>> d = Date()
        >>> d._stripError('1247~')
        ('1247', 'approximate')
        >>> d._stripError('234.43?')
        ('234.43', 'uncertain')
        >>> d._stripError('234.43')
        ('234.43', None)

        '''
        if common.isNum(value): # if a number, let pass
            return value, None
        else:
            str = value

        sym = APPROXIMATE + UNCERTAIN
        found = None
        for char in str:
            if char in sym:
                found = char
                break

        if found == None:
            return str, None
        elif found in APPROXIMATE:
            str = str.replace(found, '')
            return  str, 'approximate'
        elif found in UNCERTAIN:
            str = str.replace(found, '')
            return  str, 'uncertain'


    def _getHasTime(self):
        if self.hour != None or self.minute != None or self.second != None:
            return True
        else:
            return False
       
    hasTime = property(_getHasTime, 
        doc = '''Return True if any time elements are defined.

        >>> a = Date(year=1843, month=3, day=3)
        >>> a.hasTime
        False
        >>> b = Date(year=1843, month=3, day=3, minute=3)
        >>> b.hasTime
        True

        ''')


    def _getHasError(self):
        for attr in self.attrNames:
            if getattr(self, attr+'Error') != None:
                return True
        return False
       
    hasError = property(_getHasError, 
        doc = '''Return True if any data points have error defined. 

        >>> a = Date(year=1843, month=3, day=3, dayError='approximate')
        >>> a.hasError
        True
        >>> b = Date(year=1843, month=3, day=3, minute=3)
        >>> b.hasError
        False
        ''')

    def __str__(self):
        # datetime.strftime("%Y.%m.%d")
        # cannot use this, as it does not support dates lower than 1900!
        msg = []

        if self.hour == None and self.minute == None and self.second == None:
            breakIndex = 3 # index

        for i in range(len(self.attrNames)):
            if i >= breakIndex:
                break
            attr = self.attrNames[i]
            value = getattr(self, attr)
            error = getattr(self, attr+'Error')
            if value == None:
                msg.append('--')
            else:
                fmt = self.attrStrFormat[i]
                if error != None:
                    sub = fmt % value + errorToSymbol(error)
                else:
                    sub = fmt % value
                msg.append(sub)

        return '.'.join(msg)


    def loadStr(self, str):
        '''Load a string date representation.
        
        Assume year/month/day/hour:minute:second

        >>> d = Date()
        >>> d.loadStr('3030?/12~/?4')
        >>> d.month, d.monthError
        (12, 'approximate')
        >>> d.year, d.yearError
        (3030, 'uncertain')
        >>> d.day, d.dayError
        (4, 'uncertain')
        '''
        post = []
        postError = []
        if '.' in str:
            for chunk in str.split('.'):
                value, error = self._stripError(chunk)
                post.append(value) 
                postError.append(error)
        elif '/' in str:
            for chunk in str.split('/'):
                value, error = self._stripError(chunk)
                post.append(value) 
                postError.append(error)

        # as error is stripped, we can now convert to numbers
        post = [int(x) for x in post]

        # assume in order in post list
        for i in range(len(self.attrNames)):
            if len(post) > i: # only assign for those specified
                setattr(self, self.attrNames[i], post[i])
                if postError[i] != None:
                    setattr(self, self.attrNames[i]+'Error', postError[i])            


    def loadDatetime(self, dt):
        '''Load time data from a datetime object.

        >>> import datetime
        >>> dt = datetime.datetime(2005, 02, 01)
        >>> dt
        datetime.datetime(2005, 2, 1, 0, 0)
        >>> a = Date()
        >>> a.loadDatetime(dt)
        >>> str(a)
        '2005.02.01'
        '''
        for attr in self.attrNames:
            if hasattr(dt, attr):
                # names here are the same, so we can directly map
                value = getattr(dt, attr)
                if value not in [0, None]:
                    setattr(self, attr, value)

    def loadOther(self, other):
        '''Load values based on another Date object:

        >>> a = Date(year=1843, month=3, day=3)
        >>> b = Date()
        >>> b.loadOther(a)
        >>> b.year
        1843
        '''
        for attr in self.attrNames:
            if getattr(other, attr) != None:
                setattr(self, attr, getattr(other, attr))

    def load(self, value):
        '''Load values by string, datetime object, or Date object.

        >>> a = Date(year=1843, month=3, day=3)
        >>> b = Date()
        >>> b.load(a)
        >>> b.year
        1843
        '''

        if isinstance(value, datetime.datetime):
            self.loadDatetime(value)
        elif common.isStr(value):
            self.loadStr(value)
        elif isinstance(value, Date):
            self.loadOther(value)
        else:
            raise MetadataException('cannot load data: %s' % value)    
    
    def _getDatetime(self):
        '''Get a datetime object.

        >>> a = Date(year=1843, month=3, day=3)
        >>> str(a)
        '1843.03.03'
        >>> a.datetime
        datetime.datetime(1843, 3, 3, 0, 0)

        '''
        post = []
        # order here is order for datetime
        # TODO: need defaults for incomplete times. 
        for attr in self.attrNames:
            # need to be integers
            value = getattr(self, attr)
            if value == None:
                break
            post.append(int(value))
        return datetime.datetime(*post)

    datetime = property(_getDatetime, 
        doc = '''Return a datetime object representation. 
        ''')


#-------------------------------------------------------------------------------
class DateSingle(object):
    '''Store a date, either as certain, approximate, or uncertain.

    '''
    isSingle = True

    def __init__(self, data='', relevance='certain'):
        '''
        >>> dd = DateSingle('2009/12/31', 'approximate')
        >>> str(dd)
        '2009.12.31'

        >>> dd = DateSingle('1805.3.12', 'uncertain')
        >>> str(dd)
        '1805.03.12'
        '''
        self._data = None
        self._relevance = None # managed by property

        # not yet implemented
        # store an array of values marking if date data itself
        # is certain, approximate, or uncertain
        # here, dataError is relevance
        self._dataError = None

        self._prepareData(data)
        self.relevance = relevance # will use property
    
    def _prepareData(self, data):
        '''Assume a string is supplied as argument
        '''
        self._data = Date()
        if common.isStr(data):
            self._data.loadStr(data)

    def _setRelevance(self, value):
        if value in ['certain', 'approximate', 'uncertain']:
            self._relevance = value
            self._dataError = value # only here is dataError the same as relevance
        else:
            raise MetadataException('relevance value is not supported by this object: %s' % value)

    def _getRelevance(self):
        return self._relevance

    relevance = property(_getRelevance, _setRelevance)

    def __str__(self):
        return str(self._data)


class DateRelative(DateSingle):
    '''Store a relative date, sometime prior or sometime after
    '''
    isSingle = True

    def __init__(self, data='', relevance='after'):
        '''
        >>> dd = DateRelative('2009/12/31', 'prior')
        >>> str(dd)
        '2009.12.31'

        >>> dd = DateRelative('2009/12/31', 'certain')
        Traceback (most recent call last):
        MetadataException: relevance value is not supported by this object: certain
        '''
        DateSingle.__init__(self, data, relevance)


    def _setRelevance(self, value):
        if value in ['prior', 'after']:
            self._relevance = value
        else:
            raise MetadataException('relevance value is not supported by this object: %s' % value)

    relevance = property(DateSingle._getRelevance, _setRelevance)



class DateBetween(DateSingle):
    '''Store a relative date, sometime between two dates
    '''
    isSingle = False


    def __init__(self, data=[], relevance='between'):
        '''
        >>> dd = DateBetween(['2009/12/31', '2010/1/28'])
        >>> str(dd)
        '2009.12.31 to 2010.01.28'

        >>> dd = DateBetween(['2009/12/31', '2010/1/28'], 'certain')
        Traceback (most recent call last):
        MetadataException: relevance value is not supported by this object: certain
        '''
        DateSingle.__init__(self, data, relevance)

    def _prepareData(self, data):
        '''Assume a list of dates as strings is supplied as argument
        '''
        self._data = []
        self._dataError = []
        for part in data:
            d = Date()
            if common.isStr(part):
                d.loadStr(part)
            self._data.append(d) # a lost of Date objects
            # can look at Date and determine overall error
            self._dataError.append(None)


    def __str__(self):
        msg = []
        for d in self._data:
            msg.append(str(d))
        return ' to '.join(msg)

    def _setRelevance(self, value):
        if value in ['between']:
            self._relevance = value
        else:
            raise MetadataException('relevance value is not supported by this object: %s' % value)

    relevance = property(DateSingle._getRelevance, _setRelevance)



class DateSelection(DateSingle):
    '''Store a selection of dates, or a collection of dates that might all be possible
    '''
    isSingle = False

    def __init__(self, data='', relevance='or'):
        '''
        >>> dd = DateSelection(['2009/12/31', '2010/1/28', '1894/1/28'], 'or')
        >>> str(dd)
        '2009.12.31 or 2010.01.28 or 1894.01.28'

        >>> dd = DateSelection(['2009/12/31', '2010/1/28'], 'certain')
        Traceback (most recent call last):
        MetadataException: relevance value is not supported by this object: certain
        '''
        DateSingle.__init__(self, data, relevance)

    def _prepareData(self, data):
        '''Assume a list of dates as strings is supplied as argument
        '''
        self._data = []
        self._dataError = []
        for part in data:
            d = Date()
            if common.isStr(part):
                d.loadStr(part)
            self._data.append(d) # a lost of Date objects
            # can look at Date and determine overall error
            self._dataError.append(None)

    def __str__(self):
        msg = []
        for d in self._data:
            msg.append(str(d))
        return ' or '.join(msg)

    def _setRelevance(self, value):
        if value in ['or']:
            self._relevance = value
        else:
            raise MetadataException('relevance value is not supported by this object: %s' % value)

    relevance = property(DateSingle._getRelevance, _setRelevance)





#-------------------------------------------------------------------------------
class Contributor(object):
    '''A person that contributed to a work. Can be a composer, lyricist, arranger, or other type of contributor. In MusicXML, these are "creator" elements.  
    '''
    def __init__(self, *args, **keywords ):
        '''
        >>> td = Contributor(role='composer', name='Chopin, Fryderyk')
        >>> td.role
        'composer'
        >>> td.name
        'Chopin, Fryderyk'

        >>> td = Contributor(role='composer', names=['Chopin, Fryderyk', 'Chopin, Frederick'])
        >>> td.name
        'Chopin, Fryderyk'
        >>> td.names
        ['Chopin, Fryderyk', 'Chopin, Frederick']

        '''
        if 'role' in keywords.keys():
            self.role = keywords['role'] # validated with property
        else:
            self.role = None

        # a list of Text objects to support various spellings or 
        # language translatiions
        self._names = []
        if 'name' in keywords.keys(): # a single
            self._names.append(Text(keywords['name']))
        if 'names' in keywords.keys(): # many
            for n in keywords['names']:
                self._names.append(Text(n))

        # store the nationality, if known
        self._nationality = []

        # store birth and death of contributor, if known
        self._dateRange = [None, None]
        if 'birth' in keywords.keys():
            self._dateRange[0] = Date()
            self._dateRange[0].load(keywords['birth'])
        if 'death' in keywords.keys():
            self._dateRange[0] = Date()
            self._dateRange[0].load(keywords['death'])


    def _getRole(self):
        return self._role

    def _setRole(self, value):
        if value == None or value in ROLE_STRINGS:
            self._role = value
        else:
            raise MetadataException('role value is not supported by this object: %s' % value)

    role = property(_getRole, _setRole, 
        doc = '''The role is what part this Contributor plays in the work. 
        ''')


    def _getName(self):
        # return first name
        return str(self._names[0])

    name = property(_getName, 
        doc = '''Returns the first entered name.
        ''')

    def _getNames(self):
        # return first name
        msg = []
        for n in self._names:
            msg.append(str(n))
        return msg

    names = property(_getNames, 
        doc = '''Returns all names in a list.
        ''')

    def age(self):
        if self._dateRange[0] != None and self._dateRange[1] != None:
            b = self._dateRange[0].datetime
            d = self._dateRange[1].datetime
            pass
        else:
            return None


#-------------------------------------------------------------------------------
# as these have Date and Text fields, these need to be specialized objects

class Imprint(object):
    pass
# !!!PUB: Publication status. 
# !!!PPR: First publisher. 
# !!!PDT: Date first published. 
# !!!PPP: Place first published. 
# !!!PC#: Publisher's catalogue number. 
# !!!SCT: Scholarly catalogue abbreviation and number. E.g. BWV 551
# !!!SCA: Scholarly catalogue (unabbreviated) name. E.g.Koechel 117.
# !!!SMS: Manuscript source name. 
# !!!SML: Manuscript location. 
# !!!SMA: Acknowledgement of manuscript access.


class Copyright(object):
    pass
# !!!YEP: Publisher of electronic edition. 
# !!!YEC: Date and owner of electronic copyright. 
# !!!YER: Date electronic edition released.
# !!!YEM: Copyright message. 
# !!!YEN: Country of copyright. 
# !!!YOR: Original document. 
# !!!YOO: Original document owner. 
# !!!YOY: Original copyright year.
# !!!YOE: Original editor. 


#-------------------------------------------------------------------------------
class Metadata(object):
    '''Metadata for a work, including title, composer, dates, and other relevant information.
    '''
    # possible rename Work?
    

    def __init__(self, *args, **keywords ):
        '''
        >>> md = Metadata(title='Concerto in F')
        '''
        # a lost of Contributor objects
        # there can be more than one composer, or any other combination
        self._contributors = []

        self._date = None

        # need a specific object for copyright and imprint
        self._imprint = None
        self._copyright = None

        # a dictionary of Text elements, where keys are work id strings
        # all are loaded with None by default
        self._workIds = {}
        for idStr in WORK_ID_STRINGS:
            id = strToWorkId(idStr)
            if id in keywords.keys():
                self._workIds[idStr] = Text(keywords[id])
            elif idStr in keywords.keys():
                self._workIds[idStr] = Text(keywords[idStr])
            else:
                self._workIds[idStr] = None

    def _getTitle(self):
        searchId = ['title', 'popularTitle', 'alternativeTitle', 'movementName']
        post = None
        for key in searchId:
            post = self._workIds[key]
            if post != None: # get first matched
                # get a string from this Text object
                return str(self._workIds[key])

    def _setTitle(self, value):
        self._workIds['title'] = Text(value)

    title = property(_getTitle, _setTitle, 
        doc = '''Get the title of the work, or the next matched title string.

        >>> md = Metadata(title='Concerto in F')
        >>> md.title
        'Concerto in F'
        ''')

#-------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def runTest(self):
        pass



#-------------------------------------------------------------------------------
_DOC_ORDER = [Text]


if __name__ == "__main__":
    import sys
    import music21
    
    if len(sys.argv) == 1: # normal conditions
        music21.mainTest(Test)
    elif len(sys.argv) > 1:
        a = Test()
        a.testAugmentOrDiminish()