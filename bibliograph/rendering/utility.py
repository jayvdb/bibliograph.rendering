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
import os
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
from zope.component import queryAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.traversing.browser.absoluteurl import absoluteURL

# plone imports

# third party imports

# own factory imports
from bibliograph.core.encodings import UNICODE_ENCODINGS
from bibliograph.core.encodings import _python_encodings
from bibliograph.core.interfaces import IBibliography
from bibliograph.core.interfaces import IBibliographyExport
from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.utils import _convertToOutputEncoding
from bibliograph.core.utils import title_or_id
from bibliograph.core.utils import _encode
from bibliograph.core.bibutils import _getCommand
from bibliograph.core.bibutils import _hasCommands
from bibliograph.core.bibutils import commands

from bibliograph.rendering.interfaces import IBibTransformUtility
from bibliograph.rendering.interfaces import IReferenceRenderer
from bibliograph.rendering.interfaces import IBibliographyRenderer

log = logging.getLogger('bibliograph.rendering')

###############################################################################



###############################################################################

class ExternalTransformUtility(object):
    """An implementation of IBibTransformUtility

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IBibTransformUtility, ExternalTransformUtility)
    True
    """

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
            ...     # We need to take care of any stray Windows carriage returns.
            ...     result = result.replace('\r', '')
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

        orig_path = os.environ['PATH']
        if os.environ.has_key('BIBUTILS_PATH'):
            os.environ['PATH'] = os.pathsep.join([orig_path,
                                                  os.environ['BIBUTILS_PATH']])

        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                  close_fds=False)
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
        os.environ['PATH'] = orig_path

    transform = render

###############################################################################

class BibtexRenderer(UtilityBaseClass):
    """An implementation of IBibliographyRenderer that renders to BibTeX.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IBibliographyRenderer, BibtexRenderer)
    True
    """

    implements(IBibliographyRenderer)

    __name__ = u'BibTeX'
    source_format = None
    target_format = u'bib'
    description = u''
    available_encodings = _python_encodings
    default_encoding = u''
    view_name = u'reference.bib'

    available = True
    enabled = True

    def render(self, objects,
                     output_encoding=None,
                     title_force_uppercase=False,
                     msdos_eol_style=False,
                     omit_fields_mapping={}):
        """ Export a bunch of bibliographic entries in bibex format.
        """
        resolve_unicode = output_encoding not in UNICODE_ENCODINGS

        #request = getattr(objects[0], 'REQUEST', None)
        #if request is None:
        request = TestRequest()

        # Adapt to IBibliography if necessary/possible
        # If not, it could be ok if `entries' can be iterated over anyway.
        objects = IBibliography(objects, objects)

        try:
            # We want the values from a dictionary-ish/IBibliography object
            entries = objects.itervalues()
        except AttributeError:
            # Otherwise we just iterate over what is presumably something
            # sequence-ish.
            entries = iter(objects)
        rendered = []

        for obj in entries:
            ref = queryAdapter(obj, interface=IBibliographicReference,
                                    name=self.__name__)
            if ref is None:
                # if there is no named adapter, get the default adapter
                # compatibility with older versions
                ref = IBibliographicReference(obj, None)
            if ref is None:
                continue

            # do rendering for entry
            view = getMultiAdapter((ref, request), name=self.view_name)
            omit_fields = omit_fields_mapping.get(ref.publication_type,
                                                  [])
            bibtex_string = view.render(
                resolve_unicode=resolve_unicode,
                title_force_uppercase=title_force_uppercase,
                msdos_eol_style=msdos_eol_style,
                omit_fields=omit_fields
                )
            rendered.append(bibtex_string)

        return _convertToOutputEncoding(''.join(rendered),
                                        output_encoding=output_encoding)


###############################################################################

class EndnoteRenderer(UtilityBaseClass):
    """An implementation of IBibliographyRenderer that renders to the Endnote
    format.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IBibliographyRenderer, EndnoteRenderer)
    True
    """

    implements(IBibliographyRenderer)

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
                     msdos_eol_style=False,
                     omit_fields_mapping={}):
        """ do it
        """
        source = BibtexRenderer().render(objects,
                              output_encoding='iso-8859-1',
                              title_force_uppercase=title_force_uppercase,
                              msdos_eol_style=msdos_eol_style)
        transform = getUtility(IBibTransformUtility, name=u"external")
        return transform.render(source,
                                self.source_format,
                                self.target_format,
                                output_encoding)

###############################################################################

class RisRenderer(EndnoteRenderer):
    """An implementation of IBibliographyRenderer that renders to the RIS
    format.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IBibliographyRenderer, RisRenderer)
    True
    """

    __name__ = u'RIS'
    target_format = u'ris'
    description = u''

    enabled = True

###############################################################################

class XmlRenderer(EndnoteRenderer):
    """An implementation of IBibliographyRenderer that renders to the XML (MODS)
    format.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IBibliographyRenderer, XmlRenderer)
    True
    """

    __name__ = u'XML (MODS)'
    target_format = u'xml'
    description = u''

    enabled = True

###############################################################################

class PdfRenderer(UtilityBaseClass):
    """An implementation of IBibliographyRenderer that renders to a PDF file.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IBibliographyRenderer, PdfRenderer)
    True
    """

    implements(IBibliographyRenderer)

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
                     msdos_eol_style=False,
                     omit_fields_mapping={}):
        """ do it
        """
        if isinstance(objects, (list, tuple)):
            context = objects[0]
        else:
            context = objects

        source = BibtexRenderer().render(objects,
                              output_encoding='iso-8859-1',
                              title_force_uppercase=True)
        request = getattr(context, 'REQUEST', TestRequest())
        view = getMultiAdapter((context, request), name=u'reference.pdf')
        return view.processSource(source,
                                  title=title_or_id(context),
                                  url=absoluteURL(context, request))

# EOF
