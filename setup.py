from setuptools import setup, find_packages


def readme():
    return open('README.md', 'r').read()


setup(
    name="smooth_logger",
    version="0.2.1",
    author="Murdo Maclachlan",
    author_email="murdomaclachlan@duck.com",
    description=(
        "A simple logger made primarily for my own personal use. Made from a combination of"
        + " necessity and so much sloth that it overflowed into productivity."
    ),
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MurdoMaclachlan/smooth_logger",
    packages=find_packages(),
    install_requires=[
        "plyer",
        "smooth_progress"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    license='AGPLv3+'
)
