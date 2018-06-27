from setuptools import setup


requirements = [
    'fakeredis~=0.11.0',
    'py-lru-cache~=0.1.4',
    'python-consul~=1.0.1',
    'redis~=2.10.6',
]


setup(
    name='flipper',
    version='0.0.1',
    packages=['flipper', 'flipper_thrift'],
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest~=3.6.2',
            'ipython',
            'thrift',
        ],
    },
)
