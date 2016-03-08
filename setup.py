from codecs import open as codecs_open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(name='flask-ldap3',
      version='0.0.1',
      description=u"flask-ldap3",
      long_description='ldap3 flask example',
      classifiers=[],
      keywords='',
      author=u"Jaime Viloria",
      author_email='jaimeviloria@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'flask',
          'requests',
          'ldap3'
      ],
      extras_require={
          'test': ['pytest'],
      },
      entry_points="""
      [console_scripts]
      flask_ldap3=app:run
      """
      )
