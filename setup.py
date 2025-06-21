from setuptools import setup, find_packages

setup(
    name='photosynthesisai',
    version='0.1',
    package_dir={"": "src"},             # <--- THIS tells setuptools to look in src/
    packages=find_packages(where="src"), # <--- THIS finds packages inside src/
    install_requires=[
        "numpy",
        # ... add others as needed
    ],
)
