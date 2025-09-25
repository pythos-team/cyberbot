from setuptools import setup, find_packages

setup(
    name="cyberbot",
    version="0.1.1",
    description="CyberBot: a Flask companion that keeps routes alive and adds basic cyber-aware helpers.",
    author="Alex Austin",
    packages=find_packages(),
    install_requires=["Flask", "pycryptodome", "cryptography"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Framework :: Flask",
    ],
)