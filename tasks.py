import errno
import os

from invoke import task
import sassc

SASS = 'pythonsd/sass/pythonsd.scss'
CSS_DIR = 'pythonsd/static/css'


@task
def build():
    compile_sass()
    print('Compiled css: {}'.format(CSS_DIR))


def compile_sass():

    try:  # ensure destination directory exists
        os.makedirs(CSS_DIR)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    sassc.main(argv=[
        'sassc', SASS,
        '{css_dir}/pythonsd.css'.format(css_dir=CSS_DIR),
        '--output-style=compressed',
    ])
