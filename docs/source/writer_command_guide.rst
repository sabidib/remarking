.. _writer_command_guide:

WriterCommand Guide
====================

This document goes over an example of creating the :class:`remarking.JSONWriterCommandExample`.

To start, let's make sure we have a clear goal.


.. note::
   We want to create a new :ref:`writer command<writer_command>` that outputs
   highlights and documents as a JSON string.

   .. code-block:: bash

      remarking (run|persist) json_example my_book_name

   Running the above should output our JSON string.



``remarking`` will take care of writing the output where we want it, we just need to provide
it with the proper JSON string.



In order to achieve our goal, we need to implement 2 interfaces:

-  :class:`remarking.WriterCommand`
-  :class:`remarking.Writer`


Before we start implementing them, let's start by setting up a quick feedback loop.



Iterate quickly
---------------

Detection
*********
remarking automatically detects new writer commands that are added to the ``remarking.cli.commands`` package.


Skeleton
********

We'll start by creating a file called ``remarking/cli/commands/json_writer_command_example.py`` and 
copying this skeleton into it:

.. code-block:: python

   import typing as T
   from typing import List

   from remarking import Writer
   from remarking import WriterCommand
   from remarking import ClickOption
   from remarking import CommandLineLogger
   from remarking import Highlight
   from remarking import Document


   class JSONWriterExample(Writer):
       """ Writer a json string to output.  """

       def __init__(self,
                    documents: List[Document],
                    highlights: List[Highlight],
                    ) -> None:
           pass

       def write(self, logger: CommandLineLogger) -> None:
           """ Write to output. Invoked by remarking after extraction is ran on documents. """



   class JSONWriterCommandExample(WriterCommand):
       """ JSON Writer Command for: `json_example` output writer. """

       def name(self) -> str:
           """ Return the name of the command as referenced on the command line. """
           return "json_example"

       def options(self) -> List[ClickOption]:
           """ Return a list of click options to use for the command.

           The list can be constructed from the return value of :func:`click.option`.

           These options will be added to the default options for the run or persist command.
           """
           return []

       def long_description(self) -> str:
           """ The long description for your command. Shown when running ``--help`` """
           return ""

       def short_description(self) -> str:
           """ The short description of your command. """
           return ""

       def writer(self,
                  documents: List[Document],
                  highlights: List[Highlight],
                  **kwargs: T.Any) -> Writer:
           """ Parse options and return a configured instance of a concrete :class:`Writer` class. """
           return JSONWriterExample(documents, highlights)

Let's give this a test to make sure it is found by remarking.

.. code-block:: bash

   remarking run json_example library

This should run without errors, but will not produce any output as we are not yet writing any highlights to output!


The :class:`remarking.WriterCommand` Interface
----------------------------------------------

The :class:`remarking.WriterCommand` interface is where most of the command line parsing work happens.

We can find the methods we need to implement by looking at the ``abstractmethods`` defined on :class:`remarking.WriterCommand`.

We have already created the implementation stubs in the skeleton above.

Let's go over each of the methods in the skeleton and implement them.

name
****

The :meth:`remarking.WriterCommand.name` method should return the name by which the command will be referred to on the command line.

Let's set this to ``"json_example"`` for the purpose of this example.


.. code-block:: python

    def name(self) -> str:
        """ Return the name of the command as referenced on the command line. """
        return "json_example"


options
*******

This should be a list of command line options that your command accepts. The options
should be the return value of :func:`click.option`.

To learn more about click options check out `click's options section <https://click.palletsprojects.com/en/8.0.x/options/>`_.

.. note:: text

   Keep in mind we use options in a special way.

   We do not decorate the options method, instead we return a list of :func:`click.option` objects.

Let's add some fun options to illustrate the usage:

.. code-block:: python

    import click

    def options(self) -> List[ClickOption]:
        """ Return a list of click options to use for the command.

        The list can be constructed from the return value of :func:`click.option`.

        These options will be added to the default options for the run or persist command.
        """
        return [
            click.option("--fun/--no-fun",
                         "is_fun",
                         default=False,
                         help="Have fun"
                       ),
            click.option("--compress/--no-compress",
                         "perform_compression",
                         default=False,
                         help="If compression should be performed on the output."
                       )
        ]

This adds the ``--fun/--no-fun`` boolean flags as well as the ``--compress/--no-compress`` flags. These flags
are added to the already existing arguments needed to run ``remarking`` such as the ``--token`` and ``--output`` options.


Let's check if our options are there by running:

.. code-block:: bash

   remarking run json_example --help

This should show the help for our new options.

long_description
****************

This is used for the long description of the command when running:

.. code-block:: bash

   remarking (run|persist) json_example


Let's make it long, but not too long:


.. code-block:: python

    def long_description(self) -> str:
        """ The long description for your command. Shown when running ``--help`` """
        return """

        Returns documents and highlights as a JSON string

        Has additional compression and fun options that
        """



