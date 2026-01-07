from setuptools import setup, find_packages

setup(
    name="borken-chess-v2",
    version="1.0.0",
    description="Borken Chess V2 - specialized blitz chess engine for chess.com",
    author="Borken Chess",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "chess==1.10.0",
        "requests==2.31.0",
        "selenium==4.15.2",
        "python-dotenv==1.0.0",
        "pydantic==2.5.0",
        "aiohttp==3.9.1",
    ],
)
