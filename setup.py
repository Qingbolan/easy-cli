from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="silantui",
    version="0.1.1",
    author="Silan Hu",
    author_email="contact@silan.tech",
    description="A modern Terminal UI Framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Qingbolan/silantui",
    project_urls={
        "Homepage": "https://silan.tech",
        "Documentation": "https://github.com/Qingbolan/easy-cli",
        "Source": "https://github.com/Qingbolan/easy-cli",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
        "pyfiglet>=0.8.0",
        "openai>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
            "openai>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "silantui=silantui.cli:main",
        ],
    },
)
