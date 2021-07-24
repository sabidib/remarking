
.. _extractor-guide:

Write an Extractor
==================

This document goes over an example of creating :class:`remarkable.RemarkableHighlightExtractorExample`

To start, let's make sure we have a clear goal.

.. note::
   We want to create a new :ref:`extractor<extractor_getting_started>` that outputs a list
   of highlights for a given document

   .. code-block:: bash

       remarking (run|persist) json --extractor remarkable_example my_book_name

   This should run our extractor on ``my_book_name`` and output the highlights our extractor finsd.


In order to achieve our goal, we need to implement the :class:`remarking.HighlightExtractor` interface.


The :class:`remarking.HighlightExtractor` Interface
---------------------------------------------------


The :class:`remarking.HighlightExtractor` has a fairly straight forward
interface for us to implement.


Let's start by creating a file called ``remarking/highlight_extractor/remarkable_highlight_extractor_example.py``
and adding this to the file:

.. code-block:: python


    from typing import List 

    from remarking import HighlightExtractor
    from remarking import ExtractorData
    from remarking import Document
    from remarking import Highlight


    class RemarkableHighlightExtractorExample(HighlightExtractor):
        """ Extracts highlights from reMarkable documents. """

        @classmethod
        def get_extractor_instance_data(cls) -> List[ExtractorData]:
            """ Return a list of :class:`ExtractorData` instaces representing
                different run options for the extractor.
            """
            return [
                ExtractorData(
                    extractor_name="remarkable_example",
                    instance=cls(),
                    description=cls.__doc__
                )
            ]

        def get_highlights(self, working_path: str, document: Document) -> List[Highlight]:
            """ Retrieve all highlights for document. """
            return []


Let's check if ``remarking`` has found our extractor:

.. code-block:: bash

   remarking list extractor

Should show our extractor named ``remarkable_example`` and produce no errors.

Let's dive into implementing the methods a bit more now.

:meth:`HighlightExtractor.get_extractor_instance_data <remarking.HighlightExtractor.get_extractor_instance_data>`
*****************************************************************************************************************

The :meth:`HighlightExtractor.get_extractor_instance_data <remarking.HighlightExtractor.get_extractor_instance_data>` method returns a list of :class:`ExtractorData` instances. Ecah instance is used by ``remarking`` in order to offer the extractor through ``remarking list extractors`` and the ``--extractors`` option for output writers.

An entry in ``remarking list extractors`` will be placed for each :class:`ExtractorData` entry we return.

Let's plan for our extractor to have two modes, a fast mode and an accurate mode. The accurate mode should be expected
to take longer.

To reflect this, let's change the implementation of ``get_extractor_instance_data`` and add a constructor:


.. code-block:: python

    def __init__(self, fast: bool = False):
        self.fast = fast

    @classmethod
    def get_extractor_instance_data(cls) -> List[ExtractorData]:
        """ Return a list of :class:`ExtractorData` instaces representing
            different run options for the extractor.
        """
        return [
            ExtractorData(
                extractor_name="remarkable_example_accurate",
                instance=cls(fast=False),
                description=cls.__doc__ + " This version is more accurate."
            ),
            ExtractorData(
                extractor_name="remarkable_example_fast",
                instance=cls(fast=True),
                description=cls.__doc__ + " This version runs faster."
            )
        ]


Let's test our change by running ``remarking list extractors``.

We should see two extractors, one for each of the entries we returned.

:meth:`HighlightExtractor.get_highlights <remarking.HighlightExtractor.get_highlights>`
***************************************************************************************


:meth:`HighlightExtractor.get_highlights <remarking.HighlightExtractor.get_highlights>` is where the magic happens. It accepts a ``working_path`` where all the documents for the current execution of ``remarking`` are stored.

It also accepts a ``document`` indicating which document to return highlights for.

``remarking`` expects the extractor to return a list of :class:`Highlight` objects that represent the highlights found.

Let's make our implementation simple. A more complicated implementation can be seen in ``remarking/highlight_extractor/remarkable_highlight_extractor.py``.

.. code-block:: python

    def get_highlights(self, working_path: str, document: Document) -> List[Highlight]:
        """ Retrieve all highlights for document. """
        if self.fast:
            quote = f"A fast quote from {document.name}"
        else:
            quote = f"An accurate quote from {document.name}"

        return [
            Highlight.create_highlight(
                doc_id=document.id,
                text=quote,
                page_number=1,
                extraction_method="RemarkableHighlightExtractorExample",
            )
        ]


We're not actually parsing highlights in this example.

Instead, we simple return a quote indicating if we ran the fast option. We also include the document name.

Let's test this by running:

.. code-block:: text

   remarking run json --extractors remarkable_example_fast library

This should run the fast version of our extractor and return a single highlight per document found in library.


We can also run the accurate version with:

.. code-block:: text

   remarking run json --extractors remarkable_example_accurate library


Both examples should run without error.

Congratulations, your extractor just ran!

All together now
----------------

Our final implementation of ``remarking/highlight_extractor/remarkable_highlight_extractor.py`` should be:

.. code-block:: python

    from typing import List

    from remarking import HighlightExtractor
    from remarking import ExtractorData
    from remarking import Document
    from remarking import Highlight

    class RemarkableHighlightExtractorExample(HighlightExtractor):
        """ Extracts highlights from reMarkable documents. """

        def __init__(self, fast: bool = False):
            self.fast = fast

        @classmethod
        def get_extractor_instance_data(cls) -> List[ExtractorData]:
            """ Return a list of :class:`ExtractorData` instaces representing
                different run options for the extractor.
            """
            return [
                ExtractorData(
                    extractor_name="remarkable_example_accurate",
                    instance=cls(),
                    description=cls.__doc__
                ),
                ExtractorData(
                    extractor_name="remarkable_example_fast",
                    instance=cls(fast=True),
                    description=cls.__doc__ + " This version runs faster."
                )
            ]

        def get_highlights(self, working_path: str, document: Document) -> List[Highlight]:
            """ Retrieve all highlights for document. """
            if self.fast:
                quote = f"A fast quote from {document.name}"
            else:
                quote = f"An accurate quote from {document.name}"

            return [
                Highlight.create_highlight(
                    doc_id=document.id,
                    text=quote,
                    page_number=1,
                    extraction_method="RemarkableHighlightExtractorExample",
                )
            ]



Check out the implementation of :class:`remarking.RemarkableHighlightExtractor` for an example of a more complex extractor!


Next Steps
----------

Once you have designed your new extractor open a pull request as outlined in the `contribution doc <https://www.github.com/sabidib/remarking/CONTRIBUTING.md>`_ and someone will review it!


