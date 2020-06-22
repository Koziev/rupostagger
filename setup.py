import io
import setuptools

#with io.open("README.md", mode="r", encoding='utf-8') as fh:
#    long_description = fh.read()

setuptools.setup(
    name="rupostagger",
    version="0.0.74",
    author="Ilya Koziev",
    author_email="inkoziev@gmail.com",
    description="Part-of-Speech Tagger for Russian language",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    url="https://github.com/Koziev/rupostagger",
    packages=setuptools.find_packages(),
    package_data={'rupostagger': ['rupostagger.config', 'rupostagger.model']},
    include_package_data=True,
   
)
