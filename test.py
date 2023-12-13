#!/usr/bin/python3

from table import Table

t=Table("modules.csv")
t.read()
t.dump()

