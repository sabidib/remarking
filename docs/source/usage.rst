
Installation and Getting Started
================================

- Python: 3.8, 3.9
- Platforms: Linux, Windows, MacOS
- PyPI package name: `remarking <https://pypi.org/project/remarking/>`_


Remarking makes it easy to extract highlights from the ReMarkable cloud.


Install ``remarking``
-------------------------
1. Run the following in your command line:

.. code-block:: text

   pip install -U remarking

2. Check the version you have installed

.. code-block:: text

   remarking --version


Download your first highlights
------------------------------

Before you download your first highlights you will need to make sure you have actually annotated a document
on your reMarkable.

You can annotate a document by highlighting text on the ReMarkable using the highlight pen.

Once you have some highlighted text you can start extracting it.


.. note::

   Remarking requires a one-time authorization token from `<https://my.remarkable.com/device/connect/desktop>`_
   in order to access the documents on the reMarkable cloud.

   You will be prompted to enter the token if ``remarking`` is not able to authorize with the cloud.

   Remarking uses `rmapy <https://rmapy.readthedocs.io/en/latest/>`_ to authenticate and access documents on the cloud. ``rmapy`` stores a token in ``~/.rmapi`` so that you do not need to re-authenticate on each invocation of Remarking.



With a document highlighted, you can run ``remarking`` either on the document itself or the folder that contains the document.

Let's say the document is called ``Through the Looking Glass`` and it lives in the ``library`` folder:

.. code-block:: text

   > remarking run table library | jq
   Extractors: remarkable
   Collections: library
   Connecting to RM cloud
   Connected to RM cloud.
   Retrieving cloud metadata
   Downloading documents
   Downloading "Through the Looking Glass"
   Downloaded 1 documents.
   Running extractors on documents
   Running extractor "RemarkableHighlightExtractor" on "Through the Looking Glass"
   Ran extractors and found 1 highlights, 1 are new.
   {
     "documents": [
       {
         "id": "2b329909-332d-4c28-b6c1-d298227cc82c",
         "version": 5,
         "modified_client": 1626736734,
         "type": "DocumentType",
         "name": "Through the Looking Glass",
         "current_page": 11,
         "bookmarked": false,
         "parent": "d29d67f9-faff-429c-b800-b7815173dcb2"
       }
     ],
     "highlights": [
       {
         "hash": "14235eca5db4a758ad34ab483df737714d10e710a3e3277d726a64da",
         "document_id": "2b329909-332d-4c28-b6c1-d298227cc82c",
         "text": "Alice was sitting curled up in a corner of the great arm-chair",
         "page_number": 11,
         "extracted_at": 1626723209,
         "extraction_method": "RemarkableHighlightExtractor"
       }
     ]
   }


You could also have done:

.. code-block:: text

   > remarking run table "Through the Looking Glass"
   Extractors: remarkable
   Collections: library
   Connecting to RM cloud
   Connected to RM cloud.
   Retrieving cloud metadata
   Downloading documents
   Downloading "Through the Looking Glass"
   Downloaded 1 documents.
   Running extractors on documents
   Running extractor "RemarkableHighlightExtractor" on "Through the Looking Glass"
   highlight_text                                                    highlight_page_number  document_name
   --------------------------------------------------------------  -----------------------  -------------------------
   Alice was sitting curled up in a corner of the great arm-chair                       11  Through the Looking Glass

.. _structure_of_a_command:

The Structure of a Remarking Command
------------------------------------

All ``remarking`` commands follow a similar structure.

.. code-block:: text

   remarking <mode command> [mode options] <writer command> [options] args


Modes
*****

The first command is called the mode command. It is one of:

-  ``run``
-  ``persist``

.. _writer_command:

Writer Commands
***************

The second command specifies which the writer command to use. The built-in writer commands are:

-  ``json``
-  ``csv``
-  ``table``

Learn more about them below in :ref:`writer_commands_deep`.

The documentation section :ref:`writer_command_guide` explains how to add custom writer commands.

Run
---

The ``run`` mode will download all highlights for a given document or folder and output them all according to the
writer you have set.

.. code-block:: text

   > remarking run table "Through the Looking Glass"
   Extractors: remarkable
   Collections: library
   Connecting to RM cloud
   Connected to RM cloud.
   Retrieving cloud metadata
   Downloading documents
   Downloading "Through the Looking Glass"
   Downloaded 1 documents.
   Running extractors on documents
   Running extractor "RemarkableHighlightExtractor" on "Through the Looking Glass"
   highlight_text                                                    highlight_page_number  document_name
   --------------------------------------------------------------  -----------------------  -------------------------
   Alice was sitting curled up in a corner of the great arm-chair                       11  Through the Looking Glass


The ``run`` mode will always return the same highlights, it does not manage any state. 


The ``persist`` run mode, on the other hand, does manage state.


Persist
-------

Remarking shines when you want to keep track of highlights over time.

The ``persist`` mode makes that easy to do.

``persist`` uses the `sqlalchemy <https://www.sqlalchemy.org/>`_ ORM to map highlights and documents to any SQLAlchemy supported backing datastore.

SqlAlchemy defaults
*******************

By default, remarking will persist to a local sqlite3 database called ``remarking_database.sqlite3`` that is stored in the current working directory.

Providing an argument for `--sqlalchemy` allows you to use any database that sqlalchemy supports as a backing database.

SqlAlchemy dialects
*******************

Some examples of the `many listed dialects on the sqlalchemy website <https://docs.sqlalchemy.org/en/latest/dialects/index.html>`_:

- MySQL
- PostgreSQL
- SQLite

