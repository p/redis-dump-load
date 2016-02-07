import nose.plugins.skip
import functools
import sys

try:
    import ijson as ijson_root
    have_ijson = True
except ImportError:
    have_ijson = False

py3 = sys.version_info[0] == 3

# python 2/3 compatibility
if py3:
    # borrowed from six
    def b(s):
        '''Byte literal'''
        return s.encode("latin-1")
    def u(s):
        '''Text literal'''
        return s
else:
    # borrowed from six
    def b(s):
        '''Byte literal'''
        return s
    # Workaround for standalone backslash
    def u(s):
        '''Text literal'''
        return unicode(s.replace(r'\\', r'\\\\'), "unicode_escape")

# backport for python 2.6
def get_subprocess_check_output():
    import subprocess

    try:
        check_output = subprocess.check_output
    except AttributeError:
        # backport from python 2.7
        def check_output(*popenargs, **kwargs):
            if 'stdout' in kwargs:
                raise ValueError('stdout argument not allowed, it will be overridden.')
            process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
            output, unused_err = process.communicate()
            retcode = process.poll()
            if retcode:
                cmd = kwargs.get("args")
                if cmd is None:
                    cmd = popenargs[0]
                raise subprocess.CalledProcessError(retcode, cmd, output=output)
            return output

    return check_output

def with_temp_dir(fn):
    import tempfile
    import shutil
    import functools

    @functools.wraps(fn)
    def decorated(self, *args, **kwargs):
        dir = tempfile.mkdtemp()
        try:
            return fn(self, dir, *args, **kwargs)
        finally:
            shutil.rmtree(dir)

    return decorated

def requires_ijson(fn):
    @functools.wraps(fn)
    def decorated(*args, **kwargs):
        if not have_ijson:
            raise nose.plugins.skip.SkipTest('ijson is not present')
        return fn(*args, **kwargs)
    return decorated
