from setuptools import setup

with open("torosmanager/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            _, _, _version = line.replace('"', "").split()
            break

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="torosmanager",
    version=_version,
    description="TOROS Automation System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TOROS Dev Team",
    # author_email="toros@utrgv.edu",
    url="https://toros.utrgv.edu",
    packages=["torosmanager"],
    install_requires=["pyyaml", "pony", "ccdproc"],
    entry_points={
        "console_scripts": ["inittorosdb = torosmanager:init_database",]
    },
    test_suite="tests",
)
