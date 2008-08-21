# -*- coding: utf-8 -*-
import unittest

from zope.component import getUtility
from zope.interface import directlyProvides
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest

from zope.app.container.sample import SampleContainer
from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import setUp, tearDown

from bibliograph.core.interfaces import IBibContainerIterator
from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.interfaces import IBibliographyExport
from bibliograph.rendering.adapter import Zope2FolderAdapter
from bibliograph.rendering import interfaces
from bibliograph.rendering.tests.test_doctests import SimpleContent
from bibliograph.rendering import utility

class ViewInterfaceTestCase(unittest.TestCase):

    def test_bibtexrenderview(self):
        from bibliograph.rendering.renderers.bibtex import BibtexRenderView
        verifyClass(interfaces.IBibliographyRenderer, BibtexRenderView)

        request = TestRequest()
        view = BibtexRenderView(object(), request)
        verifyObject(interfaces.IBibliographyRenderer, view)
        
                
    def test_endnoterenderview(self):
        from bibliograph.rendering.renderers.endnote import EndnoteRenderView
        verifyClass(interfaces.IBibliographyRenderer, EndnoteRenderView)
        
        request = TestRequest()
        view = EndnoteRenderView(object(), request)
        verifyObject(interfaces.IBibliographyRenderer, view)


    def test_risrenderview(self):
        from bibliograph.rendering.renderers.endnote import RisRenderView
        verifyClass(interfaces.IBibliographyRenderer, RisRenderView)
        
        request = TestRequest()
        view = RisRenderView(object(), request)
        verifyObject(interfaces.IBibliographyRenderer, view)


    def test_xmlrenderview(self):
        from bibliograph.rendering.renderers.endnote import XmlRenderView
        verifyClass(interfaces.IBibliographyRenderer, XmlRenderView)

        request = TestRequest()
        view = XmlRenderView(object(), request)
        verifyObject(interfaces.IBibliographyRenderer, view)

    def test_pdfrenderview(self):
        from bibliograph.rendering.renderers.pdf import PdfRenderView
        verifyClass(interfaces.IBibliographyRenderer, PdfRenderView)

        request = TestRequest()
        view = PdfRenderView(object(), request)
        verifyObject(interfaces.IBibliographyRenderer, view)

class UtilityInterfaceTestCase(unittest.TestCase):        

    def test_externaltransform(self):
        verifyClass(interfaces.IBibTransformUtility,
                    utility.ExternalTransformUtility)
        
    def test_bibtexexport(self):
        verifyClass(IBibliographyExport, utility.BibtexExport)
        
    def test_endnoteexport(self):
        verifyClass(IBibliographyExport, utility.EndnoteExport)

    def test_risexport(self):
        verifyClass(IBibliographyExport, utility.RisExport)
    
    def test_xmlexport(self):
        verifyClass(IBibliographyExport, utility.XmlExport)

    def test_pdfexport(self):
        verifyClass(IBibliographyExport, utility.XmlExport)

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(ViewInterfaceTestCase),
        unittest.makeSuite(UtilityInterfaceTestCase),
        ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
