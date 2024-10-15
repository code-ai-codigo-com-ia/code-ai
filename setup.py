from setuptools import setup, find_packages

setup(
    name='codeai',
    version='0.1.0',
    description='CLI para interação com a API da OpenAI',
    author='codeai-brasil',
    author_email='codeai-brasil@proton.me',
    packages=find_packages(),
    install_requires=[
        'openai',
        'click',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'codeai=codeai.cli:main',
        ],
    },
)
