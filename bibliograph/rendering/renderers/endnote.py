# -*- coding: utf-8 -*-
###############################################################################
# $Copy$
###############################################################################
""" Render views for transformable bibliographies

$Id$
"""
__docformat__ = 'reStructuredText'
__author__  = 'Tom Gross <itconsense@gmail.com>'

# python imports
import logging

# zope2 imports

# zope3 imports
from zope.interface import implements
from zope import component

# plone imports

# third party imports

# own factory imports
from bibliograph.rendering.interfaces import IBibliographyRenderer
from bibliograph.rendering.interfaces import IBibTransformUtility

###############################################################################

log = logging.getLogger('bibliograph.rendering')

###############################################################################

class EndnoteRenderView(object):
    """ A view rendering a bibliography """

    implements(IBibliographyRenderer)

    source_format = u'bib'
    target_format = u'end'

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
                           output_encoding=output_encoding)

    def render(self, resolve_unicode=False,
                     title_force_uppercase=False,
                     msdos_eol_style=False,
                     output_encoding=None
                     ):
        """
        renders a BibliographyEntry object in EndNote format
        """
        bibrender = component.queryMultiAdapter((self.context, self.request),
            name=u'bibliography.bib')
        source = bibrender.render(msdos_eol_style=msdos_eol_style,
                                  resolve_unicode=True,
                                  output_encoding='ascii'
                                  )

        transform = component.getUtility(IBibTransformUtility,
                                         name=u"external")
        return transform.render(
            source, self.source_format, self.target_format, output_encoding)

###############################################################################

class RisRenderView(EndnoteRenderView):
    """ A view rendering a bibliography """

    target_format = 'ris'

###############################################################################

class XmlRenderView(EndnoteRenderView):
    """ A view rendering a bibliography """

    target_format = 'xml'

