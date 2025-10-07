from setuptools import setup, find_packages

setup(
    name='project_nexus_client',
    version='0.1.0',
    description='Python client SDK (skeleton) for Project Nexus core API',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests>=2.28.0'
    ],
    python_requires='>=3.8',
)
