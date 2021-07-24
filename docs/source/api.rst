
API
===


.. module:: remarking


This part of the document lists full API reference for all public classes and functions



Base Classes
------------

.. autoclass:: remarking.WriterCommand
   :members:

.. autoclass:: remarking.Writer
   :members:

.. autoclass:: remarking.HighlightExtractor
   :members:


Models
------

.. autoclass:: remarking.Document
   :members:
   :undoc-members:
   :special-members: __init__

.. autoclass:: remarking.Highlight
   :members:
   :undoc-members:
   :special-members: __init__



Extractors
----------

.. autoclass:: remarking.ExtractorData
   :members:

.. autoclass:: remarking.RemarkableHighlightExtractor


Writers
-------

.. autoclass:: remarking.JSONWriter

.. autoclass:: remarking.CSVWriter

.. autoclass:: remarking.TableWriter

Writer Commands
---------------

.. autoclass:: remarking.JSONWriterCommand

.. autoclass:: remarking.CSVWriterCommand

.. autoclass:: remarking.TableWriterCommand


Utilities
---------

.. autoclass:: remarking.CommandLineLogger
   :members:

.. autoclass:: remarking.HaloWrapper
   :members:
