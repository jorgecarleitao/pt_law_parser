# encoding: utf-8
from distutils.core import setup

setup(name='PT-Law-parser',
      version='0.1',
      description='Parser of the official PDF documents of the portuguese law.',
      long_description=open('README.md').read(),
      author='Jorge C. Leitão',
      url='https://github.com/jorgecarleitao/pt_law_parser',
      packages=('pt_law_parser',),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
)
