
from abc import ABCMeta

from remarking.cli import log


class Writer(metaclass=ABCMeta):
    """ Base class for defining custom writers.

        Concrete implementations of a configured :class:`Writer` instance are returned by
        :meth:`WriterCommand.writer` to be excuted by remarking.

        For example, :meth:`JSONWriterCommand.writer` returns a configured instance of
        :class:`JSONWriter` which will then have :meth:`JSONWriter.write` called by remarking.
    """

    def write(self, logger: log.CommandLineLogger) -> None:
        """ Write to output. Invoked by remarking after extraction is ran on documents.

        :param logger: A logger for writing output to.
        """
