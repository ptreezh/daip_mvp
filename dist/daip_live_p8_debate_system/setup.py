from setuptools import setup, find_packages

setup(
    name="daip-live-p8_debate_system",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.7.4,<3.0.0",
    ],
)