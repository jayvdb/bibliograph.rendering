# -*- coding: utf-8 -*-
###############################################################################
# $Copy$
###############################################################################
""" Bibtex render view

$Id$
"""
__docformat__ = 'reStructuredText'
__author__  = 'Tom Gross <itconsense@gmail.com>'

# python imports
import logging

# zope imports
from zope.interface import implements

# third party imports

# own factory imports
from bibliograph.core import utils
from bibliograph.rendering.interfaces import IReferenceRenderer
from base import BaseRenderer

###############################################################################

log = logging.getLogger('bibliograph.rendering')

###############################################################################

class BibtexRenderView(BaseRenderer):
    """A view rendering an IBibliographicReference to BibTeX.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IReferenceRenderer, BibtexRenderView)
    True
    """

    implements(IReferenceRenderer)

    file_extension = 'bib'

    def render(self, resolve_unicode=False,
                     title_force_uppercase=False,
                     msdos_eol_style=False,
                     output_encoding=None,
                     omit_fields=[]):
        """
        renders a BibliographyEntry object in BiBTex format
        """
        entry = self.context
        omit = [each.lower() for each in omit_fields]
        bib_key = utils._validKey(entry)
        bibtex = "\n@%s{%s," % (entry.publication_type, bib_key)

        if entry.editor_flag and self._isRenderableField('editor', omit):
            bibtex += "\n  editor = {%s}," % entry.authors
        elif not entry.editor_flag and self._isRenderableField('authors', omit):
            bibtex += "\n  author = {%s}," % entry.authors
        if self._isRenderableField('authorurls', omit):
            aURLs = utils.AuthorURLs(entry)
            if aURLs.find('http') > -1:
                bibtex += "\n  authorURLs = {%s}," % aURLs
        if self._isRenderableField('title', omit):
            if title_force_uppercase:
                bibtex += "\n  title = {%s}," % utils._braceUppercase(entry.title)
            else:
                bibtex += "\n  title = {%s}," % entry.title
        if self._isRenderableField('year', omit):
            bibtex += "\n  year = {%s}," % entry.publication_year
        if entry.url and self._isRenderableField('url', omit):
            bibtex += "\n  URL = {%s}," % entry.url
        if entry.abstract and self._isRenderableField('abstract', omit):
            bibtex += "\n  abstract = {%s}," % entry.abstract

        for key, val in entry.source_fields:
            if self._isRenderableField(key, omit) and val:
                if not isinstance(val, unicode):
                    val = utils._decode(val)
                bibtex += "\n  %s = {%s}," % (key.lower(), val)

        if self._isRenderableField('subject', omit):
            kws = ', '.join(entry.subject)
            if kws:
                if not isinstance(kws, unicode):
                    kws = utils._decode(kws)
                bibtex += "\n  keywords = {%s}," % kws
        if self._isRenderableField('note', omit):
            note = getattr(entry, 'note', None)
            if note:
                bibtex += "\n  note = {%s}," % note
        if self._isRenderableField('annote', omit):
            annote = getattr(entry, 'annote', None)
            if annote:
                bibtex += "\n  annote = {%s}," % annote
        if bibtex[-1] == ',':
            bibtex = bibtex[:-1] # remove the trailing comma
        bibtex += "\n}\n"
        bibtex = utils._normalize(bibtex, resolve_unicode=resolve_unicode)

        # leave these lines to debug _utf8enc2latex_mapping problems (for now)
        try:
            if resolve_unicode: debug = utils._decode(bibtex).encode('latin-1')
        except UnicodeEncodeError:
            log.error(
                'UnicodeEncodeError (latin-1): caused by object with ID: %s',
                bib_key
                )

        if msdos_eol_style:
            bibtex = bibtex.replace('\n', '\r\n')
        if output_encoding is not None:
            return bibtex.encode(output_encoding)
        else:
            return bibtex
