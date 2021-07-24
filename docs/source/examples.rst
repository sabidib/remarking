Examples
########

This document goes over some usages of remarking.

Note: we use `jq` tool here to format the output json. This is not needed if you're piping to another command or to a file.


JSON output
-----------
.. contents::
   :local:


Run remarking over a folder called ``books`` in the reMarkable cloud.

.. code-block:: text

    > remarking run json books | jq
    Extractors: remarkable
    Collections: books
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
          "version": 7,
          "modified_client": 1626736737,
          "type": "DocumentType",
          "name": "Through the Looking Glass",
          "current_page": 12,
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
          "extracted_at": 1626993849,
          "extraction_method": "RemarkableHighlightExtractor"
        }
      ]
    }






JSON output to file
-------------------

Run remarking over the books folder and write the resulting highlights to file named ``highlights.json``

.. code-block:: text

    > remarking run json -o highlights.json books | jq
    Extractors: remarkable
    Collections: books
    Connecting to RM cloud
    Connected to RM cloud.
    Retrieving cloud metadata
    Downloading documents
    Downloading "Through the Looking Glass"
    Downloaded 1 documents.
    Running extractors on documents
    Running extractor "RemarkableHighlightExtractor" on "Through the Looking Glass"
    Ran extractors and found 1 highlights, 1 are new.




The contents of highlights.json

.. code-block:: text

    {"documents": [{"id": "2b329909-332d-4c28-b6c1-d298227cc82c", "version": 7, "modified_client": 1626736737, "type": "DocumentType", "name": "Through the Looking Glass", "current_page": 12, "bookmarked": false, "parent": "d29d67f9-faff-429c-b800-b7815173dcb2"}], "highlights": [{"hash": "14235eca5db4a758ad34ab483df737714d10e710a3e3277d726a64da", "document_id": "2b329909-332d-4c28-b6c1-d298227cc82c", "text": "Alice was sitting curled up in a corner of the great arm-chair", "page_number": 11, "extracted_at": 1626993854, "extraction_method": "RemarkableHighlightExtractor"}]}






CSV output
----------

Run remarking over the books folder and output the discovered highlights as a csv.

.. code-block:: text

    > remarking run csv books
    Extractors: remarkable
    Collections: books
    Connecting to RM cloud
    Connected to RM cloud.
    Retrieving cloud metadata
    Downloading documents
    Downloading "Through the Looking Glass"
    Downloaded 1 documents.
    Running extractors on documents
    Running extractor "RemarkableHighlightExtractor" on "Through the Looking Glass"
    Ran extractors and found 1 highlights, 1 are new.
    highlight_text,highlight_page_number,document_name
    Alice was sitting curled up in a corner of the great arm-chair,11,Through the Looking Glass






CSV output to file
------------------

Run remarking over the books folder and output the resulting highlights as a csv to a file called ``highlights.csv`` file.

.. code-block:: text

    > remarking run csv -o highlights.csv books
    Extractors: remarkable
    Collections: books
    Connecting to RM cloud
    Connected to RM cloud.
    Retrieving cloud metadata
    Downloading documents
    Downloading "Through the Looking Glass"
    Downloaded 1 documents.
    Running extractors on documents
    Running extractor "RemarkableHighlightExtractor" on "Through the Looking Glass"
    Ran extractors and found 1 highlights, 1 are new.




The contents of highlights.csv

.. code-block:: text

    highlight_text,highlight_page_number,document_name
    Alice was sitting curled up in a corner of the great arm-chair,11,Through the Looking Glass






Custom CSV output to file
-------------------------

Run remarking over the books folder and output the resulting highlights as a csv to a file called ``highlights.csv`` file. The csv will be delimited with a ``|``.

.. code-block:: text

    > remarking run csv -o highlights.csv --delimiter '|' books
    Extractors: remarkable
    Collections: books
    Connecting to RM cloud
    Connected to RM cloud.
    Retrieving cloud metadata
    Downloading documents
    Downloading "Through the Looking Glass"
    Downloaded 1 documents.
    Running extractors on documents
    Running extractor "RemarkableHighlightExtractor" on "Through the Looking Glass"
    Ran extractors and found 1 highlights, 1 are new.




