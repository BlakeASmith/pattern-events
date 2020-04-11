from pathlib import Path
from setuptools import setup, find_packages

here = Path(__file__).parent
readme = (here / 'README.rst').read_text()

setup(
        name='pattern-events',
        version='0.0.1',
        description='Detect changed to patterns within files',
        long_description=readme,
        long_description_content_type='text/x-rst',
        url='TODO',
        author='Blake Smith',
        install_requires=[
            'fs-events'
        ]
        packages=find_packages(),
)
