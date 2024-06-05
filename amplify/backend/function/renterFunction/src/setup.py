from setuptools import setup, find_packages

setup(
    name='paymentFunction',
    version='1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'boto3',
        'mysql-connector-python',
        'botocore',
    ],
)
