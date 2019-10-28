from setuptools import find_packages, setup

requirements = [
    "fakeredis~=0.11.0",
    "lru-ttl~=0.0.6",
    "python-consul~=1.0.1",
    "redis~=2.10.6",
    "thrift~=0.11.0",
    "boto3~=1.9.83",
]


setup(
    name="flipper-client",
    version="1.0.4",
    packages=find_packages(),
    license="Apache License 2.0",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest~=3.6.2",
            "ipython",
            "thrift",
            "setuptools",
            "wheel",
            "ipdb",
            "black==18.6b4",
            "pre-commit",
            "isort",
            "flake8",
            "mypy",
            "moto",
            "bandit",
            "twine",
        ]
    },
    classifiers=["License :: OSI Approved :: Apache Software License"],
)
