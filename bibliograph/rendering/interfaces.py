from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from bibliograph.core.encodings import _python_encodings

# XXX as long as we don't have translation
_ = unicode

###############################################################################

class IBibTransformUtility(Interface):
    """ A utility to transform
        bibliographic entries from one format to another.
    """

    def __call__(data, source_format, target_format):
        """ do the transform of `data` from `source_format`
            to `target_format`
        """

###############################################################################

class IBibliographyRenderer(Interface):
    """ Interface for bibliographic output/export renderers
    """

    def __call__():
        """ Execute the renderer """

    def render(resolve_unicode,
               title_force_uppercase,
               msdos_eol_style,
               **kwargs):
        """ Returns the rendered object(s)
        object may be a bibliography folder, a single, or a list of
        bibliography entries
        """

###############################################################################

class IBibliographyExporter(Interface):
    """ A utility knowing how to export a bunch of
        bibliographies
    """
    
    source_format = schema.TextLine(
        title=_('Source format'),
        )
    
    target_format = schema.TextLine(
        title=_('Target format'),
        default=u'bib',
        )
    
    description = schema.Text(
        title=_('Description'),
        default=u'',
        )
 
    available_encodings = schema.List(
        title=_('Available encodings'),
        value_type=schema.TextLine(
            #vocabulary=SimpleVocabulary.fromValues(_python_encodings),
            )
        )
        
    default_encoding = schema.TextLine(
        title=_('Default encoding'),
        default=u''
        )

    available = schema.Bool(
        title=_('Availability of renderer'),
        default=True
        )
    
    enabled = schema.Bool(
        title=_('Renderer is enabled'),
        default=True
        )
    
    def render(objects, output_encoding, title_force_uppercase, msdos_eol_style):
        """ """
# EOF
