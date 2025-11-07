from setuptools import setup, find_packages

setup(
    name="daip-live-p4_role_manager_tools",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.7.4,<3.0.0",
    ],
)