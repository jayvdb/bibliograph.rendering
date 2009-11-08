import unittest

from zope.publisher.browser import TestRequest

from bibliograph.rendering.tests import setup
from bibliograph.rendering.tests.base import BaseRendererTestCase
from bibliograph.rendering.renderers.endnote import EndnoteRenderView
from bibliograph.rendering.utility import EndnoteRenderer


class TestEndnoteRenderer(BaseRendererTestCase):
    """tests to cover the Endnote renderer"""

    def test_RenderView(self):
        """test the functioning of the renderer"""
        ref = self.getSimpleContent()
        renderer = EndnoteRenderView(ref, TestRequest())
        source1 = self.readFile(setup.SOURCE1_END).encode('utf-8').strip()
        out1 = renderer().strip()
        self.failUnless(source1 == out1)
        # First we want no editor, but an author:
        ref.editor_flag = False
        renderer = EndnoteRenderView(ref, TestRequest())
        source2 = self.readFile(setup.SOURCE2_END).encode('utf-8').strip()
        out2 = renderer().strip()
        self.failUnless(source2 == out2)
        request = TestRequest(form=dict(omit_fields=['authors', 'uRl', 'abSTRACT']))
        renderer = EndnoteRenderView(ref, request)
        source3 = self.readFile(setup.SOURCE3_END).encode('utf-8').strip()
        out3 = renderer().strip()
        self.failUnless(source3 == out3)

    def test_RenderUtility(self):
        """test the functioning of the utility renderer"""
        ref = self.getSimpleContent()
        renderer = EndnoteRenderer()
        source1 = self.readFile(setup.SOURCE1_END).strip()
        out1 = renderer.render([ref]).strip()
        self.failUnless(source1 == out1)
        # First we want no editor, but an author:
        ref.editor_flag = False
        source2 = self.readFile(setup.SOURCE2_END).strip()
        out2 = renderer.render([ref]).strip()
        self.failUnless(source2 == out2)
        source3 = self.readFile(setup.SOURCE3_END).strip()
        ofmapping = {u'Book' : ['authors', 'uRl', 'abSTRACT']}
        out3 = renderer.render([ref], omit_fields_mapping=ofmapping).strip()
        self.failUnless(source3 == out3)


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestEndnoteRenderer),])
    return suite