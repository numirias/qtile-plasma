from setuptools import setup

setup(
    name='qtile-plasma',
    packages=['plasma'],
    version='1.0.1',
    description='An advanced, flexible layout for Qtile',
    author='numirias',
    author_email='numirias@users.noreply.github.com',
    url='https://github.com/numirias/qtile-plasma',
    license='MIT',
    python_requires='>=3',
    install_requires=['xcffib', 'qtile'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Desktop Environment :: Window Managers',
    ],
)
