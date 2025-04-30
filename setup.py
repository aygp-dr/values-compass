from setuptools import setup, find_packages

setup(
    name="values_explorer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "datasets>=2.9.0",
        "huggingface-hub>=0.12.0",
        "matplotlib>=3.5.0",
        "networkx>=2.7.0",
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "seaborn>=0.11.0",
        "torch>=1.10.0",
        "transformers>=4.15.0",
    ],
    author="Aidan Pace",
    author_email="apace@defrecord.com",
    description="A toolkit for exploring the Anthropic Values-in-the-Wild dataset",
    keywords="ai, ethics, values, anthropic, nlp",
    url="https://github.com/aidanpace/values-compass",
)
