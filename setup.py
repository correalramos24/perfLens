import re
from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent
VERSION = re.search(r'__version__ = "(.+)"',
                    (HERE / "perfLens" / "__init__.py").read_text()).group(1)

setup(
    name="perflens",
    version=VERSION,
    description="Gather performance metrics from rundirs.",
    long_description=(HERE / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Victor Correal",
    url="https://github.com/correalramos24/perfLens",
    license="LICENSE",
    python_requires=">=3.6",
    packages=find_packages(include=["perfLens", "perfLens.*"]),
    install_requires=["pandas>=1.1"],
    entry_points={"console_scripts": ["perfLens = perfLens.cli:main"]},
)
