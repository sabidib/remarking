# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we have a [code of conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.


## Requirements

For development you will need at least:
  - Python 3.8+
  - pip
  - Poetry

## Development environment setup

To set up a development environment, please follow these steps:

1. Clone the repo

   ```sh
   git clone https://github.com/sabidib/remarking
   ```

2. Prepare the development environment:

   ```
   scripts/setup_develpment
   ```

3. Run `poetry install` to install dependencies.

4. Enter the poetry virtualenv with `poetry shell`.

5. Get contributing! Check out the [writer command walkthrough](https://remarking.readthedocs.com/writer_command_guide.html) or the [extractor walkthrough](https://remarking.readthedocs.com/extractor_guide.html)


## Issues and feature requests

You've found a bug in the source code, a mistake in the documentation or maybe you'd like a new feature? You can help us by submitting an issue to our [GitHub Repository](https://github.com/sabidib/remarking/issues). Before you create an issue, make sure you search the archive, maybe your question was already answered.

Please try to create bug reports that are:

- _Reproducible._ Include steps to reproduce the problem.
- _Specific._ Include as much detail as possible: which version, what environment, etc.
- _Unique._ Do not duplicate existing opened issues.
- _Scoped to a Single Bug._ One bug per report.

Even better: You could submit a pull request with a fix or new feature!

## Pull request process

1. Search our repository for open or closed
[pull requests](https://github.com/sabidib/remarking/pulls)
that relates to your submission. You don't want to duplicate effort.
2. Fork the project
3. Create your feature branch (`git checkout -b amazing_feature`)
4. Commit your changes (`git commit -m 'add amazing_feature'`)
5. Push to the branch (`git push origin amazing_feature`)
6. Open a pull request

