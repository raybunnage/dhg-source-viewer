from setuptools import setup, find_packages

setup(
    name="dhg-source-viewer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # List your project dependencies here
        "supabase",
        "python-dotenv",
        "streamlit",
    ],
)

# Then install with: pip install -e .
