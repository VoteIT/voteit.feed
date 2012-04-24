import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'voteit.core',
    'betahaus.pyracont',
    'betahaus.viewcomponent',
    'Babel',
    'lingua',
    'colander==0.9.5',
    'deform',
    ]

setup(name='voteit.feed',
      version='0.1dev',
      description='Feeds for VoteIT',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require= requires,
      test_suite="voteit.feed",
      entry_points = """\
      [fanstatic.libraries]
      voteit_feed_lib = voteit.feed.fanstaticlib:voteit_feed_lib
      """,
      message_extractors = { '.': [
              ('**.py',   'lingua_python', None ),
              ('**.pt',   'lingua_xml', None ),
              ('**.zcml', 'lingua_zcml', None ),
              ]},
      )
