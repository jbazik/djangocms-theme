from setuptools import find_packages, setup
from djangocms_theme import __version__

setup(name='djangocms-theme',
    version=__version__,
    packages=find_packages(),
    provides = ['djangocms_theme'],
    include_package_data = True,
    license = 'BSD',
    description='Per-page themes for django-cms',
    author='John Bazik',
    author_email='jsb@cs.brown.edu',
    url='http://github.com/jbazik/djangocms-theme',
    install_requires = [
        'Django>=1.8',
        'django-cms>=3.0',
        'Pillow',
        'html5lib<=0.9999999',
    ],
    test_suite = 'djangocms_theme.tests.test_models',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
    ],
)
