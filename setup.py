"""
Flask-Handler
-------------

Inheritable request handlers for Flask (Webapp inspired)

Links
`````

* `documentation <http://packages.python.org/Flask-Handler>`_
* `development version
  <http://github.com/kijun/flask-handler/zipball/master#egg=Flask-Handler-dev>`_

"""
from setuptools import setup


setup(
    name='Flask-Handler',
    version='0.1',
    url='http://github.com/kijun/flask-handler',
    license='BSD',
    author='Kijun Seo',
    author_email='m@kijun.co',
    description='Inheritable request handlers for Flask (Webapp inspired)',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
