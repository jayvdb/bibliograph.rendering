# -*- coding: utf-8 -*-
###############################################################################
# $Copy$
###############################################################################
""" PDF render view

$Id$
"""
__docformat__ = 'reStructuredText'
__author__  = 'Tom Gross <itconsense@gmail.com>'

# python imports
import logging
import tempfile
import os
import shutil

# zope2 imports

# zope3 imports
from zope.interface import implements
from zope import component
from zope.traversing.browser.absoluteurl import absoluteURL

# plone imports

# third party imports

# own factory imports
from bibliograph.core import utils
from bibliograph.rendering.interfaces import IBibliographyRenderer

###############################################################################

log = logging.getLogger('bibliograph.rendering')

###############################################################################

DEFAULT_TEMPLATE = r"""
\documentclass[english,12pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[latin9]{inputenc}
\usepackage{bibmods}
\usepackage{bibnames}
\usepackage{showtags}
\renewcommand{\refname}{~}


\begin{document}
\begin{center}
{\large \bf %(title)s}\\
(URL: %(url)s)
\end{center}


~\hfill \today


\nocite{*}
\bibliographystyle{abbrv}
\bibliography{references}


\end{document}
"""

###############################################################################

def getWorkingDirectory():
    """
    returns the full path to a newly created
    temporary working directory
    """
    tmp_dir = tempfile.mkdtemp()
    renderer_dir = '/'.join(os.path.split(__file__)[:-1])
    resource_dir = os.path.join(renderer_dir, 'latex_resources')
    for file in os.listdir(resource_dir):
        source = os.path.join(resource_dir, file)
        destination = os.path.join(tmp_dir, file)
        if os.path.isfile(source):
            shutil.copy(source, destination)
    return tmp_dir

###############################################################################

def clearWorkingDirectory(wd):
    """
    removes the temporary working directory
    """
    for file in os.listdir(wd):
        try:
            path = os.path.join(wd, file)
            os.remove(path)
        except OSError:
            pass
    os.rmdir(wd)


###############################################################################

class PdfRenderView(object):
    """ A view rendering a bibliography """

    implements(IBibliographyRenderer)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        resolve_unicode = self.request.get('resolve_unicode', False)
        title_force_uppercase = self.request.get('title_force_uppercase', False)
        msdos_eol_style = self.request.get('msdos_eol_style', False)
        output_encoding = self.request.get('output_encoding', 'utf-8')
        return self.render(resolve_unicode,
                           title_force_uppercase,
                           msdos_eol_style,
                           output_encoding)

    def render(self, resolve_unicode=False,
                     title_force_uppercase=False,
                     msdos_eol_style=False,
                     output_encoding=None
                     ):
        """
        renders a BibliographyEntry object in EndNote format
        """
        bibrender = component.queryMultiAdapter((self.context, self.request),
            name=u'bibliography.bib')
        source = bibrender.render(output_encoding='latin-1',
                                  title_force_uppercase=True)
        return self.processSource(source,
            title=utils.title_or_id(self.context),
            url=absoluteURL(self.context, self.request))

    def getTemplate(self, **kwargs):
        template = getattr(self.context, 'latextemplate', None)
        if template is None:
            values = {'title': 'Bibliographic Export',
                      'url': ''}
            for key, val in kwargs.items():
                values[key] = unicode(utils._normalize(val, True),
                         'utf-8').encode('latin-1')
            template = DEFAULT_TEMPLATE % values
        return template

    def processSource(self, source, **kwargs):
        """
        use latex/bibtex/pdflatex to generate the pdf
        from the passed in BibTeX file in 'source' using
        the (LaTeX) source tempalte from the renderer's
        'template' property
        """
        template = self.getTemplate(**kwargs)
        wd = getWorkingDirectory()
        tex_path = os.path.join(wd, 'template.tex')
        bib_path = os.path.join(wd, 'references.bib')
        tex_file = open(tex_path, 'w')
        bib_file = open(bib_path, 'w')
        tex_file.write(template)
        bib_file.write(source)
        tex_file.close()
        bib_file.close()
        os.system("cd %s; latex %s"% (wd, tex_path))
        os.system("cd %s; bibtex %s"% (wd, 'template'))
        os.system("cd %s; latex %s"% (wd, 'template.tex'))
        os.system("cd %s; pdflatex %s"% (wd, tex_path))
        pdf_file= open(os.path.join(wd, "template.pdf"), 'r')
        pdf = pdf_file.read()
        pdf_file.close()
        clearWorkingDirectory(wd)
        return pdf

# EOF
