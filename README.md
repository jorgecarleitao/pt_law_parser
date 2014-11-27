[![Build Status](https://travis-ci.org/jorgecarleitao/pt_law_parser.svg)](https://travis-ci.org/jorgecarleitao/pt_law_parser)

# PT Law Parser

PT law parser is an open source Python package to parse the official PDFs of the
Portuguese law to HTML. Thanks for checking it out.

## The problem this package solves

The portuguese law is officially published in PDF. As a consequence, it is
difficult to perform text analysis on it. This package solves that problem by
allowing the user to convert the law to HTML.

This package aims to parse *everything* in the PDF. It currently parses text,
tables, and images. However, this parser does not parse *any PDF*. Only PDFs
published since ~1996, since previous PDFs are image-only and require OCR
recognition.

Since PDF is a very diverse format, there will always be edge cases, which means
that we cannot guarantee a 100% fidelity of the results. Fortunately, neither a
person can.

## Author

The author of this package is Jorge C. Leitão.

## The code

This package is written in Python and is licenced under MIT licence.
We use Python 2.7 since our dependency still does not support Python 3.

## Pre-requisites and installation

The package is a normal Python package. It depends on a fork of PDFMiner, a tool
to parse PDFs. To install it, run

`pip install git+https://github.com/jorgecarleitao/pdfminer.git@main`

## Tests

The package contains a test suite that you can run with

`python -m unittest discover`

## Contributions and issues

If you find a problem or bug, please file an
[issue](https://github.com/jorgecarleitao/pt_law_parser/issues).

If you have a specific PDF that is not parsing correctly, please refer to it in
the issue so we can reproduce the error.

If you want to contribute to the package, you can submit a pull request.
