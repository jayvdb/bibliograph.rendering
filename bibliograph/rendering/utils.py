
import string
import re

from bibliograph.rendering.enc import _utf8enc2latex_mapping

_default_encoding = 'utf-8'

_entity_mapping = {'&mdash;':'{---}',
                   '&ndash;':'{--}',
                   }

###############################################################################
# a poor-mans approach to fixing unicode issues :-(

def _encode(s, encoding=_default_encoding):
    try:
        return s.encode(encoding)
    except (TypeError, UnicodeDecodeError, ValueError):
        return s

def _decode(s, encoding=_default_encoding):
    try:
        return unicode(s, encoding)
    except (TypeError, UnicodeDecodeError, ValueError):
        return s

###############################################################################

VALIDIDPAT = re.compile('[ "@\',\\#}{~%&$^]')

def _validKey(entry):
    """
    uses the Zope object id but
    removes characters not allowed in BibTeX keys

    >>> from bibliograph.rendering.utils import _validKey
    >>> _validKey(DummyEntry('Foo Bar'))
    'FooBar'

    >>> _validKey(DummyEntry('my@id'))
    'myid'

    """

    # be forward compatible to zope3 contained objects
    raw_id = getattr(entry, '__name__', '')
    if not raw_id:
        raw_id = entry.getId()

    # This substitution is based on the description of cite key restrictions at
    # http://bibdesk.sourceforge.net/manual/BibDesk%20Help_2.html
    return VALIDIDPAT.sub('', raw_id)

###############################################################################

def AuthorURLs(entry):
    """a string with all the known author's URLs;
    helper method for bibtex output"""
    a_URLs = ''
    for a in entry.Authors():
        url = a.get('homepage', ' ')
        a_URLs += "%s and " % url
    return a_URLs[:-5]

###############################################################################

def _braceUppercase(text):
    """ """
    for uc in string.uppercase:
        text = text.replace(uc, r'{%s}' % uc)
    return text

###############################################################################

def _normalize(text, resolve_unicode=True):
    text.replace('\\', '\\\\')
    text = _resolveEntities(text)
    if resolve_unicode:
        text = _resolveUnicode(text)
    return _escapeSpecialCharacters(text)

###############################################################################

def _resolveEntities(text):
    for entity in _entity_mapping.keys():
        text = text.replace(entity, _entity_mapping[entity])
    return text

###############################################################################

def _resolveUnicode(text):
    for unichar in _utf8enc2latex_mapping.keys():
        text = _encode(_decode(text).replace(unichar,
                                             _utf8enc2latex_mapping[unichar]))
    return _encode(_decode(text).replace(r'$}{$',''))

###############################################################################

def _escapeSpecialCharacters(text):
    """
    latex escaping some (not all) special characters
    """
    text.replace('\\', '\\\\')
    escape = ['~', '#', '&', '%', '_']
    for c in escape:
        text = text.replace(c, '\\' + c )
    return text


###############################################################################

def title_or_id(context):
    """ Return the title or id.

        Works with Zope2 and Zope3
    """
    title = getattr(context, 'title', '')
    if not title:
        if hasattr(context, '__name__'):
            title = getattr(context, '__name__', '')
        elif hasattr(context, 'getId'):
            title = context.getId()
    return title

###############################################################################

def _convertToOutputEncoding(export_text,
                             input_encoding=None,
                             output_encoding='utf-8'):
    """ Convert the renderer's result to the output encoding
    """
    if input_encoding:
        return _encode(_decode(export_text, input_encoding), output_encoding)
    return _encode(_decode(export_text), output_encoding)

# EOF
