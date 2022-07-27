from setuptools import find_packages, setup

requirements = [
    "cachetools~=4.2.1",
    "python-consul~=1.0",
    "redis>=2.10.6,<5",
    "thrift~=0.13",
    "boto3~=1.9",
    "pyee~=6.0",
]


setup(
    name="flipper-client",
    version="1.3.0",
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
            "ipython",
            "thrift",
            "setuptools",
            "wheel",
            "ipdb",
            "black==22.1.0",
            "pre-commit",
            "isort",
            "flake8",
            "mypy",
            "moto",
            "bandit",
            "twine",
            "testing.postgresql",
        ],
    },
    classifiers=["License :: OSI Approved :: Apache Software License"],
)
