bibliograph.rendering
=====================

Package contains renderers for different bibliographic formats. It uses an
adapter to extract data from Zope/Plone-objects and provides utilities to call
the renderers. Currently supported formats are: bibtex, endnote, pdf, xml
(mods), and ris.


Transforms
----------

Only the bibtex bibliography is rendered from scratch. pdf is rendered with
pdflatex_. All other formats (EndNote, XML, RIS, ...) are transformed using
external tools from bibutils_. At the time of writing I used version 3.38
of the tools. See the following table for a list of dependencies:

+--------+-------------------------+
| Format | Dependency              |
+========+=========================+
| bibtex | none (builtin)          |
+--------+-------------------------+
| pdf    | latex, bibtex, pdflatex |
+--------+-------------------------+
| others | bibutils                |
+--------+-------------------------+


.. _bibutils:: http://bibutils.refbase.org/
.. _pdflatex:: http://www.latex-project.org/


Resources
---------

- Homepage: http://pypi.python.org/pypi/bibliograph.rendering
- Code repository: https://github.com/collective/bibliograph.rendering/
