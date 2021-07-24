import sys
import typing as T

import click
import halo


def isatty() -> bool:
    """ Indicates if stderr is a tty. """
    return sys.stderr.isatty()


class HaloWrapper:
    """ A wrapper for Halo spinners. Should be constructed from :meth:`CommandLineLogger.spinner`.


    Example:
        .. code-block:: python

            spinner = HaloWrapper(logger, "MyText", "bouncingBar")
            spinner.start() # prints "MyText"
            ...
            spinner.suceed("Success text") # Prints "Success text"

    :param logger: The logger to write to.
    :param text: Initial text for the spinner
    :param spinner: The spinner to use.
            Check the `Halo documentation <https://github.com/sindresorhus/cli-spinners/blob/main/spinners.json>`_
            for options.
    :param spinner_enabled: If the spinner should be enabled or not.
                            If false no spinners are used, and only text is printed out on start, fail and succeed.
    :param quiet: If any output should be written. If true, then all output is suppressed.
    :param kwargs: Additional arguments to be passed to Halo spinner if spinners are enabled.


    """

    def __init__(self,
                 logger: 'CommandLineLogger',
                 text: str,
                 spinner: str,
                 spinner_enabled: bool = True,
                 quiet: bool = False,
                 **kwargs: T.Any):
        self.enabled = not quiet
        self.text_str = text
        self.logger = logger
        self.spinner_enabled = spinner_enabled and not quiet
        if self.spinner_enabled:
            self.halo = halo.Halo(text=self.text_str, spinner=spinner, stream=sys.stderr, enabled=True, **kwargs)

    def start(self) -> None:
        """ Called when starting a spinner for the first time.

        If spinner is disabled then it prints the currently stored text.
        """
        if self.spinner_enabled:
            self.halo.start()
        else:
            self.logger.echo(self.text_str, err=True)

    @property
    def text(self) -> str:
        """ Retrieves the current text of the spinner

            When this property is set, the spinner text is changed automatically.

            If the spinner is disabled, then the text is printed when it is set.
        """
        if self.spinner_enabled:
            return self.halo.text
        return self.text_str

    @text.setter
    def text(self, value: str) -> None:
        """ Sets the text of the spinner. If spinner is disabled, then text is printed."""
        self.text_str = value
        if self.spinner_enabled:
            self.halo.text = value
        else:
            self.__show_echo()

    def __show_echo(self) -> None:
        """ Write current text to logger stderr. Logs should always go to stderr."""
        self.logger.echo(self.text_str, err=True)

    def fail(self, text: T.Optional[str] = None) -> None:
        """ Stops the spinner with a failure icon prepended to the current text.
        If spinner is disabled, then only the stored text is printed.

        :param text: The text to use for failure. If this is not set, then the stored text is used.
        """
        if self.spinner_enabled:
            self.halo.fail(text)
        else:
            if text is not None:
                self.text_str = text
                self.__show_echo()

    def succeed(self, text: T.Optional[str] = None) -> None:
        """ Stops the spinner with a success icon prepended to the current text.
        If spinner is disabled, then only the stored text is printed.

        :param text: The text to use for success. If this is not set, then the stored text is used.
        """
        if self.spinner_enabled:
            self.halo.succeed(text)
        else:
            if text is not None:
                self.text_str = text
                self.__show_echo()


class CommandLineLogger():
    """ A logger used throughout remarking.

    The logger is created at the start of a ``remarking`` execution and is passed to methods that require logging
    functionality. By default this logs to stdout and stderr.

    :param spinners_enabled: If refreshing spinners should be used in output.
                             Used to configure the instance of :class:`HaloWrapper` returned
                             from :meth:`CommandLineLogger.spinner`.
    :param quiet: If output should be supressed.
                  This will not supress output from calls to :meth:`CommandLineLogger.output_result`
    :param file_output: When set, this indicates that all logs should go to the given file handle.

    """

    def __init__(self,
                 spinners_enabled: bool = True,
                 quiet: bool = False,
                 file_output: T.Optional[T.IO] = None):
        if not isatty():
            self._spinners_enabled = False
        else:
            self._spinners_enabled = spinners_enabled
        self._file_output = file_output
        self._quiet = quiet

    def spinner(self, text: str, spinner: str, **kwargs: T.Any) -> HaloWrapper:
        """ Return a spinner to show the user that something is happening.

        The spinner inherits the settings used to initialize the Logger.

        :param text: The text to intialize :class:`HaloWrapper` with.
        :param spinner: The spinner to pass to :class:`HaloWrapper`.
        :param kwargs: Any additional kwargs to pass to the ``Halo`` library.
        """
        return HaloWrapper(self, text, spinner, spinner_enabled=self._spinners_enabled, quiet=self._quiet, **kwargs)

    def output_result(self, text: str) -> None:
        """ Write text results as output.

        This method will ignore the quiet flag.
        It should be used to signal final output as in a :class:`Writer` implementation.

        :param text: The result to print.
        """
        if self._file_output is not None:
            self._file_output.write(text)
        else:
            sys.stdout.write(text)
            sys.stdout.flush()

    def echo(self, text: str, **kwargs: T.Any) -> None:
        """ Write text to given output.

        By default, echo uses :func:`click.echo` to write output. All kwargs are passed to :func:`click.echo`

        If the logger was constructed with a file for output,
        then text is written to a file. :func:`click.echo` is not used.

        .. code-block:: python

            self.echo(click.style("This is a red message", fg="red"), err=True)

        The above would write the text in red to the stderr.

        :param text: The text to echo.
        :param kwargs: Arguments to be passed to :func:`click.echo`.

        """
        if not self._quiet and text != "":
            click.echo(text, **kwargs)
