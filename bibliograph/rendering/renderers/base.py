from bibliograph.core.utils import _normalize

class BaseRenderer(object):
    """A base class for renderers.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        resolve_unicode = self.request.get('resolve_unicode', False)
        title_force_uppercase = self.request.get('title_force_uppercase', False)
        msdos_eol_style = self.request.get('msdos_eol_style', False)
        output_encoding = self.request.get('output_encoding', 'utf-8')
        omit_fields = self.request.get('omit_fields', [])
        response = self.request.response
        response.setHeader('Content-Type', 'application/octet-stream')
        filename = 'reference.%s' % self.file_extension
        response.setHeader('Content-Disposition',
                           'attachment; filename=%s' % filename)
        result = self.render(resolve_unicode=resolve_unicode,
                           title_force_uppercase=title_force_uppercase,
                           msdos_eol_style=msdos_eol_style,
                           output_encoding=output_encoding,
                           omit_fields=omit_fields)

        return result

    def _isRenderableField(self, field_name, omit):
        if field_name.lower() in omit:
            return False
        return True

