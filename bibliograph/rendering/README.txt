bibliograph.rendering Package Readme
====================================

Overview
--------

Render bibliographic information from plone content.


Transforms
----------

Only the bibtex bibliography is rendered from the scratch. pdf is rendered
with pdflatex[2]_. All other formats (EndNote, XML, RIS, ...) are transformed
using external tools from bibutils[1]_.  At the time of writing I used
version 3.38 of the tools. See the following table for a list of dependencies:

+--------+-------------------------+
| Format | Dependency              |
+--------+-------------------------+
| bibtex | none (builtin)          |
+--------+-------------------------+
| pdf    | latex, bibtex, pdflatex |
+--------+-------------------------+
| others | bibutils                |
+--------+-------------------------+


.. [1] http://bibutils.refbase.org/
.. [2] http://www.latex-project.org/
