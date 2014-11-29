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

This package is always looking for help. An easy way for you to help us is to test
the package against a PDF, and file an issue ([here](https://github.com/jorgecarleitao/pt_law_parser/issues))
when it does not parse it correctly.

Don't forget to add the following to the issue: 

1. a link to the PDF in the [DRE.pt website](https://dre.pt/).
2. which page the parsing is failing
3. what it should appear, and what it appears.

Example: On this PDF (link), page 2, where there is the paragraph "Olá mundo",
the parser interprets it as "Olámundo".

In case you want to contribute with code, the easiest way is to pick an issue
and fix it. The pull request must contain a test case with the PDF parsed and
previously failing, and must pass all tests.
