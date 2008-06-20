# -*- coding: utf-8 -*-
###############################################################################
# $Copy$
###############################################################################
""" Utility for bibliography conversions


$Id$
"""
__docformat__ = 'reStructuredText'
__author__  = 'Tom Gross <itconsense@gmail.com>'

# python imports
from subprocess import Popen, PIPE
import logging

# zope2 imports
try:
    import Acquisition
    UtilityBaseClass = Acquisition.Explicit
except ImportError:
    UtilityBaseClass = object

# zope3 imports
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.traversing.browser.absoluteurl import absoluteURL

# plone imports

# third party imports

# own factory imports
from bibliograph.core.encodings import UNICODE_ENCODINGS
from bibliograph.core.encodings import _python_encodings
from bibliograph.core.interfaces import IBibliographyExport
from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.interfaces import IBibContainerIterator
from bibliograph.core.utils import _convertToOutputEncoding
from bibliograph.core.utils import title_or_id
from bibliograph.core.utils import _encode
from bibliograph.core.utils import bin_search

from bibliograph.rendering.interfaces import IBibTransformUtility

log = logging.getLogger('bibliograph.rendering')

###############################################################################

commands = {'bib2xml':'bib2xml',
            'copac2xml':'copac2xml',
            'end2xml':'end2xml',
            'isi2xml':'isi2xml',
            'med2xml':'med2xml',
            'ris2xml':'ris2xml',
            'xml2bib':'xml2bib',
            'xml2end':'xml2end',
            'xml2ris':'xml2ris',
            'copac2bib':'copac2xml | xml2bib ',
            'end2bib':'end2xml | xml2bib ',
            'isi2bib':'isi2xml | xml2bib ',
            'med2bib':'med2xml | xml2bib ',
            'ris2bib':'ris2xml | xml2bib ',
            'bib2end':'bib2xml | xml2end -o unicode',
            'bib2ris':'bib2xml | xml2ris -o unicode',
            'copac2end':'copac2xml | xml2end ',
            'isi2end':'isi2xml | xml2end ',
            'med2end':'med2xml | xml2end ',
            'ris2end':'ris2xml | xml2end ',
            'end2ris':'end2xml | xml2ris ',
            'copac2ris':'copac2xml | xml2ris ',
            'isi2ris':'isi2xml | xml2ris ',
            'med2ris':'med2xml | xml2ris ',
            }

def _getKey(source_format, target_format):
    return '2'.join([source_format, target_format])


def _hasCommands(command):
    """ Check if a collection of piped commands is available

        >>> _hasCommands('python -o|python -wrt')
        True

        >>> _hasCommands(' something_strange -m | python')
        False

    """
    for cmd in command.split('|'):
        cmd = cmd.strip()
        if ' ' in cmd:
            cmd = cmd[:cmd.find(' ')]
        if bin_search(cmd, False) is False:
            log.warn('Command %s not found in search path!', cmd)
            return False
    return True

_marker = object()
def _getCommand(source_format, target_format, default=_marker):
    key = _getKey(source_format, target_format)
    command = commands.get(key, None)
    if command is None:
        raise ValueError, "No transformation from '%s' to '%s' found." \
              % (source_format, target_format)

    if not _hasCommands(command):
        if default is _marker:
            raise LookupError, "Command %s not found." % command
        else:
            return default
    return command

###############################################################################

class ExternalTransformUtility(object):

    implements(IBibTransformUtility)

    def render(self, data, source_format, target_format, output_encoding=None):
        """ Transform data from 'source_format'
            to 'target_format'

            We have nothing, so we do nothing :)
            >>> if _getCommand('bib', 'end', None) is not None: 
            ...     result = ExternalTransformUtility().render('', 'bib', 'end')
            ...     assert result == ''

            >>> data = '''
            ...   @Book{bookreference.2008-02-04.7570607450,
            ...     author = {Werner, kla{\"u}s},
            ...     title = {H{\"a}rry Motter},
            ...     year = {1980},
            ...     publisher = {Diogenes}
            ...   }'''

            This should work. (If external bibutils are installed!)
            We transform the `bib`-format into the `end`-format
            >>> if _hasCommands(commands.get('bib2end')):
            ...     result = ExternalTransformUtility().render(data, 'bib', 'end')
            ...     assert '''
            ... %0 Book
            ... %A Werner, kla"us title =. H"arry Motter
            ... %D 1980
            ... %I Diogenes
            ... %F bookreference.2008-02-04.7570607450 '''.strip() in result

            This one is not allowed. No valid transformer exists for
            `foo` and `bar` (foo2bar)
            >>> ExternalTransformUtility().render(data, 'foo', 'bar')
            Traceback (most recent call last):
            ...
            ValueError: No transformation from 'foo' to 'bar' found.

        """
        command = _getCommand(source_format, target_format)
        if not command:
            return ''
        
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                  close_fds=True)
        (fi, fo, fe) = (p.stdin, p.stdout, p.stderr)
        fi.write(_encode(data))
        fi.close()
        result = fo.read()
        fo.close()
        error = fe.read()
        fe.close()
        if error:
            # command could be like 'ris2xml', or 'ris2xml | xml2bib'. It
            # seems unlikely, but we'll code for an arbitrary number of
            # pipes...
            command_list = command.split(' | ')
            for each in command_list:
                if each in error and not result:
                    log.error("'%s' not found. Make sure 'bibutils' is installed.",
                              command)
        if output_encoding is None:
            return result
        else:
            return _convertToOutputEncoding(result,
                                            output_encoding=output_encoding)

    transform = render

