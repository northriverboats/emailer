import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="emailer",
    version="1.0.0",
    author="Fredrick W. Warren",
    author_email="fredw@northriverboats.com",
    description="an email wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/northriverboats/emailer,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
