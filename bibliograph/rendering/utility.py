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
import sys
import time
import logging
import tempfile
from subprocess import Popen, PIPE

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

try:
    from Products.CMFBibliographyAT.interface import IBibliographicItem
    HAVE_CMFBIB_AT = True
except:
    HAVE_CMFBIB_AT = False


# plone imports

# third party imports

# own factory imports
from bibliograph.core.interfaces import IBibliography
from bibliograph.core.interfaces import IBibliographyExport
from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.utils import _normalize
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
        try:
            if 'BIBUTILS_PATH' in os.environ:
                os.environ['PATH']=os.pathsep.join([os.environ['BIBUTILS_PATH'],
                                                    orig_path])

            ts = time.time()

            # This is a stinking workaround  with hanging subprocesses on Linux.
            # We had the case where "end2xml | xml2bib " was just hanging
            # while reading the results from the output pipeline. So we fall
            # back in a safe way to os.system() on Linux

            if sys.platform.startswith('linux'):
    
                input_filename = tempfile.mktemp()
                error_filename = tempfile.mktemp()
                output_filename = tempfile.mktemp()
                file(input_filename, 'wb').write(_encode(data))
                command = 'cat "%s" | %s 2>"%s" 1>"%s"' % (input_filename, command, error_filename, output_filename)
                st = os.system(command)
                error = file(output_filename, 'rb').read()
                result = file(output_filename, 'rb').read()
                os.unlink(input_filename)
                os.unlink(output_filename)
                os.unlink(error_filename)
    
            else:
                ts = time.time()
                log.info(command)
                p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                          close_fds=False)
                (fi, fo, fe) = (p.stdin, p.stdout, p.stderr)
                fi.write(_encode(data))
                fi.close()
                result = fo.read()
                fo.close()
                error = fe.read()
                fe.close()

            log.info('Execution time: %2.2f seconds' % (time.time() - ts))

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
        finally:
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
    description = u'Export to native BibTeX format (with LaTeX escaping)'
    view_name = u'reference.bib'
    available = True
    enabled = True

    def render(self, objects,
                     title_force_uppercase=False,
                     output_encoding=None,
                     msdos_eol_style=False,
                     omit_fields_mapping={}):
        """ Export a bunch of bibliographic entries in bibex format"""

        # This implementation here is completely bullshit from the 
        # beginning. Why is there no interface and API for getting hold
        # of the exportable items? The iterator interface here sucks.
        # This method should also work with *single* bibliographic entries.

        #request = getattr(objects[0], 'REQUEST', None)
        #if request is None:
        request = TestRequest()

        # Adapt to IBibliography if necessary/possible
        # If not, it could be ok if `entries' can be iterated over anyway.
        objects = IBibliography(objects, objects)

        found = False
        if HAVE_CMFBIB_AT:
            if IBibliographicItem.providedBy(objects):
                entries = [objects]
                found = True

        if not found:
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
            omit_fields = omit_fields_mapping.get(ref.publication_type, [])
            bibtex_string = view.render(title_force_uppercase=title_force_uppercase,
                                        omit_fields=omit_fields
                                        )
            rendered.append(bibtex_string)

        rendered = ''.join(rendered)
        if msdos_eol_style:
            rendered = rendered.replace('\n', '\r\n')
        return rendered


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
    description = u'Export to EndNote format (UTF-8 encoded)'
    enabled = True

    @property
    def available(self):
        return bool(_getCommand(self.source_format, self.target_format, False))

    def render(self, objects, output_encoding=None,
                     title_force_uppercase=False,
                     msdos_eol_style=False,
                     omit_fields_mapping={}):
        """ do it """

        source = BibtexRenderer().render(objects,
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
    description = u'Export to RIS format (Research Information Systems/Reference Manager, UTF-8 encoded)'

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
    description = u'XML/MODS (UTF-8 encoded)'

    enabled = True

    def render(self, objects, output_encoding=None,
                     title_force_uppercase=False,
                     msdos_eol_style=False,
                     omit_fields_mapping={}):
        """ do it """

        # render with output_encoding=None in order to avoid a duplicate conversion
        # the output of 'bib2xml -un' to utf-8 (it is utf-8 already)
        return super(XmlRenderer, self).render(objects, 
                                               output_encoding=None,
                                               title_force_uppercase=title_force_uppercase,
                                               msdos_eol_style=msdos_eol_style,
                                               omit_fields_mapping=omit_fields_mapping
                                               )

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
    description = u'Generate PDF'

    enabled = True

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

        if not IBibliographyExport.providedBy(context):
            try:
                context = context.aq_parent
            except AttributeError:
                pass

        source = BibtexRenderer().render(objects, title_force_uppercase=True)
        request = getattr(context, 'REQUEST', TestRequest())
        view = getMultiAdapter((context, request), name=u'reference.pdf')
        return view.processSource(source,
                                  title=title_or_id(context),
                                  url=absoluteURL(context, request))
