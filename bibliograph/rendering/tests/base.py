import unittest
import codecs
from zope.interface import implements
from bibliograph.core.interfaces import IBibliographicReference
from zope.app.testing.placelesssetup import setUp
from zope.app.testing.placelesssetup import tearDown
from zope.app.testing import ztapi
from zope.component import testing
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.app.container.contained import Contained
from zope.interface import implements

from zope.publisher.browser import TestRequest
from bibliograph.rendering.renderers.endnote import XmlRenderView
from bibliograph.rendering.renderers.bibtex import BibtexRenderView
from bibliograph.rendering.interfaces import IBibTransformUtility

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

    title = u'A new approach to managing literat\xfcre'
    publication_year = 1985
    abstract = u'Lorem ipsum dolor sit amet, consectetuer adipiscing elit.'
    subject = [u'Manage Literat\xfcr']
    note = u''
    annote = u''
    url = u"http://www.books.com/approach"

    @property
    def authors(self):
        return self.getAuthors()()

    def getAuthors(self, **kwargs):
        return Names([Name(firstnames=u'Heinz',
                           lastnames=u'M\xfcller',
                           homepage=u'http://www.zope.org')])

    def getFieldValue(self, name):
        return self[name]

class AbsoluteURL(object):

    def __init__(self, context, request):
        pass

    def __call__(self):
        return "http://nohost/bibliography/unittest"


def customSetup(test=None):
    testing.setUp()
    from bibliograph.rendering.renderers.pdf import PdfRenderView
    from bibliograph.rendering.utility import ExternalTransformUtility
    ztapi.provideView(IBibliographicReference, None, None,
                      name=u'reference.bib',
                      factory=BibtexRenderView)
    ztapi.provideView(IBibliographicReference, None, None,
                      name=u'reference.pdf',
                      factory=PdfRenderView)

    ztapi.provideUtility(IBibTransformUtility, ExternalTransformUtility(),
                         name=u'external')
    ztapi.browserViewProviding(None, AbsoluteURL, IAbsoluteURL)


ENCODING = 'utf-8'

class BaseRendererTestCase(unittest.TestCase):

    def setUp(self):
        customSetup()

    def tearDown(self):
        tearDown()

    def readFile(self, path, encoding=ENCODING):
        out = codecs.open(path, 'r', ENCODING).read()
        out = out.lstrip( unicode( codecs.BOM_UTF8, "utf8" ) )
        out = out.replace('\r\n', '\n').replace('\r', '\n')
        return out

    def getSimpleContent(self):
        return SimpleContent()

    def getRenderer(self, ref):
        request = TestRequest()
        return self.rendererview(ref, request)
