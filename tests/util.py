import sys

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

def broken_on_python_3(issue_url):
    if py3:
        import nose.plugins.skip
        import functools

        def decorator(fn):
            @functools.wraps(fn)
            def decorated(*args, **kwargs):
                raise nose.plugins.skip.SkipTest('Broken on Python 3: %s' % issue_url)
            return decorated
    else:
        def decorator(fn):
            return fn
    return decorator
