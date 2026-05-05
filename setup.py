"""Package setup for envdiff."""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="envdiff",
    version="0.1.0",
    author="envdiff contributors",
    description="Compares environment variable configurations across multiple deployment targets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/envdiff",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
        ]
    },
    entry_points={
        "console_scripts": [
            "envdiff=envdiff.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Software Development :: Build Tools",
    ],
)
