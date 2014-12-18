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

This package has two dependencies: 

1 a fork of PDFMiner, a tool to parse PDFs. To install it, run

`pip install git+https://github.com/jorgecarleitao/pdfminer.git@main`

2 [pycrypto](https://www.dlitz.net/software/pycrypto/). To install it, run

`pip install pycrypto`

Finally, you can install `pt_law_parser` running:

`pip install git+https://github.com/jorgecarleitao/pt_law_parser`

## Tests

The package contains a test suite that you can run with

`python -m unittest discover`

## Contributions and issues

This package is always looking for help. The easiest way to contribute is to test
the package against an official PDF, and file an issue 
([here](https://github.com/jorgecarleitao/pt_law_parser/issues)) when it does not
parse it correctly. Don't forget to add the following to the issue: 

1. a link to the PDF in the [DRE.pt website](https://dre.pt/);
2. which page the parsing is failing;
3. what it should appear, and what it appears.

Example: On this PDF (link), page 2, where there is the paragraph "Olá mundo",
the parser interprets it as "Olámundo".

If you are passionate about the project and would like to contribute with code,
the easiest way is to take a look at the tests directory and propose a solution
(by pull request) to tests marked as `expectedFailure`. Other possibility
is to pick an issue and fix it. Issues tend to be a bit more complicated since
they typically require designing an algorithm or component.

Pull requests must contain a test case with the PDF parsed and previously failing,
and must pass all tests.

Other things that can be done include improving the code (PEP8, function names, 
inline comments explaining the code, etc.). We are always trying to improve our
code to be easily readable.