The contents of highlights.csv

.. code-block:: text

    highlight_text|highlight_page_number|document_name
    Alice was sitting curled up in a corner of the great arm-chair|11|Through the Looking Glass






Table output
------------

Print out a table that contains the highlights for all documents in the books folder.

.. code-block:: text

    > remarking run table books
    Extractors: remarkable
    Collections: books
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






Plain table output
------------------

Print out a table that contains the highlights for all documents in the books folder. When printing plain only whitespace separates columns and newlines for each row.

.. code-block:: text

    > remarking run table --plain books
    Extractors: remarkable
    Collections: books
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
    Alice was sitting curled up in a corner of the great arm-chair                       11  Through the Looking Glass






Specify extractors
------------------

Use the remarkable extractor to extract highlights from documents. You can see all available extractors by running ``remarking list extractors``. ``remarkable`` is the default value for ``--extractors`` option.

.. code-block:: text

    > remarking run json --extractors remarkable books | jq 
    Extractors: remarkable
    Collections: books
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
          "version": 7,
          "modified_client": 1626736737,
          "type": "DocumentType",
          "name": "Through the Looking Glass",
          "current_page": 12,
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
          "extracted_at": 1626993883,
          "extraction_method": "RemarkableHighlightExtractor"
        }
      ]
    }






Persist
-------

Use a database to keep track of documents seen, and highlights produced. When using the persist command, the last modified date of documents in the Remarkable cloud will be used to trigger their processing. highlights are deduped by checking their text and document. By default, if a ``--sqlalchemy`` argument is passed, a sqlite file is created in the current working directory called ``remarking.sqlite3``. The persist argument will only output highlights that are considered new according to the database state.

.. code-block:: text

    > remarking persist json books | jq
    Extractors: remarkable
    Collections: books
    Connecting to RM cloud
    Connected to RM cloud.
    Retrieving cloud metadata
    Downloading documents
    Downloaded 0 documents.
    Running extractors on documents
    Ran extractors and found 0 highlights, 0 are new.
    {
      "documents": [],
      "highlights": []
    }






Persist to SQLite
-----------------

When passing the ``--sqlalchemy`` option, persist will use the option to create a sqlalchemy engine. This is particularly useful for syncing with an external database. Check the sqlalchemy documentation for more info on sqlalchemy connection string. You can also set the ``REMARKING_PERSIST_SQALCHEMY`` env var instead of the ``--sqlalchemy`` option.

.. code-block:: text

    > remarking persist --sqlalchemy sqlite:///my_database.sqlite3 json books | jq
    Extractors: remarkable
    Collections: books
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
          "version": 7,
          "modified_client": 1626736737,
          "type": "DocumentType",
          "name": "Through the Looking Glass",
          "current_page": 12,
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
          "extracted_at": 1626993891,
          "extraction_method": "RemarkableHighlightExtractor"
        }
      ]
    }






Persist to MySQL
----------------

Use the mysql database located at host for state management. You can query this database directly to extract all historical highlights and documents.

.. code-block:: text

    > remarking persist --sqlalchemy mysql+pymysql://user:pass@host/dbname?charset=utf8mb4 json books | jq
        Extractors: remarkable
        Collections: books
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
              "version": 7,
              "modified_client": 1626736737,
              "type": "DocumentType",
              "name": "Through the Looking Glass",
              "current_page": 12,
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
              "extracted_at": 1626993891,
              "extraction_method": "RemarkableHighlightExtractor"
            }
          ]
        }






Quiet logging
-------------

Quiet any logging with ``-q`` Only the results are output stdout.

.. code-block:: text

    > remarking run json -q books | jq
    {
      "documents": [
        {
          "id": "2b329909-332d-4c28-b6c1-d298227cc82c",
          "version": 7,
          "modified_client": 1626736737,
          "type": "DocumentType",
          "name": "Through the Looking Glass",
          "current_page": 12,
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
          "extracted_at": 1626993896,
          "extraction_method": "RemarkableHighlightExtractor"
        }
      ]
    }





