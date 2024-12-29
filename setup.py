from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stagehand-py",
    version="0.1.2",
    author="BrowserBase",
    author_email="support@browserbase.io",
    description="Python SDK for Stagehand",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/browserbase/stagehand-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "httpx>=0.24.0",
        "asyncio>=3.4.3",
        "python-dotenv>=1.0.0",
        "pydantic>=1.10.0",
    ],
) 