.. warning::

   You need to install the specific driver for database you would like to connect to.

   For example, to connect to a MySQL database, you need to make sure a mysql driver is accessible by
   sqlalchemy.

   On most systems you will need the ``mysqlclient`` binaries installed on your machine
   which can then allow you to install the required python package:

   .. code-block:: text

      pip install mysqlclient

   Please refer to the `sqlalchemy docs for more info <https://docs.sqlalchemy.org/en/14/core/engines.html>`_


An example of connecting to a MySQL database:

.. code-block:: text

   > remarking persist --sqlalchemy mysql+pymysql://user:pass@host/dbname?charset=utf8mb4 table library
   Extractors: remarkable
   Collections: library
   Connecting to RM cloud
   Connected to RM cloud.
   Retrieving cloud metadata
   Downloading documents
   Downloading "Through the Looking Glass"
   Downloaded 1 documents.
   Running extractors on documents
   Running extractor "RemarkableHighlightExtractor" on "Through the Looking Glass"
   Ran extractors and found 1 highlights, 1 are new.
   highlight_text                                                    highlight_page_number  document_name
   --------------------------------------------------------------  -----------------------  -------------------------
   Alice was sitting curled up in a corner of the great arm-chair                       11  Through the Looking Glass


Querying the database will show a ``documents`` and ``highlights`` table that can be queried and futher used.

Another execution of ``persist`` without modifying the document would yield no new highlights.

If the document is modified and a new highlight is made, only the new highlight will be returned on the next run of ``persist``

Setting the ``--sqlalchemy`` option
***************************************

If the argument provided for the ``--sqlalchemy`` is a file, then the first line of that file is read and used as the sqlalchemy connection string. This is useful to avoid leaking secrets.

You can also set the ``REMARKING_SQLALCHEMY`` env var instead of the cmd line option.


.. _extractor_getting_started:

Extractors
----------

Extractors are what actually parse a document and return highlights for it.

You can specify the extractors you want to use via the ``--extractors`` option for both ``run`` and ``persist``.

Listing extractors
******************

You can list all extractors available to use with

.. code-block:: bash

   remarking list extractors


Adding new extractors
*********************

Check out :ref:`extractor-guide` for how to create your own extractor.


.. _writer_commands_deep:

Writer Commands
---------------

Writer commands as mentioned in the :ref:`structure_of_a_command` section are the second part of a ``remarking`` command.

Writer commands specify how the highlights should be output.

Viewing Writer Commands
***********************

You can see all available writer commands with:

.. code-block:: bash

   remarking run --help


Built-in Writer Commands
************************


Remember that ``run`` will always output all highlights found and that ``persist`` will only output new highlights found since the last execution.


json
****

.. code-block:: text

   Usage: remarking run json [OPTIONS] [COLLECTION_NAMES]...

     Output highlights and documents as JSON

   Options:
     -t, --token TEXT                One time auth token from for the reMarkable
                                     cloud. Needs only be specified once.  [env
                                     var: REMARKING_TOKEN]
     -e, --extractors TEXT           Comma delimited list of extractors to use.
                                     Run `remarking list extractors` to see valid
                                     extractors.  [default: remarkable]
     -o, --output FILENAME           Output highlights to the given file
     -w, --working-directory DIRECTORY
                                     Working directory where files will be
                                     downloaded and highlights generated.
                                     [default: (A randomly generated path within
                                     /tmp/)]
     -q, --quiet                     Print nothing.
     -h, --help                      Show this message and exit.



csv
***

.. code-block:: text

   Usage: remarking run csv [OPTIONS] [COLLECTION_NAMES]...

     Output highlights normalized with documents as csv.

     Check out `remarking list columns` for a list of columns to choose from for
     the `--columns` option.



   Options:
     -t, --token TEXT                One time auth token from for the reMarkable
                                     cloud. Needs only be specified once.  [env
                                     var: REMARKING_TOKEN]
     -e, --extractors TEXT           Comma delimited list of extractors to use.
                                     Run `remarking list extractors` to see valid
                                     extractors.  [default: remarkable]
     -o, --output FILENAME           Output highlights to the given file
     -w, --working-directory DIRECTORY
                                     Working directory where files will be
                                     downloaded and highlights generated.
                                     [default: (A randomly generated path within
                                     /tmp/)]
     -q, --quiet                     Print nothing.
     --delimiter TEXT                Delimiter to use to split columns
     --columns TEXT                  Comma delimited list of columns to print
                                     when using plain printing. `remarking list
                                     columns` shows all available columns
                                     [default: highlight_text,document_name,highl
                                     ight_page_number]
     -h, --help                      Show this message and exit.


table
*****

.. code-block:: text

   Usage: remarking run table [OPTIONS] [COLLECTION_NAMES]...

     Output highlights normalized with documents as a table.

     Check out `remarking list columns` for a list of columns to choose from for
     the `--columns` option.

   Options:
     -t, --token TEXT                One time auth token from for the reMarkable
                                     cloud. Needs only be specified once.  [env
                                     var: REMARKING_TOKEN]
     -e, --extractors TEXT           Comma delimited list of extractors to use.
                                     Run `remarking list extractors` to see valid
                                     extractors.  [default: remarkable]
     -o, --output FILENAME           Output highlights to the given file
     -w, --working-directory DIRECTORY
                                     Working directory where files will be
                                     downloaded and highlights generated.
                                     [default: (A randomly generated path within
                                     /tmp/)]
     -q, --quiet                     Print nothing.
     --truncate / --no-truncate      Truncate results when printing plain
     --plain / --no-plain            Output one data entry per line.
     --columns TEXT                  Comma delimited list of columns to print
                                     when using plain printing. `remarking list
                                     columns` shows all available columns
                                     [default: highlight_text,document_name,highl
                                     ight_page_number]
     -h, --help                      Show this message and exit.

