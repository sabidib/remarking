#!/usr/bin/env python3
# pylint: disable=all

import os
import subprocess
import textwrap
import typing as T
from typing import List, Tuple

examples: T.List[T.Dict[str, T.Any]] = [
    {
        "title": "JSON output",
        "command": "remarking run json books | jq",
        "description": "Run remarking over a folder called ``books`` in the reMarkable cloud."
    },
    {
        "title": "JSON output to file",
        "command": "remarking run json -o highlights.json books | jq",
        "file": "highlights.json",
        "description": "Run remarking over the books folder and write the resulting highlights to file named ``highlights.json``"
    },
    {
        "title": "Specify extractors",
        "command": "remarking run json --extractors remarkable books | jq ",
        "description": "Use the remarkable extractor to extract highlights from documents. You can see all available extractors by running ``remarking list extractors``. ``remarkable`` is the default value for ``--extractors`` option."
    },
    {
        "title": "CSV output",
        "command": "remarking run csv books",
        "description": "Run remarking over the books folder and output the discovered highlights as a csv."
    },
    {
        "title": "CSV output to file",
        "command": "remarking run csv -o highlights.csv books",
        "file": "highlights.csv",
        "description": "Run remarking over the books folder and output the resulting highlights as a csv to a file called ``highlights.csv`` file."
    },
    {
        "title": "CSV output to file with custom delimiter",
        "command": "remarking run csv -o highlights.csv --delimiter '|' books",
        "file": "highlights.csv",
        "description": "Run remarking over the books folder and output the resulting highlights as a csv to a file called ``highlights.csv`` file. The csv will be delimited with a ``|``."
    },
    {
        "title": "Table output",
        "command": "remarking run table books",
        "description": "Print out a table that contains the highlights for all documents in the books folder."
    },
    {
        "title": "Plain table output",
        "command": "remarking run table --plain books",
        "description": "Print out a table that contains the highlights for all documents in the books folder. When printing plain only whitespace separates columns and newlines for each row."
    },
    {
        "title": "Persist",
        "command": "remarking persist json books | jq",
        "description": "Use a database to keep track of documents seen, and highlights produced. When using the persist command, the last modified date of documents in the Remarkable cloud will be used to trigger their processing. highlights are deduped by checking their text and document. By default, if a ``--sqlalchemy`` argument is passed, a sqlite file is created in the current working directory called ``remarking.sqlite3``. "
        "The persist argument will only output highlights that are considered new according to the database state."
    },
    {
        "title": "Persist SQLite",
        "command": "remarking persist --sqlalchemy sqlite:///my_database.sqlite3 json books | jq",
        "description": "When passing the ``--sqlalchemy`` option, persist will use the option to create a sqlalchemy engine. This is particularly useful for syncing with an external database. Check the sqlalchemy documentation for more info on sqlalchemy connection string. You can also set the ``REMARKING_PERSIST_SQALCHEMY`` env var instead of the ``--sqlalchemy`` option."
    },
    {
        "title": "Persist MySQL",
        "command": "remarking persist --sqlalchemy mysql+pymysql://user:pass@host/dbname?charset=utf8mb4 json books | jq",
        "run": False,
        "description": "Use the mysql database located at host for state management. You can query this database directly to extract all historical highlights and documents."
    },
    {
        "title": "Quiet logging",
        "command": "remarking run json -q books | jq",
        "description": "Quiet any logging with ``-q`` Only the results are output stdout."
    },
]


example_format = """
{title}

{description}

.. code-block:: text

    > {command}
{output}

{file_message_and_output}

"""

file_message_template = """

The contents of {filename}

.. code-block:: text

{contents}

"""


def main() -> None:
    example_result_list: List[Tuple[T.Dict[str, str], str, str]] = []

    for example in examples:
        file = example.get("file")
        file_message_and_output = ""
        print(f"Running {example['command']}")
        if example.get("run") is None:
            if 'persist' in example['command']:
                if os.path.exists('my_database.sqlite3'):
                    os.remove('my_database.sqlite3')
            process = subprocess.run(example['command'].replace("books", "test2"), capture_output=True, shell=True)

            output = ""
            if file:
                with open(file, "r") as fp:
                    file_message_and_output = file_message_template.format(
                        filename=file,
                        contents=textwrap.indent(fp.read(), "    ")
                    )

            output = process.stderr.decode("utf-8") + process.stdout.decode("utf-8")

        else:
            output = example_result_list[-1][2]
            if file:
                raise Exception("Can't handle this case yet")

        example_result_list.append(
            (
                example,
                example_format.format(
                    title=example['title'] + '\n' + '-' * len(example['title']),
                    command=example['command'],
                    output=textwrap.indent(output, "    "),
                    file_message_and_output=file_message_and_output,
                    description=example['description']
                ),
                textwrap.indent(output, "    ")
            )
        )
        print(example_result_list[-1][1])

    with open("source/examples.rst", "w") as fp:
        with open("templates/examples.md", "r") as fp_template:
            template = fp_template.read()
            fp.write(template.format(
                examples="\n".join(example[1].replace("test2", "books") for example in example_result_list)
            ))

    to_delete = [
        "highlights.csv",
        "highlights.json",
        "my_database.sqlite3"
    ]

    for file in to_delete:
        if os.path.exists(file):
            os.remove(file)


if __name__ == "__main__":
    main()
