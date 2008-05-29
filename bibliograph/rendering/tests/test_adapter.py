# -*- coding: utf-8 -*-
import unittest

from zope.component import getUtility
from zope.interface import directlyProvides

from zope.app.container.sample import SampleContainer
from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import setUp, tearDown

from bibliograph.core.interfaces import IBibContainerIterator
from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.interfaces import IBibliographyExport
from bibliograph.rendering.adapter import Zope2FolderAdapter
from bibliograph.rendering.interfaces import IBibliographyExporter
from bibliograph.rendering.renderers.bibtex import BibtexRenderView
from bibliograph.rendering.tests.test_doctests import SimpleContent
from bibliograph.rendering.utility import BibtexExport

class FakeZopeContainer(SampleContainer):
    
    def objectValues(self):
        return self.values()

class AdapterTestCase(unittest.TestCase):

    def setUp(self):
        setUp()
        ztapi.provideUtility(IBibliographyExporter, BibtexExport(),
                         name=u'bibtex')
        ztapi.provideAdapter(IBibliographyExport,
                             IBibContainerIterator,
                             Zope2FolderAdapter,
                             )
        ztapi.provideView(IBibliographicReference, None, None,
                          name='bibliography.bib',
                          factory=BibtexRenderView)

        self.bib = FakeZopeContainer()
        self.bib['ref1'] = SimpleContent()
        self.bib['ref2'] = SimpleContent()
        directlyProvides(self.bib, IBibliographyExport)

    def tearDown(self):
        tearDown()

    def test_bibtexutility(self):
        utility = getUtility(IBibliographyExporter, name='bibtex')
        result = utility.render(self.bib).strip()
        self.failUnlessEqual(result.count('@Book'), 2)
        self.failUnless(result.endswith('}'))

    def test_z2folderadpater(self):
        bib = self.bib
        adapter = IBibContainerIterator(bib)
        self.assertEqual(list(adapter), [bib['ref1'], bib['ref2']])

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(AdapterTestCase),])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
