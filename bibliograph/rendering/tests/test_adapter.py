# -*- coding: utf-8 -*-
import unittest

from zope.component import getUtility
from zope.app.testing import ztapi

from zope.interface import implements
from zope.interface import directlyProvides

from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.interfaces import IBibliographyExport
from bibliograph.core.interfaces import IBibContainerIterator
from bibliograph.rendering.interfaces import IBibliographyExporter
from bibliograph.rendering.utility import BibtexExport
from bibliograph.rendering.tests.test_doctests import Name, Names
from bibliograph.rendering.adapter import Zope2FolderAdapter
from bibliograph.rendering.renderers.bibtex import BibtexRenderView

from Testing import ZopeTestCase as ztc
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

class Z2SimpleContent(SimpleItem):
    """ """

    implements(IBibliographicReference)

    publication_type = u'Article'
    editor_flag = True
    source_fields = []
    field_values = []
    __name__ = 'approach'

    title = u'A new approach to managing literatüre'
    publication_year = 1985
    abstract = u'Lorem ipsum dolor sit amet, consectetuer adipiscing elit.'
    subject = [u'Manage Literatür']
    note = u''
    annote = u''
    url = u"http://www.books.com/approach"

    @property
    def authors(self):
        return self.getAuthors()()

    def getAuthors(self, **kwargs):
        return Names([Name(firstnames=u'Heinz',
                           lastnames=u'Müller',
                           homepage=u'http://www.zope.org')])

    def getFieldValue(self, name):
        return self[name]

class AdapterTestCase(ztc.ZopeTestCase):

    def afterSetUp(self):
        ztapi.provideUtility(IBibliographyExporter, BibtexExport(),
                         name=u'bibtex')
        ztapi.provideAdapter(IBibliographyExport,
                             IBibContainerIterator,
                             Zope2FolderAdapter,
                             )
        ztapi.provideView(IBibliographicReference, None, None,
                          name='bibliography.bib',
                          factory=BibtexRenderView)

        self.folder._setObject('bib', Folder('bib'))
        directlyProvides(self.folder.bib, IBibliographyExport)
        self.folder.bib._setObject('ref1', Z2SimpleContent('ref1'))
        self.folder.bib._setObject('ref2', Z2SimpleContent('ref2'))

    def test_bibtexutility(self):
        utility = getUtility(IBibliographyExporter, name='bibtex')
        result = utility.render(self.folder.bib).strip()
        self.failUnlessEqual(result.count('@Article'), 2)
        self.failUnless(result.endswith('}'))

    def test_z2folderadpater(self):
        bib = self.folder.bib
        adapter = IBibContainerIterator(bib)
        self.assertEqual(list(adapter), [bib.ref1, bib.ref2])

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(AdapterTestCase)
        ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
