from setuptools import setup, find_packages

setup(
name="axomosint",
version="1.0.0",
description="OSINT email checker tool by Axom",
author="Axom",
author_email="axom@protonmail.com",
packages=find_packages(),
include_package_data=True,
install_requires=[
"httpx",
"trio",
"beautifulsoup4",
"termcolor"
],
entry_points={
"console_scripts": [
"axomosint=axomosint.main:main"
]
},
python_requires=">=3.8",
)
