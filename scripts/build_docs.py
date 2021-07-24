#!/usr/bin/env python3
# pylint: disable=all

def main() -> None:
    examples_file = 'data/examples.txt'
    example_template_file = 'templates/examples.md'
    example_doc_file = 'docs/examples.md'

    example_template_string = ""

    with open(example_template_file, "r") as example_template_fp:
        with open(examples_file, "r") as example_fp:
            with open(example_doc_file, "w") as example_doc_fp:
                example_doc_fp.write(
                    example_template_fp.read().format(
                        examples=example_fp.read()
                    )
                )


if __name__ == "__main__":
    main()
