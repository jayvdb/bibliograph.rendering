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
import codecs
from subprocess import Popen, PIPE

# zope imports
from zope.interface import implements
from zope import component
from zope.traversing.browser.absoluteurl import absoluteURL

# third party imports

# own factory imports
from bibliograph.core import utils
from bibliograph.rendering.interfaces import IReferenceRenderer
from base import BaseRenderer

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

LATEX_OPTS = "-interaction=nonstopmode"

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

class PdfRenderView(BaseRenderer):
    """ A view rendering a bibliography """

    implements(IReferenceRenderer)

    file_extension = 'pdf'

    def render(self, resolve_unicode=False,
                     title_force_uppercase=False,
                     msdos_eol_style=False,
                     output_encoding=None,
                     omit_fields=[],
                     ):
        """
        renders a BibliographyEntry object in PDF format
        """
        bibrender = component.queryMultiAdapter((self.context, self.request),
            name=u'reference.bib')
        source = bibrender.render(output_encoding='iso-8859-15',
                                  title_force_uppercase=True,
                                  omit_fields=omit_fields)
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
                         'utf-8').encode('iso-8859-15')
            template = DEFAULT_TEMPLATE % values
        return template

    def processSource(self, source, **kwargs):
        """
        use latex/bibtex/pdflatex to generate the pdf
        from the passed in BibTeX file in 'source' using
        the (LaTeX) source tempalte from the renderer's
        'template' property
        """

        template = kwargs.pop('template', None)
        if template is None:
            template = self.getTemplate(**kwargs)
        wd = getWorkingDirectory()
        tex_path = os.path.join(wd, 'template.tex')
        bib_path = os.path.join(wd, 'references.bib')
        tex_file = file(tex_path, 'w')
        # 'source' is a unicode string which should contain non-ascii
        # characters escaped (TeX notation). However the encoding.py module
        # only provides a minimal mapping (unicode -> TeX notation) - especially
        # it lacks support for greek characters. This will lead to the situation
        # that the BibTeX source file contains non-asci chars..this will lead
        # to Unicode decoding errors on the storage layer. As a workaround we
        # use the codecs module and instruct it to replace non-convertable
        # characters. A better solution would be to generated a utf-8 encoding
        # TeX template.tex file supporting UTF-8 directly on the TeX level.
        # {ajung)

        # ensure that ascii is really ascii 
        source = unicode(source, 'ascii', 'ignore').encode('ascii')
        bib_file = codecs.open(bib_path, 'w', encoding='ascii', errors='ignore')
        tex_file.write(template)
        bib_file.write(source)
        tex_file.close()
        bib_file.close()

        latexlog = []

        cmd = "cd %s; latex %s %s" % (wd, LATEX_OPTS, tex_path)
        log.debug(cmd)
        p = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
        (child_stdout, child_stderr) = (p.stdout, p.stderr)
        sts = os.waitpid(p.pid, 0)
        latexlog.extend([child_stdout.read().strip(),
                         child_stderr.read().strip()])

        cmd = "cd %s; bibtex %s" % (wd, 'template')
        log.debug(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True) 
        (child_stdout, child_stderr) = (p.stdout, p.stderr)
        sts = os.waitpid(p.pid, 0)
        latexlog.extend([child_stdout.read().strip(),
                         child_stderr.read().strip()])

        cmd = "cd %s; latex %s %s" % (wd, LATEX_OPTS, 'template.tex')
        log.debug(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True) 
        (child_stdout, child_stderr) = (p.stdout, p.stderr)
        sts = os.waitpid(p.pid, 0)
        latexlog.extend([child_stdout.read().strip(),
                         child_stderr.read().strip()])

        cmd = "cd %s; pdflatex %s %s" % (wd, LATEX_OPTS, tex_path)
        log.debug(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        (child_stdout, child_stderr) = (p.stdout, p.stderr)
        sts = os.waitpid(p.pid, 0)
        latexlog.extend([child_stdout.read().strip(),
                         child_stderr.read().strip()])

        log.debug('\n'.join(latexlog))

        pdf_file= open(os.path.join(wd, "template.pdf"), 'r')
        pdf = pdf_file.read()
        pdf_file.close()
        clearWorkingDirectory(wd)
        return pdf

# EOF
