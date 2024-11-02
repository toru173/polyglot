from setuptools import setup, find_packages

setup(
    name = 'adjust_line_endings',
    version = '0.7',
    author = 'toru173',
    description = 'A Python module for working with polyglot files',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/toru173/polyglot',
    packages = ['adjust_line_endings'],
    entry_points = {
        'console_scripts': [
            'adjust_line_endings = adjust_line_endings:main',
        ],
    }
)
