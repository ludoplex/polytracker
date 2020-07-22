from setuptools import setup, find_packages

setup(
    name='polytracker',
    description='API and Library for operating and interacting with PolyTracker',
    url='https://github.com/trailofbits/polytracker',
    author='Trail of Bits',
    version="0.1.0",
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'graphviz',
        'matplotlib',
        'networkx',
        'pygraphviz',
        'pydot',
        'tqdm',
        'typing_extensions'
    ],
    extras_require={
        "dev": ["black", "mypy", "pytest"]
    },
    entry_points={
        'console_scripts': [
            'polyprocess = polytracker.polyprocess.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
    ]
)
