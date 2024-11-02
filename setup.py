from setuptools import setup, find_packages

setup(
    name='adjust_line_endings.py',
    version='0.5',
    author='toru173',
    description='A Python module for working with polyglot files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/toru173/polyglot',
    packages=find_packages(),
    python_requires='>=3.7',
)
