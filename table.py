#!/usr/bin/python3

import re, types

class StrMatch:
    def __init__(self, match):
        self.m=match
    def __getattr__(self, name):
        return getattr(self.m, name)
    def __repr__(self):
        return repr(self.m.group(0))
    def __str__(self):
        return self.m.group(0)

def Matcher(regexstr, constr=lambda a:a):
    regex=re.compile(regexstr, re.ASCII)
    def match(string):
        m=regex.match(string)
        assert m, "%s does not match %s" % (string, regexstr)
        #m.str=types.MethodType(lambda self: self.group(0), m)
        return constr(StrMatch(m))
    return match

def StrRepr(obj):
    if type(obj)==re.Match:
        return obj.group(0)
    else:
        return str(obj)


class Table:

    def __init__(self, filename):
        self.__try_run__(self.__parse_keys__, filename, "field descriptions")

    def __try_run__(self, method, filename, task, *args, **kwargs):
        self.lastline=None
        self.lineno=0
        try:
            method(filename, *args, **kwargs)
        except BaseException as be:
            raise SyntaxError("Error parsing %s in file %s, line %d \n  %s\n --> %s"
                              %(task, filename, self.lineno, self.lastline, repr(be))) from be

    def __parse_keys__(self, filename):
        fieldre=re.compile("#%\s*(\S+)\s*!\s*([^!]*?)\s*!\s*(KEY)?\s*(\w[.]\w)?\s*(#.*)?", re.ASCII) 
        self.fields={}
        self.bykey={}
        self.constraints={}
        self.filename=filename
        f=open(filename)
        for lineno, l in enumerate(f):
            if l.startswith("#%"):
                m=fieldre.match(l.rstrip())
                self.lineno=lineno
                self.lastline=l.rstrip()
                assert m, "Invalid field description"
                field, fun, iskey, constraint, comment=m.groups()
                fun=eval(fun) # this may raise
                if type(fun)==str:
                    fun=Matcher(fun)
                assert not field in self.fields, "Non-unique field name %s"%field
                self.fields[field]=fun
                if iskey:
                    self.bykey[field]={}
                if constraint:
                    self.constraints[key]=constraint
        self.lines=[]
    
    def read(self, filename=None):
        if not filename:
            filename=self.filename
        self.__try_run__(self.__read_impl__, filename, "table contents")

    def __read_impl__(self, filename):
        f=open(filename)
        for lineno, l in enumerate(f):
            self.lineno=lineno
            self.lastline=l.rstrip()
            if l.startswith("#"):
                continue
            items=list(map(lambda s:s.strip(), l.split(":")))
            parsed={}
            assert len(self.fields) == len(items),\
                    "Number of line items do not match, expected %d, got %d" \
                    % (len(self.fields), len(items))
            for (field, fun), inp in zip(self.fields.items(), items):
                parsed[field]=fun(inp)
            self.lines.append(parsed)
            print(parsed)
            for keyname, keydict in self.bykey.items():
                key=str(parsed[keyname])
                assert not key in keydict, "Non-unique key %s"%parsed[keyname]
                keydict[key]=self.lines[-1]
    def dump(self):
        for l in self.lines:
            print(l)


