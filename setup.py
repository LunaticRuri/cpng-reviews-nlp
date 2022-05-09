from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='cpng-reviews-nlp',
      version='1.0.0',
      description='CPNG reviews analysis using nlp',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Team_10',
      # author_email='',
      keywords=['Coopang', 'NLP'],
      url='https://github.com/LunaticRuri/cpng-reviews-nlp',
      license='MIT',
      py_modules=['packageTest'],
      install_requires=[],
      packages=find_packages(),
      python_requires='>=3',
      )
