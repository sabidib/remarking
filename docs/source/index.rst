Welcome to Remarking
====================

Remarking is tool for easily extracting highlights from documents in the Remarkable cloud.

Remarking aim to make it as easy as possible extract highlights. It also excels at providing
a clean API for adding new extraction functionality and output functionality.


Remarking in three points:

-  allows you to incrementally extract highlights to a backing database.
-  easy to use API for adding new functionality.
-  follows UNIX philosophy of composable tooling.


What does it look like? Let's see:

.. code-block:: bash

   > remarking run json library
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

Installation
------------

To install Remarking run:

.. code-block:: bash

  pip3 install remarking

Usage
-----

For a usage guide check out :doc:`usage`.


Persisting
----------

If you run with ``remarking persist``, then you can specify the ``--sqlalchemy`` option to incrementally sync new highlights to a database.

Check out the `sqlalchemy documentation <https://docs.sqlalchemy.org/en/latest/core/engines.html>`_ for infomation on sqlalchemy connection strings.

An example of using ``persist``:

.. code-block:: bash

   > remarking persist --sqlalchemy sqlite:///my_database.sqlite3 json books | jq
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
         "extracted_at": 1626723250,
         "extraction_method": "RemarkableHighlightExtractor"
       }
     ]
   }

The sqlite database file ``my_database.sqlite3`` now contains the highlight and document data.

Another run of ``persist`` should produce no new highlights, as long as the document has not been modified:

.. code-block:: bash

   > remarking persist --sqlalchemy sqlite:///my_database.sqlite3 json books | jq
   Extractors: remarkable
   Collections: library
   Connecting to RM cloud
   Connected to RM cloud.
   Retrieving cloud metadata
   Downloading documents
   Downloaded 0 documents.
   Running extractors on documents
   Ran extractors and found 0 highlights, 0 are new.
   {"documents": [], "highlights": []}


Documentation
-------------

This part of the documentation guides you through usage and contribution guides.

.. toctree::
   :maxdepth: 2

   Installation and Getting Started<usage>
   Guide<guide>

API Reference
-------------
If you are looking for information on a specific public API function, class or method:

.. toctree::
   :maxdepth: 2

   API<api>

Miscellaneous Pages
-------------------

.. toctree::
   :maxdepth: 1

   Examples<examples>
   Contributing<https://github.com/sabidib/remarking/blob/master/CONTRIBUTING.md>
   License<https://github.com/sabidib/remarking/blob/master/LICENSE>

