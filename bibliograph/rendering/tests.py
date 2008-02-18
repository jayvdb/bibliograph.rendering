# -*- coding: utf-8 -*-
import unittest, doctest

from zope.testing import doctestunit
from zope.component import testing
from zope.app.testing import ztapi
from zope.traversing.browser.interfaces import IAbsoluteURL

from zope.app.container.contained import Contained
from zope.interface import implements

from bibliograph.core.interfaces import IBibrenderable
from bibliograph.rendering.interfaces import IBibTransformUtility


class Name(dict):

    def __call__(self):
        return ' '.join([self['firstnames'], self['lastnames']])

class Names(list):

    def __call__(self):
        return u', '.join([a() for a in self])

class SimpleContent(Contained, dict):

    implements(IBibrenderable)

    publication_type = u'Book'
    editor_flag = True
    source_fields = None
    __name__ = 'approach'

    title = u'A new approach to managing literatüre'
    publication_year = 1985
    abstract = u'Lorem ipsum dolor sit amet, consectetuer adipiscing elit.'
    subject = [u'Manage Literatür']
    note = u''
    annote = u''

    def Authors(self, **kwargs):
        return Names([Name(firstnames=u'Heinz',
                           lastnames=u'Müller',
                           homepage=u'http://www.zope.org')])

    def getURL(self):
        return u"http://www.books.com/approach"

    def getFieldValue(self, name):
        return self[name]

class DummyEntry(object):

    def __init__(self, id=None):
        self.id = id

    def getId(self):
        return self.id


class AbsoluteURL(object):

    def __init__(self, context, request):
        pass

    def __call__(self):
        return "http://nohost/bibliography/unittest"

def setUp(test=None):
    testing.setUp()
    from bibliograph.rendering.renderers.bibtex import BibtexRenderView
    from bibliograph.rendering.renderers.pdf import PdfRenderView
    from bibliograph.rendering.utility import ExternalTransformUtility
    ztapi.provideView(IBibrenderable, None, None, name='bibliography.bib',
                      factory=BibtexRenderView)
    ztapi.provideView(IBibrenderable, None, None, name='bibliography.pdf',
                      factory=PdfRenderView)

    ztapi.provideUtility(IBibTransformUtility, ExternalTransformUtility,
                         name=u'external')
    ztapi.browserViewProviding(None, AbsoluteURL, IAbsoluteURL)

def test_suite():
    suite = unittest.TestSuite([

        # Unit tests for your API
        doctestunit.DocFileSuite(
            'renderers/pdf.txt',
            'renderers/endnote.txt',
            'renderers/bibtex.txt',
            'renderers/ris.txt',
            'renderers/xml.txt',
            'renderers/utility.txt',
            package='bibliograph.rendering',
            setUp=setUp,
            tearDown=testing.tearDown,
            globs=dict(SimpleContent=SimpleContent),
            optionflags=doctest.ELLIPSIS,
            ),

        doctestunit.DocTestSuite(
            module='bibliograph.rendering.utils',
            setUp=testing.setUp,
            tearDown=testing.tearDown,
            globs=dict(DummyEntry=DummyEntry)
            ),

        doctestunit.DocTestSuite(
            module='bibliograph.rendering.utility',
            setUp=testing.setUp,
            tearDown=testing.tearDown,
            optionflags=doctest.ELLIPSIS,
            ),

        ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
