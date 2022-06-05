================================================================================
pyexcel-ods - Let you focus on data, instead of ods format
================================================================================

.. image:: https://raw.githubusercontent.com/pyexcel/pyexcel.github.io/master/images/patreon.png
   :target: https://www.patreon.com/pyexcel

.. image:: https://api.bountysource.com/badge/team?team_id=288537
   :target: https://salt.bountysource.com/teams/chfw-pyexcel

.. image:: https://travis-ci.org/pyexcel/pyexcel-ods.svg?branch=master
   :target: http://travis-ci.org/pyexcel/pyexcel-ods

.. image:: https://codecov.io/gh/pyexcel/pyexcel-ods/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/pyexcel/pyexcel-ods

.. image:: https://img.shields.io/gitter/room/gitterHQ/gitter.svg
   :target: https://gitter.im/pyexcel/Lobby


**pyexcel-ods** is a tiny wrapper library to read, manipulate and write data in
ods format using python 2.6 and python 2.7. You are likely to use it with
`pyexcel <https://github.com/pyexcel/pyexcel>`_.
`pyexcel-ods3 <https://github.com/pyexcel/pyexcel-ods3>`_ is a sister library that
depends on ezodf and lxml. `pyexcel-odsr <https://github.com/pyexcel/pyexcel-odsr>`_
is the other sister library that has no external dependency but do ods reading only

Known constraints
==================

Fonts, colors and charts are not supported.

Installation
================================================================================


You can install pyexcel-ods via pip:

.. code-block:: bash

    $ pip install pyexcel-ods


or clone it and install it:

.. code-block:: bash

    $ git clone https://github.com/pyexcel/pyexcel-ods.git
    $ cd pyexcel-ods
    $ python setup.py install

Support the project
================================================================================

If your company has embedded pyexcel and its components into a revenue generating
product, please support me on `patreon <https://www.patreon.com/bePatron?u=5537627>`_
or `bounty source <https://salt.bountysource.com/teams/chfw-pyexcel>`_ to maintain
the project and develop it further.

If you are an individual, you are welcome to support me too and for however long
you feel like. As my backer, you will receive
`early access to pyexcel related contents <https://www.patreon.com/pyexcel/posts>`_.

And your issues will get prioritized if you would like to become my patreon as `pyexcel pro user`.

With your financial support, I will be able to invest
a little bit more time in coding, documentation and writing interesting posts.


Usage
================================================================================

As a standalone library
--------------------------------------------------------------------------------

Write to an ods file
********************************************************************************



Here's the sample code to write a dictionary to an ods file:

.. code-block:: python

    >>> from pyexcel_ods import save_data
    >>> data = OrderedDict() # from collections import OrderedDict
    >>> data.update({"Sheet 1": [[1, 2, 3], [4, 5, 6]]})
    >>> data.update({"Sheet 2": [["row 1", "row 2", "row 3"]]})
    >>> save_data("your_file.ods", data)


Read from an ods file
********************************************************************************

Here's the sample code:

.. code-block:: python

    >>> from pyexcel_ods import get_data
    >>> data = get_data("your_file.ods")
    >>> import json
    >>> print(json.dumps(data))
    {"Sheet 1": [[1, 2, 3], [4, 5, 6]], "Sheet 2": [["row 1", "row 2", "row 3"]]}


Write an ods to memory
********************************************************************************

Here's the sample code to write a dictionary to an ods file:

.. code-block:: python

    >>> from pyexcel_ods import save_data
    >>> data = OrderedDict()
    >>> data.update({"Sheet 1": [[1, 2, 3], [4, 5, 6]]})
    >>> data.update({"Sheet 2": [[7, 8, 9], [10, 11, 12]]})
    >>> io = StringIO()
    >>> save_data(io, data)
    >>> # do something with the io
    >>> # In reality, you might give it to your http response
    >>> # object for downloading




Read from an ods from memory
********************************************************************************

Continue from previous example:

.. code-block:: python

    >>> # This is just an illustration
    >>> # In reality, you might deal with ods file upload
    >>> # where you will read from requests.FILES['YOUR_ODS_FILE']
    >>> data = get_data(io)
    >>> print(json.dumps(data))
    {"Sheet 1": [[1, 2, 3], [4, 5, 6]], "Sheet 2": [[7, 8, 9], [10, 11, 12]]}


Pagination feature
********************************************************************************

Special notice 30/01/2017: due to the constraints of the underlying 3rd party
library, it will read the whole file before returning the paginated data. So
at the end of day, the only benefit is less data returned from the reading
function. No major performance improvement will be seen.

With that said, please install `pyexcel-odsr <https://github.com/pyexcel/pyexcel-odsr>`_
and it gives better performance in pagination.

Let's assume the following file is a huge ods file:

.. code-block:: python

   >>> huge_data = [
   ...     [1, 21, 31],
   ...     [2, 22, 32],
   ...     [3, 23, 33],
   ...     [4, 24, 34],
   ...     [5, 25, 35],
   ...     [6, 26, 36]
   ... ]
   >>> sheetx = {
   ...     "huge": huge_data
   ... }
   >>> save_data("huge_file.ods", sheetx)

