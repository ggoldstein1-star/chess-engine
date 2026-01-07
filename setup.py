from setuptools import setup, find_packages

setup(
    name="chess-engine-blitz",
    version="1.0.0",
    description="A specialized chess engine for blitz chess on chess.com",
    author="Chess Engine",
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
