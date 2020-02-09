from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    install_requires = fp.readlines()

setup(
    name='mongoengine-history',
    packages=find_packages(),
    version='1.0',
    description='Track the documents changes',
    author='Álvaro García Gómez',
    author_email='maxpowel@gmail.com',
    url='https://github.com/maxpowel/mongoengine-history',
    download_url='https://github.com/maxpowel/mongoengine-history/archive/master.zip',
    keywords=['mongoengine', 'dictdiff', 'diff', 'history', 'log', 'dictdiffer'],
    classifiers=['Topic :: Adaptive Technologies', 'Topic :: Software Development', 'Topic :: System',
                 'Topic :: Utilities'],
    install_requires=install_requires
)
