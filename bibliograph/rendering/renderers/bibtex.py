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

# zope2 imports

# zope3 imports
from zope.interface import implements

# plone imports
try:
    from Products.Archetypes.utils import shasattr
except:
    # we don't want to depend on Archetypes
    _marker = []
    def shasattr(obj, attr):
        return getattr(obj, attr, _marker) is not _marker

# third party imports

# own factory imports
from bibliograph.core import utils
from bibliograph.rendering.interfaces import IBibliographyRenderer

###############################################################################

log = logging.getLogger('bibliograph.rendering')

###############################################################################

class BibtexRenderView(object):
    """ A view rendering a bibliography """

    implements(IBibliographyRenderer)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        resolve_unicode = self.request.get('resolve_unicode', False)
        title_force_uppercase = self.request.get('title_force_uppercase', False)
        msdos_eol_style = self.request.get('msdos_eol_style', False)
        output_encoding = self.request.get('output_encoding', 'utf-8')
        return self.render(resolve_unicode,
                           title_force_uppercase,
                           msdos_eol_style,
                           output_encoding)

    def render(self, resolve_unicode=False,
                     title_force_uppercase=False,
                     msdos_eol_style=False,
                     output_encoding=None):
        """
        renders a BibliographyEntry object in BiBTex format
        """
        entry = self.context

        bib_key = utils._validKey(entry)
        bibtex = "\n@%s{%s," % (entry.publication_type, bib_key)
        authors = entry.getAuthors(sep=' and ',
                                lastsep=' and ',
                                format="%L, %F %M",
                                abbrev=0,
                                lastnamefirst=0)()
        if not isinstance(authors, unicode):
            authors = unicode(authors, 'utf-8')
        if shasattr(entry, 'editor_flag') and entry.editor_flag:
            bibtex += "\n  editor = {%s}," % authors
        else:
            bibtex += "\n  author = {%s}," % authors
        aURLs = utils.AuthorURLs(entry)
        if aURLs.find('http') > -1:
            bibtex += "\n  authorURLs = {%s}," % aURLs
        if title_force_uppercase:
            bibtex += "\n  title = {%s}," % utils._braceUppercase(entry.title)
        else:
            bibtex += "\n  title = {%s}," % entry.title
        bibtex += "\n  year = {%s}," % entry.publication_year
        if hasattr(entry, 'aq_base'):
            url = entry.aq_base.getURL()
        else:
            url = entry.getURL()
        if url: bibtex += "\n  URL = {%s}," % url
        bibtex += "\n  abstract = {%s}," % entry.abstract

        if shasattr(entry, 'source_fields') and entry.source_fields:
            source_fields = list(entry.source_fields)
            field_values = [entry.getFieldValue(name)
                            for name in source_fields]
            if 'publication_type' in source_fields:
                source_fields[source_fields.index('publication_type')] = 'type'
            for key, value in zip(source_fields, field_values):
                if value:
                    bibtex += "\n  %s = {%s}," % (key, value)

        kws = ', '.join(entry.subject)
        if kws:
            bibtex += "\n  keywords = {%s}," % kws
        note = getattr(entry, 'note', None)
        if note:
            bibtex += "\n  note = {%s}," % note
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


