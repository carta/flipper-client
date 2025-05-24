from setuptools import find_packages, setup

requirements = [
    "cachetools>=4.2.1,<6",
    "python-consul~=1.0",
    "redis>=2.10.6,<5",
    "thrift~=0.13",
    "boto3~=1.9",
    "pyee~=6.0",
]


setup(
    name="flipper-client",
    version="1.3.2",
    packages=find_packages(),
    license="Apache License 2.0",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require={
        "postgres": ["psycopg~=3.0.10"],
        "dev": [
            "six>=1.12",
            "fakeredis~=1.0",
            "pytest~=7.1.0",
            "ipython~=8.0",
            "thrift~=0.22",
            "setuptools",
            "wheel",
            "ipdb",
            "black==22.1.0",
            "pre-commit",
            "isort~=6.0",
            "flake8~=7.2",
            "mypy~=1.0",
            "moto~=4.2",
            "bandit~=1.8",
            "twine~=6.1",
            "testing.postgresql",
        ],
    },
    classifiers=["License :: OSI Approved :: Apache Software License"],
)
