# -*- coding: utf-8 -*-

# Copyright © 2013 Pietro Battiston <me@pietrobattiston.it>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
This is a simple incremental json parser. It relies on other parsers for the
real operation: all it does is to read the "key : value" pairs one at a time
and call the parser separately on each of them. It may hence be slower than the
original parser, but it allows to process json strings which represent a very
large number of objects (compared to the available RAM), or to parse json
streams without waiting for the end of their transmission.
"""

from __future__ import print_function

try:
    import json
except ImportError:
    import simplejson as json

BUF_LEN = 100
STRIP_CHARS = set((' ', '\n', '\t'))
DELIMITERS = {'{' : '}',
              '[' : ']',
              '"' : '"'}

STATES_LIST = ["STARTING",
               "BEFORE_KEY",
               "INSIDE_KEY",
               "AFTER_KEY",
               "BEFORE_VALUE",
               "INSIDE_VALUE",
               "AFTER_VALUE",
               "FINISHED"]

exec(",".join(STATES_LIST) + "= range(%d)" % len(STATES_LIST))
STATES = dict(zip(range(len(STATES_LIST)), STATES_LIST))

DEBUG = False

def _debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)
    else:
        pass

def loads(file_obj):
    """
    This generator reads and incrementally parses file_obj, yielding each
    key/value pair it parses as a tuple (key, value).
    """
    state = STARTING

    same_buf = False
    
    open_delimiters = []
    
    escape = False
    
    cursor = -1
    buf = ''
    
    while state != FINISHED:
        if cursor == len(buf)-1:
            new_buf = file_obj.read(BUF_LEN)
            assert(new_buf), ("Premature end (current processing buffer ends"
                              " with '%s')" % buf)
            
            buf += new_buf

        cursor += 1
        char = buf[cursor]
        
        _debug("Parse \"%s\" with state %s,"
               " open delimiters %s..." % (char,
                                           STATES[state],
                                           open_delimiters),
              end="")
        
        old_state = state

            
        if state == STARTING:
            if char == '{':
                state = BEFORE_KEY
        
        elif state == BEFORE_KEY:
            if char == '"':
                obj_start = cursor
                state = INSIDE_KEY
        
        elif state == INSIDE_KEY:
            if char == '"':
                state = AFTER_KEY
        
        elif state == AFTER_KEY:
            if char == ':':
                state = BEFORE_VALUE
        
        elif state == BEFORE_VALUE:
            if char in DELIMITERS:
                state = INSIDE_VALUE
                open_delimiters.append(char)
        
        elif state == INSIDE_VALUE:
            if open_delimiters[-1] == '"':
                if escape:
                    escape = False
                    continue
                elif char == '\\':
                    escape = True
                    continue
                elif char != '"':
                    continue
                
            # Since we are INSIDE_VALUE, there is at least an open delimiter.
            if char == DELIMITERS[open_delimiters[-1]]:
                open_delimiters.pop()
                if not open_delimiters:
                    state = AFTER_VALUE
                    json_chunk = "{%s}" % buf[obj_start:cursor+1]
                    _debug("Parse key/value pair '%s'" % json_chunk)
                    
                    try:
                        json_obj = json.loads(json_chunk)
                    except:
                        print("Problem with key/value pair '%s'" % json_chunk)
                        raise
                    yield json_obj.popitem()
                    del obj_start
                    buf = buf[cursor:]
                    cursor = 0
            elif char in DELIMITERS:
                open_delimiters.append(char)
        
        elif state == AFTER_VALUE:
            if char == ',':
                state = BEFORE_KEY
            elif char == '}':
                state = FINISHED
        
        else:
            assert(state == FINISHED)
        
        # Unless there are whitespaces and such, all "non-content" states last
        # just 1 char.
        if state == old_state and not state in (INSIDE_KEY, INSIDE_VALUE):
            assert(char in STRIP_CHARS), ("Found char '%s' in %s while"
                              " parsing '%s'" % (char, STATES[old_state], buf))
        
        _debug("... to state %s" % (STATES[state]))
