from setuptools import setup, find_packages
from os import path

here: str = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="labctl",
    version="0.0.1",
    description="An utility for controlling laboratory equipment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luizribeiro/labctl",
    author="Luiz Ribeiro",
    author_email="luizribeiro@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="lab automation, laboratory, instruments, experiments, science",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    python_requires=">=3.7",
    install_requires=["pyserial==3.4"],
    dependency_links=[],
    project_urls={
        "Bug Reports": "https://github.com/luizribeiro/labctl/issues",
        "Source": "https://github.com/luizribeiro/labctl/",
    },
)
