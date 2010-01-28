from zope.interface import Interface
from zope import schema

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

class IReferenceRenderer(Interface):
    """Renders an IBibliographicReference to some designated output format.
    """

    def __call__():
        """Execute the renderer.
        """

    def render(resolve_unicode,
               title_force_uppercase,
               msdos_eol_style,
               output_encoding,
               omit_fields=[]):
        """Returns the rendered object(s) object may be a bibliography folder,
        a single, or a list of bibliography entries. Field names supplied in
        the `omit_fields' argument are not rendered.
        """

###############################################################################

class IBibliographyRenderer(Interface):
    """Renders a sequence of IBibliographicReference objects, or an
    IBibliography, to some designated output format.
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

    available = schema.Bool(
        title=_('Availability of renderer'),
        default=True
        )

    enabled = schema.Bool(
        title=_('Renderer is enabled'),
        default=True
        )

    def render(objects,
               output_encoding,
               title_force_uppercase,
               msdos_eol_style,
               omit_fields_mapping={}):
        """Export `objects' to the target_format. `omit_fields_mapping' is a
        dictionary with keys for publication_type names and values as lists of
        fields to omit when rendering those types, where field names or not
        case-sensitive. E.g.:
          {u"Book" : ['editor','note']}
        """
# EOF
