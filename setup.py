import setuptools

with open("README", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nitc-fwd-astroanax",
    version="0.0.1",
    author="Rehan Tadpatri",
    author_email="astroanax@outlook.com",
    description="nitc firewall login daemon/cli",
    long_description=long_description,
    long_description_content_type="text/plain",
    url="https://github.com/astroanax/nitc-fwd.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "nitc-fwd = nitc_fwd.__main__:main",
        ],
    },
    install_requires=["requests"],
)