###############################################################################

class BibtexExport(UtilityBaseClass):

    implements(IBibTransformUtility)

    __name__ = u'BibTeX'
    source_format = None
    target_format = u'bib'
    description = u''
    available_encodings = _python_encodings
    default_encoding = u''

    available = True
    enabled = True

    def render(self, objects, output_encoding=None,
                     title_force_uppercase=False,
                     msdos_eol_style=False):
        """ Export a bunch of bibliographic entries in bibex format.
        """
        resolve_unicode = output_encoding not in UNICODE_ENCODINGS

        if not isinstance(objects, (list, tuple)):
            objects = [objects]

        request = getattr(objects[0], 'REQUEST', None)
        if request is None:
            request = TestRequest()

        if IBibliographyExport.providedBy(objects[0]):
            entries = IBibContainerIterator(objects[0], [])
            rendered = []
            for entry in entries:
                # call prehook
                prehook = getattr(entries, 'prehook', None)
                if callable(prehook): entry = entries.prehook(entry)

                adapter = IBibliographicReference(entry, None)
                if adapter is None: continue

                # do rendering for entry
                view = getMultiAdapter((adapter, request),
                                       name=u'bibliography.bib')
                bibtex_string = view.render(
                    resolve_unicode=resolve_unicode,
                    title_force_uppercase=title_force_uppercase,
                    msdos_eol_style=msdos_eol_style,
                    )
                rendered.append(bibtex_string)

                # call posthook
                posthook = getattr(entries, 'posthook', None)
                if callable(posthook): entries.posthook(entry)

            return _convertToOutputEncoding(''.join(rendered),
                                            output_encoding=output_encoding)

        # processing a single or a list of BibRef Items
        else:
            rendered = []
            for entry in objects:
                view = getMultiAdapter((entry, request),
                                       name=u'bibliography.bib')
                bibtex = view.render(
                    resolve_unicode=resolve_unicode,
                    title_force_uppercase=title_force_uppercase,
                    msdos_eol_style=msdos_eol_style)
                rendered.append(bibtex)
            if output_encoding is not None:
                return _convertToOutputEncoding(''.join(rendered),
                                                output_encoding=output_encoding)
            else:
                return ''.join(rendered)
        return ''

###############################################################################

class EndnoteExport(UtilityBaseClass):
    """ Export a bunch of bibliographic entries in endnote format.
    """

    implements(IBibTransformUtility)

    __name__ = u'EndNote'
    source_format = u'bib'
    target_format = u'end'
    description = u''

    enabled = True

    available_encodings = _python_encodings
    default_encoding = u''

    @property
    def available(self):
        return bool(_getCommand(self.source_format, self.target_format, False))
        
    def render(self, objects, output_encoding=None,
                     title_force_uppercase=False,
                     msdos_eol_style=False):
        """ do it
        """
        source = BibtexExport().render(objects,
                              output_encoding='iso-8859-1',
                              title_force_uppercase=title_force_uppercase,
                              msdos_eol_style=msdos_eol_style)
        transform = getUtility(IBibTransformUtility, name=u"external")
        return transform.render(source,
                                self.source_format,
                                self.target_format,
                                output_encoding)

###############################################################################

class RisExport(EndnoteExport):
    """ Export a bunch of bibliographic entries in ris format.
    """
    __name__ = u'RIS'
    target_format = u'ris'
    description = u''

    enabled = True

###############################################################################

class XmlExport(EndnoteExport):
    """ Export a bunch of bibliographic entries in xml format.
    """

    __name__ = u'XML (MODS)'
    target_format = u'xml'
    description = u''

    enabled = True

###############################################################################

class PdfExport(UtilityBaseClass):
    """ Export a bunch of bibliographic entries in pdf format.
    """

    implements(IBibTransformUtility)

    __name__ = u'PDF'
    source_format = u''
    target_format = u'pdf'
    description = u''

    enabled = True

    available_encodings = []
    default_encoding = u''

    @property
    def available(self):
        return bool(_hasCommands('latex|bibtex|pdflatex'))
    
    def render(self, objects, output_encoding=None,
                     title_force_uppercase=False,
                     msdos_eol_style=False):
        """ do it
        """
        if not isinstance(objects, (list, tuple)):
            objects = [objects]

        source = BibtexExport().render(objects,
                              output_encoding='iso-8859-1',
                              title_force_uppercase=True)
        context = objects[0]
        request = getattr(context, 'REQUEST', TestRequest())
        view = getMultiAdapter((context, request), name=u'bibliography.pdf')
        return view.processSource(source,
                                  title=title_or_id(context),
                                  url=absoluteURL(context, request))

# EOF
