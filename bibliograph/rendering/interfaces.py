from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

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
    
    source_format = schema.TextLine()
    target_format = schema.TextLine()
    description = schema.Text()
    available_encodings = schema.List()
    default_encoding = schema.TextLine()

    available = schema.Bool()
    enabled = schema.Bool()
    
    def render(objects, output_encoding, title_force_uppercase, msdos_eol_style):
        """ """
# EOF
