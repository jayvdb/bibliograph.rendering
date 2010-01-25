import unittest
import codecs
from zope.interface import implements
from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.content import Author
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


AUTH1 = Author()
AUTH1.firstname = u'Heinz'
AUTH1.middlename = u''
AUTH1.lastname = u'M\xfcller'
#unicode('M\u00FCller', 'utf8')?
#u'\u00FC' 
AUTH1.isEditor = True


class SimpleContent(Contained, dict):

    implements(IBibliographicReference)

    __name__ = 'approach'

    def __init__(self):
        self.publication_type = u'Book'
        self.source_fields = []
        self.field_values = []
        self.title = u'A new approach to managing literat\xfcre'
        self.publication_year = 1985
        self.abstract = u'Lorem ipsum dolor sit amet, consectetuer adipiscing elit.'
        self.subject = [u'Manage Literat\xfcr']
        self.note = u''
        self.annote = u''
        self.url = u"http://www.books.com/approach"
        self.editors = [AUTH1]
        self.authors = []

    #def getFieldValue(self, name):
    #    return self[name]

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
