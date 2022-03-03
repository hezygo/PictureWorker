from setuptools import setup

setup(
    name='zrpc',
    version='0.0.1',
    packages=['zrpc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyzmq',
    ],
)