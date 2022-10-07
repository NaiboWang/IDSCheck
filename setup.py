import setuptools
from setuptools.command.install_scripts import install_scripts


# class InstallScripts(install_scripts):

#     def run(self):
#         setuptools.command.install_scripts.install_scripts.run(self)

#         # Rename some script files
#         for script in self.get_outputs():
#             if basename.endswith(".py") or basename.endswith(".sh"):
#                 dest = script[:-3]
#             else:
#                 continue
#             print("moving %s to %s" % (script, dest))
#             shutil.move(script, dest)


with open("README.md", "r",  encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="idscheck",
    version="1.0.1",
    author="Naibo Wang",
    author_email="naibowang@foxmail.com",
    description="A command line tool for IDS student to check GPU allocation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NaiboWang/IDSCheck",
    packages=setuptools.find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'ids = idscheck.idscheck:cmd',
            'idsgpu = idscheck.idscheck:gpu',
            'idstop = idscheck.idscheck:top',
            'idstopall = idscheck.idscheck:topall',
            'idsquery = idscheck.idscheck:query',
        ],
    },
)