And let's pretend to read partial data:

.. code-block:: python

   >>> partial_data = get_data("huge_file.ods", start_row=2, row_limit=3)
   >>> print(json.dumps(partial_data))
   {"huge": [[3, 23, 33], [4, 24, 34], [5, 25, 35]]}

And you could as well do the same for columns:

.. code-block:: python

   >>> partial_data = get_data("huge_file.ods", start_column=1, column_limit=2)
   >>> print(json.dumps(partial_data))
   {"huge": [[21, 31], [22, 32], [23, 33], [24, 34], [25, 35], [26, 36]]}

Obvious, you could do both at the same time:

.. code-block:: python

   >>> partial_data = get_data("huge_file.ods",
   ...     start_row=2, row_limit=3,
   ...     start_column=1, column_limit=2)
   >>> print(json.dumps(partial_data))
   {"huge": [[23, 33], [24, 34], [25, 35]]}

As a pyexcel plugin
--------------------------------------------------------------------------------

No longer, explicit import is needed since pyexcel version 0.2.2. Instead,
this library is auto-loaded. So if you want to read data in ods format,
installing it is enough.


Reading from an ods file
********************************************************************************

Here is the sample code:

.. code-block:: python

    >>> import pyexcel as pe
    >>> sheet = pe.get_book(file_name="your_file.ods")
    >>> sheet
    Sheet 1:
    +---+---+---+
    | 1 | 2 | 3 |
    +---+---+---+
    | 4 | 5 | 6 |
    +---+---+---+
    Sheet 2:
    +-------+-------+-------+
    | row 1 | row 2 | row 3 |
    +-------+-------+-------+


Writing to an ods file
********************************************************************************

Here is the sample code:

.. code-block:: python

    >>> sheet.save_as("another_file.ods")


Reading from a IO instance
********************************************************************************

You got to wrap the binary content with stream to get ods working:

.. code-block:: python

    >>> # This is just an illustration
    >>> # In reality, you might deal with ods file upload
    >>> # where you will read from requests.FILES['YOUR_ODS_FILE']
    >>> odsfile = "another_file.ods"
    >>> with open(odsfile, "rb") as f:
    ...     content = f.read()
    ...     r = pe.get_book(file_type="ods", file_content=content)
    ...     print(r)
    ...
    Sheet 1:
    +---+---+---+
    | 1 | 2 | 3 |
    +---+---+---+
    | 4 | 5 | 6 |
    +---+---+---+
    Sheet 2:
    +-------+-------+-------+
    | row 1 | row 2 | row 3 |
    +-------+-------+-------+


Writing to a StringIO instance
********************************************************************************

You need to pass a StringIO instance to Writer:

.. code-block:: python

    >>> data = [
    ...     [1, 2, 3],
    ...     [4, 5, 6]
    ... ]
    >>> io = StringIO()
    >>> sheet = pe.Sheet(data)
    >>> io = sheet.save_to_memory("ods", io)
    >>> # then do something with io
    >>> # In reality, you might give it to your http response
    >>> # object for downloading


License
================================================================================

New BSD License

Developer guide
==================

Development steps for code changes

#. git clone https://github.com/pyexcel/pyexcel-ods.git
#. cd pyexcel-ods

Upgrade your setup tools and pip. They are needed for development and testing only:

#. pip install --upgrade setuptools pip

Then install relevant development requirements:

#. pip install -r rnd_requirements.txt # if such a file exists
#. pip install -r requirements.txt
#. pip install -r tests/requirements.txt

Once you have finished your changes, please provide test case(s), relevant documentation
and update CHANGELOG.rst.

.. note::

    As to rnd_requirements.txt, usually, it is created when a dependent
    library is not released. Once the dependecy is installed
    (will be released), the future
    version of the dependency in the requirements.txt will be valid.


How to test your contribution
------------------------------

Although `nose` and `doctest` are both used in code testing, it is adviable that unit tests are put in tests. `doctest` is incorporated only to make sure the code examples in documentation remain valid across different development releases.

On Linux/Unix systems, please launch your tests like this::

    $ make

On Windows systems, please issue this command::

    > test.bat

How to update test environment and update documentation
---------------------------------------------------------

Additional steps are required:

#. pip install moban
#. git clone https://github.com/moremoban/setupmobans.git # generic setup
#. git clone https://github.com/pyexcel/pyexcel-commons.git commons
#. make your changes in `.moban.d` directory, then issue command `moban`

What is pyexcel-commons
---------------------------------

Many information that are shared across pyexcel projects, such as: this developer guide, license info, etc. are stored in `pyexcel-commons` project.

What is .moban.d
---------------------------------

`.moban.d` stores the specific meta data for the library.

Acceptance criteria
-------------------

#. Has Test cases written
#. Has all code lines tested
#. Passes all Travis CI builds
#. Has fair amount of documentation if your change is complex
#. Please update CHANGELOG.rst
#. Please add yourself to CONTRIBUTORS.rst
#. Agree on NEW BSD License for your contribution

Credits
================================================================================

