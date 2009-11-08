import unittest

from zope.publisher.browser import TestRequest

from bibliograph.rendering.tests import setup
from bibliograph.rendering.tests.base import BaseRendererTestCase
from bibliograph.rendering.renderers.endnote import RisRenderView
from bibliograph.rendering.utility import RisRenderer


class TestRisRenderer(BaseRendererTestCase):
    """tests to cover the RIS renderer"""

    def test_Render(self):
        """test the functioning of the renderer"""
        ref = self.getSimpleContent()
        renderer = RisRenderView(ref, TestRequest())
        source1 = self.readFile(setup.SOURCE1_RIS).encode('utf8').strip()
        out1 = renderer().strip()
        self.failUnless(source1 == out1)
        # First we want no editor, but an author:
        ref.editor_flag = False
        renderer = RisRenderView(ref, TestRequest())
        source2 = self.readFile(setup.SOURCE2_RIS).encode('utf8').strip()
        out2 = renderer().strip()
        self.failUnless(source2 == out2)
        request = TestRequest(form=dict(omit_fields=['authors', 'uRl', 'abSTRACT']))
        renderer = RisRenderView(ref, request)
        source3 = self.readFile(setup.SOURCE3_RIS).encode('utf8').strip()
        out3 = renderer().strip()
        self.failUnless(source3 == out3)

    def test_RenderUtility(self):
        """test the functioning of the utility renderer"""
        ref = self.getSimpleContent()
        renderer = RisRenderer()
        source1 = self.readFile(setup.SOURCE1_RIS).strip()
        out1 = renderer.render([ref]).strip()
        self.failUnless(source1 == out1)
        # First we want no editor, but an author:
        ref.editor_flag = False
        source2 = self.readFile(setup.SOURCE2_RIS).strip()
        out2 = renderer.render([ref]).strip()
        self.failUnless(source2 == out2)
        source3 = self.readFile(setup.SOURCE3_RIS).strip()
        out3 = renderer.render([ref], omit_fields=['authors', 'uRl', 'abSTRACT']).strip()
        self.failUnless(source3 == out3)


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestRisRenderer),])
    return suite