short_description
******************

Next, we have the short description. This is used when listing all the available writer commands.

Let's make it short and sweet.

.. code-block:: python

    def short_description(self) -> str:
        """ The short description of your command """
        return "Output results as a JSON String"


Let's test our new descriptions by having a look at the output of

.. code-block:: bash

   remarking run --help

and

.. code-block:: bash

   remarking run json_example --help


writer
******

The final method we need to implement will lead us into the implementation of our ``JSONWriterExample`` class.

The ``JSONWriterCommandExample.writer`` method should return an instance of :class:`remarking.Writer`. 

In our case this means the concrete implementation ``JSONWriterExample``. 

The concrete implementation instance is passed documents and highlights processed by ``remarking`` for them to be output as JSON.

Along the way, the ``JSONWriterCommandExample.writer`` will also need to parse the ``kwargs`` argument for the options that it specified in the ``options`` method.

Let's have a look at what this all looks like:

.. code-block:: python

    def writer(self,
               documents: List[Document],
               highlights: List[Highlight],
               **kwargs: T.Any) -> Writer:
        """ Parse options and return a configured instance of a concrete :class:`Writer` class. """
        is_fun = kwargs['is_fun']
        perform_compression = kwargs['perform_compression']
        return JSONWriterExample(documents, highlights, is_fun, perform_compression)

As you can see, we reach into the ``kwargs`` dictionary to extract the named options we declared in ``options`` method.

You'll notice the ``JSONWriterExample`` constructor receives ``documents`` and ``highlights`` in addition to the options we set.

.. note::

   Having separate writer logic and command logic makes it easier to have clean code.


We won't be able to test this until we modify the ``JSONWriterExample`` class with the correct constructor.

Let's create the ``JSONWriterExample`` shortly, but before that, let's go over what we have so far.


Final State
***********

Our ``JSONWriterCommandExample`` class should resemble:

.. code-block:: python

   import typing as T
   from typing import List

   import click
   from remarking import Writer
   from remarking import WriterCommand
   from remarking import ClickOption
   from remarking import CommandLineLogger
   from remarking import Highlight
   from remarking import Document

   class JSONWriterCommandExample(WriterCommand):
       """ JSON Writer Command for: `json_example` output writer. """

       def name(self) -> str:
           """ Return the name of the command as referenced on the command line. """
           return "json_example"

       def options(self) -> List[ClickOption]:
           """ Return a list of click options to use for the command.

           The list can be constructed from the return value of :func:`click.option`.

           These options will be added to the default options for the run or persist command.
           """
           return [
               click.option("--fun/--no-fun",
                            "is_fun",
                            default=False,
                            help="Have fun"
                          ),
               click.option("--compress/--no-compress",
                            "perform_compression",
                            default=False,
                            help="If compression should be performed on the output."
                          )
           ]

       def long_description(self) -> str:
           """ The long description for your command. Shown when running ``--help`` """
           return """

           Returns documents and highlights as a JSON string

           Has additional compression and fun options that
           """

       def short_description(self) -> str:
           """ The short description of your command. """
           return "Output results as a JSON String"


       def writer(self,
                  documents: List[Document],
                  highlights: List[Highlight],
                  **kwargs: T.Any) -> Writer:
           """ Parse options and return a configured instance of a concrete :class:`Writer` class. """
           is_fun = kwargs['is_fun']
           perform_compression = kwargs['perform_compression']
           return JSONWriterExample(documents, highlights, is_fun, perform_compression)


Let's move on to defining our ``JSONWriterExample``


The :class:`remarking.Writer` Interface
---------------------------------------

The last class we need to define is the implementation of :class:`remarking.Writer`: ``JSONWriterExample``.


We previously added our definition of ``JSONWriterExample`` at the top of ``remarking/cli/commands/json_writer_command_example.py``

.. code-block:: python

   class JSONWriterExample(Writer):
       """ Writer a json string to output.  """

       def __init__(self,
                    documents: List[Document],
                    highlights: List[Highlight],
                    ) -> None:
           pass

       def write(self, logger: CommandLineLogger) -> None:
           """ Write to output. Invoked by remarking after extraction is ran on documents. """

The only method we must implement is ``JSONWriterExample.write``. We also need to make sure we implement
a constructor that can take the documents, highlights `and` the options we set in ``JSONWriterCommandExample``.

Let's match the signature of ``JSONWriterExample`` to the one we used in ``JSONWriterCommandExample.writer``:

.. code-block:: python

   def __init__(self,
                documents: List[Document],
                highlights: List[Highlight],
                is_fun: bool,
                perform_compression: bool) -> None:
       self.is_fun = is_fun
       self.perform_compression = perform_compression
       self.data = {
          'documents': [doc.to_dict() for doc in documents],
          'highlights': [highlight.to_dict() for highlight in highlights]
       }


