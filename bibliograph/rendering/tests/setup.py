from os.path import join

# This is so we can find our sample test files
from bibliograph.rendering.tests import GLOBALS
from Globals import package_home

PACKAGE_HOME = package_home(GLOBALS)

SOURCE1_XML = join(PACKAGE_HOME, 'samples', 'source1.xml')
SOURCE2_XML = join(PACKAGE_HOME, 'samples', 'source2.xml')
SOURCE3_XML = join(PACKAGE_HOME, 'samples', 'source3.xml')

SOURCE1_RIS = join(PACKAGE_HOME, 'samples', 'source1.ris')
SOURCE2_RIS = join(PACKAGE_HOME, 'samples', 'source2.ris')
SOURCE3_RIS = join(PACKAGE_HOME, 'samples', 'source3.ris')

SOURCE1_END = join(PACKAGE_HOME, 'samples', 'source1.end')
SOURCE2_END = join(PACKAGE_HOME, 'samples', 'source2.end')
SOURCE3_END = join(PACKAGE_HOME, 'samples', 'source3.end')

SOURCE1_BIB = join(PACKAGE_HOME, 'samples', 'source1.bib')
SOURCE2_BIB = join(PACKAGE_HOME, 'samples', 'source2.bib')
SOURCE3_BIB = join(PACKAGE_HOME, 'samples', 'source3.bib')
