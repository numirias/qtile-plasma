from setuptools import setup

setup(
    name='qtile-plasma',
    packages=['plasma'],
    version='1.5.4',
    description='A flexible, tree-based layout for Qtile',
    author='numirias',
    author_email='numirias@users.noreply.github.com',
    url='https://github.com/numirias/qtile-plasma',
    license='MIT',
    python_requires='>=3',
    install_requires=['xcffib>=0.5.0', 'qtile>=0.14.2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Desktop Environment :: Window Managers',
    ],
)
