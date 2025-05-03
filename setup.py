from setuptools import setup, find_packages

setup(
    name="publisher",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-docx",
        "PyPDF2",
        "openai",
        "pillow",
        "requests",
        "reportlab",
        "weasyprint",
        "fpdf2",
        "ebooklib",
        "pyyaml",
        "argparse",
    ],
    entry_points={
        "console_scripts": [
            "publisher=publisher.cli:main",
        ],
    },
    author="Publisher Team",
    description="Auto Publisher for children's books and SEND materials",
    python_requires=">=3.8",
)
