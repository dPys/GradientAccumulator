import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="GradientAccumulator",
    version="0.1.0",
    author="André Pedersen",
    author_email="andrped94@gmail.com",
    description="Package for gradient accumulation in TensorFlow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andreped/GradientAccumulator",
    packages=setuptools.find_packages(),
    install_requires=[
        'tensorflow',
        'tensorflow-addons'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
)