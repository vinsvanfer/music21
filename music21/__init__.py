# -*- coding: utf-8 -*-
'''
The music21 Framework is Copyright © 2008-2013 Michael Scott Cuthbert 
and the music21 Project

(Michael Scott Cuthbert, principal investigator; cuthbert@mit.edu)

Some Rights Reserved
Released under the Lesser GNU Public License (LGPL)

See license.txt file for the full license which represents your legal
obligations in using, modifying, or distributing music21.

Roughly speaking, this means that anyone can use this software for
free, they can distribute it to anyone, so long as this acknowledgment
of copyright and ownership remain publicly accessible.  You may also
modify this software or use it in your own programs so long as you do
so long as you make your product available
under the same license.  You may also link to this code as a library
from your sold, proprietary commercial product so long as this code 
remains open and accessible, this license is made accessible, 
and the developers are credited.

The development of music21 was supported by grants
from the Seaver Institute and the NEH/Digging into Data Challenge, 
with the support of the MIT
Music and Theater Arts section and the School of Humanities, Arts,
and Social Sciences.  Portions of music21 were originally part of
the PMusic (Perl) library, developed by Cuthbert prior to arriving at MIT.

music21 outputs a subset of XML data defined by the  MusicXML 2.0 
standard, Copyright © Recordare LLC;  License available at
http://www.recordare.com/dtds/license.html, now transferred to MakeMusic

music21 incorporates Microsoft Excel reading via the included 
xlrd library:
   Portions copyright (c) 2005-2006, Stephen John Machin, Lingfo Pty Ltd
   All rights reserved.
see ext/xlrd/licenses.py for the complete disclaimer and conditions

Files in the ext/ folder are not copyright music21 Project but whose distribution
is compatible with music21.  The corpus files have copyrights retained by their
owners who have allowed them to be included with music21.
'''
print("NOTE: This version of music21 from GoogleCode/SVN is obsolete. "
      "Please update to the version at GitHub: https://github.com/cuthbertLab/music21 .")

# this defines what  is loaded when importing __all__
# put these in alphabetical order FIRST dirs then modules
# but: base must come first; in some cases other modules depend on 
# definitions in base

__all__ = [
    'base', 
    # sub folders
    'abc', 
    'analysis', 
    'audioSearch',
    'braille', 
    'capella',
    'composition',
    'counterpoint',
    'corpus', 
    'demos',
    'documentation',
    'features',
    'figuredBass', 
    'humdrum',
    'ipython21',
    'languageExcerpts',
    'lily', 
    'midi',
    'musedata',
    'musicxml', 
    'noteworthy',
    'romanText', 
    'scala', 'search',
    'test',
    'theoryAnalysis',
    'trecento',
    'vexflow',
    'webapps', 
    # individual modules 
    # KEEP ALPHABETICAL unless necessary for load reasons, if so
    # put a note.  Keep one letter per line.
    'articulations', 
    'bar',
    # base listed above
    'beam', 
    'chant',
    'chord',
    'chordTables', 
    'classCache',
    'clef',
    'common',
    'configure',
    'contour',
    'converter',
    'defaults',
    'derivation',
    'duration',
    'dynamics',
    'editorial',
    'environment',
    'exceptions21',
    'expressions', 
    'freezeThaw',
    'graph', 
    'harmony', 
    'instrument',
    'interval',
    'intervalNetwork', 
    'key', 
    'layout',
    'medren',
    'metadata',
    'meter', 
    'note', 
    'pitch', 
    'repeat',
    'roman',
    'scale',
    'serial',
    'sieve',
    'spanner',
    'stream', 
    'tempo',
    'text', 
    'tie',
    'tinyNotation', 
    'variant',
    'voiceLeading',
    'volume',
    'xmlnode',
    ]

#__all__.reverse()
#print __all__
# skipped purposely, "base", "xmlnode"

#-------------------------------------------------------------------------------
# for sub packages, need to manually add the modules in these subpackages
#from music21.analysis import *
#import sys
#x = sys.stdout


#-------------------------------------------------------------------------------
# base Music21Object -- all objects should inherit from this!
import base
from base import *
#del(types)
#del(sys)
#del(imp)
#del(doctest)
#del(copy)
#del(codecs)
#del(unittest)
#-------------------------------------------------------------------------------
# place the parse function directly in the music21 namespace
# this cannot go in music21/base.py
#import converter
#parse = converter.parse


#------------------------------------------------------------------------------
# this bring all of the __all__ names into the music21 package namespace
from music21 import * # @UnresolvedImport
#------------------------------------------------------------------------------
# eof


