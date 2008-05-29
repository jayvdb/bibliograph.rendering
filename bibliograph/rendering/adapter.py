""" Adapters used for rendering bibliographic content
    =================================================

    The iteration adapter
    ---------------------

    The iteration adapter is used to provide a common api for accessing
    containers of bibliographic content. Basically it defines an iterator
    with two hooks: prehook, posthook

    The prehook is called **before** a contained item is adapted to
    IBibliographicReference. The call of posthook is the last action done
    when iterating the container.

    Both hooks may be none. Let's see if they work

    Add some structure first
    >>> from zope.app.container.sample import SampleContainer
    >>> bib = SampleContainer()

    >>> from bibliograph.rendering.tests.test_doctests import SimpleContent
    >>> bib['ref1'] = SimpleContent()

    Prepare components
    >>> from zope.interface import directlyProvides
    >>> from bibliograph.core.interfaces import IBibliographyExport
    >>> directlyProvides(bib, IBibliographyExport)

    Call renderer
    >>> from zope.component import getUtility
    >>> from bibliograph.rendering.interfaces import IBibliographyExporter
    >>> util = getUtility(IBibliographyExporter, name='bibtex')
    >>> print util.render(bib)
    prehook called!
    posthook called!
    <BLANKLINE>
    @Book...

"""

from zope.interface import implements
from bibliograph.core.interfaces import IBibContainerIterator

class Zope2FolderAdapter(object):
    """ The simplest possible Zope2 IBibContainerIterator-adapter.

        It iterates over the folders objectValues.
    """

    implements(IBibContainerIterator)

    prehook = None
    posthook = None

    def __init__(self, context):
        self.context = context

    def __iter__(self):
        return iter(self.context.objectValues())
