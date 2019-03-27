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
    version="0.2.8",
    packages=find_packages(),
    license="MIT",
    long_description=open("README.md").read(),
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
)