Note that we also create a dictionary with the ``highlights`` and ``documents`` keys. 

This will be the dictionary we output as a JSON string.

Let's make sure everything works by giving our example a run:

.. code-block:: bash

   remarking run json_example --compress library

Once again, nothing should be displayed, but there should be no errors.

write
*****

The last method we need to implement is ``write``.

The ``write`` method receives an instance of :class:`remarking.CommandLineLogger` called ``logger`` that is configured to send output to the correct location.

You should use :meth:`remarking.CommandLineLogger.output_result` to write any strings for the user to further process.

Check out the class reference for :class:`remarking.CommandLineLogger` for information on other methods you can use to print statuses.

Our implementation should be something like this:

.. code-block:: python

    import zlib
    import base64
    import json
    from remarking.cli.commands.json_writer_command import json_serial

    def write(self, logger: CommandLineLogger) -> None:
        """ Write to a logger"""
        json_string = json.dumps(self.data, default=json_serial)
        if self.is_fun:
            json_string = "Only errors for you."

        if self.perform_compression:
             json_string = base64.b64encode(
                 zlib.compress(
                     json_string.encode("utf-8")
                 )
             ).decode("utf-8")

        logger.output_result(json_string + '\n')


You can see we have utilized the ``self.is_fun`` and ``self.perform_compression`` that we defined as options in our :class:`JSONWriterCommandExample`.

We use the ``json.dumps`` command to turn our ``self.data`` dictionary into a json string. Note that we use the ``json_serial`` method from the built-in :class:`JSONWriter` so that we can handle serializing dates.

Finally, we output our result with :meth:`CommandLineLogger.output_result`.


All together now
----------------


The final contents of ``remarkable/cli/commands/json_writer_command_example.py`` should be:

.. code-block:: python

   import base64
   import json

   import typing as T
   from typing import List

   import zlib


   import click
   from remarking import Writer
   from remarking import WriterCommand
   from remarking import ClickOption
   from remarking import CommandLineLogger
   from remarking import Highlight
   from remarking import Document

   from remarking.cli.commands.json_writer_command import json_serial


   class JSONWriterExample(Writer):
       """ Writer a json string to output.  """


       def __init__(self,
                    documents: List[Document],
                    highlights: List[Highlight],
                    is_fun: bool,
                    perform_compression: bool) -> None:
           self.is_fun = is_fun
           self.perform_compression = perform_compression
           self.data = {
              'documents': [doc.to_dict() for doc in documents],
              'highlights': [highlight.to_dict() for highlight in highlights]
           }

       def write(self, logger: CommandLineLogger) -> None:
           """ Write to output. Invoked by remarking after extraction is ran on documents. """
           json_string = json.dumps(self.data, default=json_serial)
           if self.is_fun:
               json_string = "Only errors for you."

           if self.perform_compression:
                json_string = base64.b64encode(
                    zlib.compress(
                        json_string.encode("utf-8")
                    )
                ).decode("utf-8")

           logger.output_result(json_string + '\n')



   class JSONWriterCommandExample(WriterCommand):
       """ JSON Writer Command for: `json_example` output writer. """

       def name(self) -> str:
           """ Return the name of the command as referenced on the command line. """
           return "json_example"

       def options(self) -> List[ClickOption]:
           """ Return a list of click options to use for the command.

           The list can be constructed from the return value of :func:`click.option`.

           These options will be added to the default options for the run or persist command.
           """
           return [
               click.option("--fun/--no-fun",
                            "is_fun",
                            default=False,
                            help="Have fun"
                          ),
               click.option("--compress/--no-compress",
                            "perform_compression",
                            default=False,
                            help="If compression should be performed on the output."
                          )
           ]

       def long_description(self) -> str:
           """ The long description for your command. Shown when running ``--help`` """
           return """

           Returns documents and highlights as a JSON string

           Has additional compression and fun options that
           """

       def short_description(self) -> str:
           """ The short description of your command. """
           return "Output results as a JSON String"


       def writer(self,
                  documents: List[Document],
                  highlights: List[Highlight],
                  **kwargs: T.Any) -> Writer:
           """ Parse options and return a configured instance of a concrete :class:`Writer` class. """
           is_fun = kwargs['is_fun']
           perform_compression = kwargs['perform_compression']
           return JSONWriterExample(documents, highlights, is_fun, perform_compression)

Finally we can run our command with:

.. code-block:: bash

   remarking run json_example library


We can use the compress option to compress our JSON string:

.. code-block:: bash

   remarking run json_example --compress library


We can also have some fun:


.. code-block:: bash

   remarking run json_example --fun library


Next Steps
----------

Once you have your new writer command open a pull request as outlined in the `contribution doc <https://github.com/sabidib/remarking/blob/master/CONTRIBUTING.md>`_ and someone will be pinged for review!


