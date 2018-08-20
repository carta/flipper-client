from setuptools import find_packages, setup


requirements = [
    'fakeredis~=0.11.0',
    'lru-ttl~=0.0.6',
    'python-consul~=1.0.1',
    'redis~=2.10.6',
    'thrift~=0.11.0',
]


setup(
    name='flipper-client',
    version='0.1.0',
    packages=find_packages(),
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest~=3.6.2',
            'ipython',
            'thrift',
            'cloudsmith-cli',
            'setuptools',
            'wheel',
        ],
    },
)
