# -*- coding: utf-8 -*-
import unittest, doctest

from zope.app.testing import ztapi
from zope.component import testing
from zope.testing import doctestunit
from zope.traversing.browser.interfaces import IAbsoluteURL

from zope.app.container.contained import Contained
from zope.interface import implements

from bibliograph.core.interfaces import IBibContainerIterator
from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.interfaces import IBibliographyExport
from bibliograph.rendering.adapter import Zope2FolderAdapter
from bibliograph.rendering.interfaces import IBibTransformUtility
from bibliograph.rendering.interfaces import IBibliographyExporter
from bibliograph.rendering.renderers.bibtex import BibtexRenderView
from bibliograph.rendering.utility import BibtexExport
from bibliograph.rendering.utility import _hasCommands
from bibliograph.rendering.utility import commands

class Name(dict):

    def __call__(self):
        return ' '.join([self['firstnames'], self['lastnames']])

class Names(list):

    def __call__(self):
        return u', '.join([a() for a in self])

class SimpleContent(Contained, dict):

    implements(IBibliographicReference)

    publication_type = u'Book'
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

class AbsoluteURL(object):

    def __init__(self, context, request):
        pass

    def __call__(self):
        return "http://nohost/bibliography/unittest"

def setUp(test=None):
    testing.setUp()
    from bibliograph.rendering.renderers.pdf import PdfRenderView
    from bibliograph.rendering.utility import ExternalTransformUtility
    ztapi.provideView(IBibliographicReference, None, None,
                      name='bibliography.bib',
                      factory=BibtexRenderView)
    ztapi.provideView(IBibliographicReference, None, None,
                      name='bibliography.pdf',
                      factory=PdfRenderView)

    ztapi.provideUtility(IBibTransformUtility, ExternalTransformUtility(),
                         name=u'external')
    ztapi.browserViewProviding(None, AbsoluteURL, IAbsoluteURL)


class SampleAdapter(Zope2FolderAdapter):

    def prehook(self, entry):
        print "prehook called!"
        return entry

    def posthook(self, entry):
        print "posthook called!"

    def __iter__(self):
        return iter(self.context.values())

def setUpAdapter(test=None):
    testing.setUp()
    ztapi.provideUtility(IBibliographyExporter, BibtexExport(),
                         name=u'bibtex')
    ztapi.provideAdapter(IBibliographyExport,
                         IBibContainerIterator,
                         SampleAdapter)
    ztapi.provideView(IBibliographicReference, None, None,
                      name='bibliography.bib',
                      factory=BibtexRenderView)

NOBIBUTILSMSG = """One or more transformationtool was not found!
please make sure bibutils is installed to run all tests. """

NOLATEXMSG = """One of latex, bibtex, pdflatex was not found!
please make sure these are installed to run all tests. """


def test_suite():
    utilsavailable = True
    latexavailable = True
    
    suite = unittest.TestSuite()
    suite.addTest(
        doctestunit.DocFileSuite(
            'renderers/bibtex.txt',
            'renderers/utility.txt',
            package='bibliograph.rendering',
            setUp=setUp,
            tearDown=testing.tearDown,
            globs=dict(SimpleContent=SimpleContent),
            optionflags=doctest.ELLIPSIS,
            ))

    suite.addTest(doctestunit.DocTestSuite(
            module='bibliograph.rendering.utility',
            setUp=testing.setUp,
            tearDown=testing.tearDown,
            optionflags=doctest.ELLIPSIS,
            ))

    suite.addTest(doctestunit.DocTestSuite(
            module='bibliograph.rendering.adapter',
            setUp=setUpAdapter,
            tearDown=testing.tearDown,
            optionflags=doctest.ELLIPSIS,
            ))

    if _hasCommands(commands.get('bib2end')):

        suite.addTest(doctestunit.DocFileSuite(
            'renderers/endnote.txt',
            package='bibliograph.rendering',
            setUp=setUp,
            tearDown=testing.tearDown,
            globs=dict(SimpleContent=SimpleContent),
            optionflags=doctest.ELLIPSIS,
            ))

    else:
        utilsavailable = False

    if _hasCommands(commands.get('bib2ris')):
        suite.addTest(doctestunit.DocFileSuite(
            'renderers/ris.txt',
            package='bibliograph.rendering',
            setUp=setUp,
            tearDown=testing.tearDown,
            globs=dict(SimpleContent=SimpleContent),
            optionflags=doctest.ELLIPSIS,
            ))
    else:
        utilsavailable = False
        
    if _hasCommands(commands.get('bib2xml')):
        suite.addTest(doctestunit.DocFileSuite(
            'renderers/xml.txt',
            package='bibliograph.rendering',
            setUp=setUp,
            tearDown=testing.tearDown,
            globs=dict(SimpleContent=SimpleContent),
            optionflags=doctest.ELLIPSIS,
            ))
    else:
        utilsavailable = False

    if _hasCommands('latex|bibtex|pdflatex'):
        suite.addTest(doctestunit.DocFileSuite(
            'renderers/pdf.txt',
            package='bibliograph.rendering',
            setUp=setUp,
            tearDown=testing.tearDown,
            globs=dict(SimpleContent=SimpleContent),
            optionflags=doctest.ELLIPSIS,
            ))
    else:
        latexavailable = False

    if utilsavailable:
        suite.addTest(doctestunit.DocFileSuite(
            'renderers/bibutility.txt',
            package='bibliograph.rendering',
            setUp=setUp,
            tearDown=testing.tearDown,
            globs=dict(SimpleContent=SimpleContent),
            optionflags=doctest.ELLIPSIS,
            ))

    if not utilsavailable:
        print NOBIBUTILSMSG
        print "-" * 20
        
    if not latexavailable:
        print NOLATEXMSG
        print "-" * 20

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
