from setuptools import setup, find_packages

setup(
    name='axomicosint',
    version="2.0",
    packages=find_packages(),
    author="Axom",
    author_email="axom@protonmail.com",
    install_requires=["termcolor", "bs4", "httpx", "trio", "tqdm", "colorama"],
    description="Axomic OSINT - Email reconnaissance tool to check if an email is registered on various online platforms.",
    include_package_data=True,
    url='https://github.com/Axom/axomicosint',
    entry_points={'console_scripts': ['axomicosint = axomicosint:main']},
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
