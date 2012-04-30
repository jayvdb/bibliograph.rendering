# -*- coding: utf-8 -*-
###############################################################################
# $Copy$
###############################################################################
""" Bibtex render view

$Id$
"""
__docformat__ = 'reStructuredText'
__author__  = 'Tom Gross <itconsense@gmail.com>'

import os
import codecs
import tempfile
import logging

from zope.interface import implements

from bibliograph.core import utils
from bibliograph.core.utils import _normalize
from bibliograph.rendering.interfaces import IReferenceRenderer
from base import BaseRenderer

###############################################################################

log = logging.getLogger('bibliograph.rendering')

###############################################################################

def _c(fmt, *args):

    try:
        return fmt % args
    except UnicodeDecodeError:
        #TODO: Return the field with quotations
        args = tuple([repr(a) for a in args])
        return fmt % args


class BibtexRenderView(BaseRenderer):
    """A view rendering an IBibliographicReference to BibTeX.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IReferenceRenderer, BibtexRenderView)
    True

    """

    implements(IReferenceRenderer)

    file_extension = 'bib'

    def render(self, title_force_uppercase=False, omit_fields=[],
              msdos_eol_style=None, # not used
              resolve_unicode=None, # not used
              output_encoding=None, # not used
              ):
        """
        renders a BibliographyEntry object in BiBTex format
        """

        entry = self.context
        omit = [each.lower() for each in omit_fields]
        bib_key = utils._validKey(entry)
        f_temp = tempfile.mktemp()

        fp = codecs.open(f_temp, 'w', 'utf-8', 'ignore')
        print >>fp, _c(u"\n@%s{%s,",  entry.publication_type, bib_key)

        if entry.editor_flag and self._isRenderableField('editor', omit):
            print >>fp,  _c(u"  editor = {%s},", entry.authors)
        elif not entry.editor_flag and self._isRenderableField('authors', omit):
            print >>fp,  _c("  author = {%s},", entry.authors)
        if self._isRenderableField('authorurls', omit):
            aURLs = utils.AuthorURLs(entry)
            if aURLs.find('http') > -1:
                print >>fp,  _c(u"  authorURLs = {%s},", aURLs)
        if self._isRenderableField('title', omit):
            if title_force_uppercase:
                print >>fp,  _c(u"  title = {%s},", utils._braceUppercase(entry.title))
            else:
                print >>fp,  _c(u"  title = {%s},", entry.title)
        if self._isRenderableField('year', omit):
            print >>fp,  _c(u"  year = {%s},", entry.publication_year)
        if self._isRenderableField('month', omit):
            if entry.publication_month:
                print >>fp,  _c(u"  month = {%s},", entry.publication_month)
        if entry.url and self._isRenderableField('url', omit):
            print >>fp,  _c(u"  URL = {%s},",  entry.url)
        if entry.abstract and self._isRenderableField('abstract', omit):
            print >>fp,  _c(u"  abstract = {%s},", entry.abstract)

        for key, val in entry.source_fields:
            if self._isRenderableField(key, omit) and val:
                if not isinstance(val, unicode):
                    val = utils._decode(val)
                print >>fp,  _c(u"  %s = {%s},",  key.lower(), val)

        if self._isRenderableField('subject', omit):
            kws = ', '.join(entry.subject)
            if kws:
                if not isinstance(kws, unicode):
                    kws = utils._decode(kws)
                print >>fp,  _c(u"  keywords = {%s},", kws)
        if self._isRenderableField('note', omit):
            note = getattr(entry, 'note', None)
            if note:
                print >>fp,  _c(u"  note = {%s},", note)
        if self._isRenderableField('annote', omit):
            annote = getattr(entry, 'annote', None)
            if annote:
                print >>fp,  _c(u"  annote = {%s},", annote)
        if self._isRenderableField('additional', omit):
            try:
                additional = entry.context.getAdditional()
            except AttributeError:
                additional = []
            for mapping in additional:
                print >>fp,  _c(u"  %s = {%s},", mapping['key'], mapping['value'])

        keys = entry.identifiers.keys()
        keys.sort()
        source_fields_keys = [tp[0].lower() for tp in entry.source_fields]
        for identifier, value in entry.identifiers.items():
            if value:
                print >>fp,  _c(u"  %s = {%s},", identifier.lower(), value)


        # remove trailing command
        fp.seek(-2, 2)
        print >>fp
        print >>fp,  u"}"
        print >>fp
        fp.close()
        bibtex = file(f_temp, 'r').read()
        os.unlink(f_temp)
        return _normalize(bibtex, resolve_unicode=True)

