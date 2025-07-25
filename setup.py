"""Setup script for AUX Protocol."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aux-protocol",
    version="0.1.0",
    author="AUX Protocol Contributors",
    description="Agent UX Layer - Semantic interface protocol for AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aux-protocol/aux-protocol",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "selenium>=4.15.0", 
        "pydantic>=2.0.0",
        "asyncio-mqtt>=0.13.0",
        "websockets>=11.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aux-server=aux_protocol.server:main",
        ],
    },
)