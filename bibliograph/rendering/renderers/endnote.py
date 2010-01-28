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

# zope imports
from zope.interface import implements
from zope import component

# third party imports

# own factory imports
from bibliograph.rendering.interfaces import IReferenceRenderer
from bibliograph.rendering.interfaces import IBibTransformUtility
from base import BaseRenderer

###############################################################################

log = logging.getLogger('bibliograph.rendering')

###############################################################################

class EndnoteRenderView(BaseRenderer):
    """A view rendering an IBibliographicReference to the Endnote format.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IReferenceRenderer, EndnoteRenderView)
    True
    """

    implements(IReferenceRenderer)

    source_format = u'bib'
    target_format = u'end'

    file_extension = 'end'

    def render(self, resolve_unicode=False,
                     title_force_uppercase=False,
                     msdos_eol_style=False,
                     output_encoding=None,
                     omit_fields=[]
                     ):
        """
        renders a BibliographyEntry object in EndNote format
        """
        bibrender = component.queryMultiAdapter((self.context, self.request),
            name=u'reference.bib')
        source = bibrender.render(omit_fields=omit_fields)

        transform = component.getUtility(IBibTransformUtility,
                                         name=u"external")
        return transform.render(
            source, self.source_format, self.target_format, output_encoding)

###############################################################################

class RisRenderView(EndnoteRenderView):
    """A view rendering an IBibliographicReference to the RIS format.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IReferenceRenderer, RisRenderView)
    True
    """

    target_format = 'ris'
    file_extension = 'ris'


###############################################################################

class XmlRenderView(EndnoteRenderView):
    """A view rendering an IBibliographicReference to the XML (MODS) format.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IReferenceRenderer, XmlRenderView)
    True
    """

    target_format = 'xml'
    file_extension = 'xml'
