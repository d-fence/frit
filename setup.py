from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='frit',
      version=version,
      description="Forensic Robust Investigation Toolkit",
      long_description="""\
A framework for forensic investigations.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='forensics security recovery',
      author='Christophe Monniez',
      author_email='christophe.monniez@fccu.be',
      url='',
      license='GPL-3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