ODSReader is originally written by `Marco Conti <https://github.com/marcoconti83/read-ods-with-odfpy>`_


Change log
================================================================================

0.5.3 - unreleased
--------------------------------------------------------------------------------

added
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. `#24 <https://github.com/pyexcel/pyexcel-ods/issues/24>`_, ignore
   comments(<office:comment>) in cell
#. `#27 <https://github.com/pyexcel/pyexcel-ods/issues/27>`_, exception raised
   when currency type is missing
#. fix odfpy version on 1.3.5.

0.5.2 - 23.10.2017
--------------------------------------------------------------------------------

updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. pyexcel `pyexcel#105 <https://github.com/pyexcel/pyexcel/issues/105>`_,
   remove gease from setup_requires, introduced by 0.5.1.
#. remove python2.6 test support

0.5.1 - 20.10.2017
--------------------------------------------------------------------------------

added
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. `pyexcel#103 <https://github.com/pyexcel/pyexcel/issues/103>`_, include
   LICENSE file in MANIFEST.in, meaning LICENSE file will appear in the released
   tar ball.

0.5.0 - 30.08.2017
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. put dependency on pyexcel-io 0.5.0, which uses cStringIO instead of StringIO.
   Hence, there will be performance boost in handling files in memory.

Relocated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. All ods type conversion code lives in pyexcel_io.service module

0.4.1 - 25.08.2017
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. `pyexcel#23 <https://github.com/pyexcel/pyexcel/issues/23>`_, handle
   unseekable stream given by http response
#. PR `#22 <https://github.com/pyexcel/pyexcel-ods/pull/22>`_, hanle white
   spaces in a cell.

0.4.0 - 19.06.2017
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. `pyexcel#14 <https://github.com/pyexcel/pyexcel/issues/14>`_, close file
   handle
#. pyexcel-io plugin interface now updated to use `lml
   <https://github.com/chfw/lml>`_.

0.3.3 - 07.05.2017
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. issue `pyexcel#19 <https://github.com/pyexcel/pyexcel/issues/19>`_, not all
   texts in a multi-node cell were extracted.

0.3.2 - 13.04.2017
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. issue `pyexcel#17 <https://github.com/pyexcel/pyexcel/issues/17>`_, empty new
   line is ignored
#. issue `pyexcel#6 <https://github.com/pyexcel/pyexcel/issues/6>`_,
   PT288H00M00S is valid duration

0.3.1 - 02.02.2017
--------------------------------------------------------------------------------

Added
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Recognize currency type

0.3.0 - 22.12.2016
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Code refactoring with pyexcel-io v 0.3.0

0.2.2 - 24.10.2016
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. issue `pyexcel#14 <https://github.com/pyexcel/pyexcel/issues/14>`_, index
   error when reading a ods file that has non-uniform columns repeated property.

0.2.1 - 31.08.2016
--------------------------------------------------------------------------------

Added
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. support pagination. two pairs: start_row, row_limit and start_column,
   column_limit help you deal with large files.
#. use odfpy 1.3.3 as compulsory package. offically support python 3

0.2.0 - 01.06.2016
--------------------------------------------------------------------------------

Added
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. By default, `float` will be converted to `int` where fits. `auto_detect_int`,
   a flag to switch off the autoatic conversion from `float` to `int`.
#. 'library=pyexcel-ods' was added so as to inform pyexcel to use it instead of
   other libraries, in the situation where multiple plugins were installed.

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. support the auto-import feature of pyexcel-io 0.2.0

0.1.1 - 30.01.2016
--------------------------------------------------------------------------------

Added
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 'streaming' is an extra option given to get_data. Only when 'streaming' is
   explicitly set to True, the data will be consisted of generators, hence will
   break your existing code.
#. uses yield in to_array and returns a generator
#. support multi-line text cell #5
#. feature migration from pyexcel-ods3 pyexcel/pyexcel-ods3#5

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. compatibility with pyexcel-io 0.1.1

0.0.12 - 10.10.2015
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Bug fix: excessive trailing columns with empty values

0.0.11 - 26.09.2015
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Complete fix for libreoffice datetime field

0.0.10 - 15.09.2015
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Bug fix: date field could have datetime from libreoffice

0.0.9 - 21.08.2015
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Bug fix: utf-8 string throw unicode exceptions

0.0.8 - 28.06.2015
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Pin dependency odfpy 0.9.6 to avoid buggy odfpy 1.3.0

0.0.7 - 28.05.2015
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Bug fix: "number-columns-repeated" is now respected

0.0.6 - 21.05.2015
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. get_data and save_data are seen across pyexcel-* extensions. remember them
   once and use them across all extensions.

0.0.5 - 22.02.2015
--------------------------------------------------------------------------------

Added
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Loads only one sheet from a multiple sheet book
#. Use New BSD License

0.0.4 - 14.12.2014
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. IO interface update as pyexcel-io introduced keywords.
#. initial release

0.0.3 - 08.12.2014
--------------------------------------------------------------------------------

Updated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. IO interface update as pyexcel-io introduced keywords.
#. initial release



