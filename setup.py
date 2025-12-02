from setuptools import setup, find_packages

setup(
    name="korefi-commons",
    version="0.3.1",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "tenacity",
        "googleapis-common-protos>=1.63.0",
    ],
    extras_require={
        "dev": ["pytest", "django>=4.0"],
        "django": ["django>=4.0"],
    },
    setup_requires=["setuptools>=42", "wheel"],
    author="KoreFi",
    description="Common utilities for KoreFi projects",
    python_requires=">=3.9",
)
