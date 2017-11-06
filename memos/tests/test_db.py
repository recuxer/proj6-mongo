"""
author: john nemeth
sources: class material, previous testcases
description: test for database functions
"""
import db
from db import enterinDB, removefromDB, getmemos
import arrow
import nose

#tests for correct sorting order of memos (by date)
def test_datesort():
    testrecords = db.getmemos()
    prevdate = arrow.get(2000, 1, 1)
    for record in testrecords:
        recorddate = arrow.get(record['date'])
        if prevdate:
            assert prevdate < recorddate
        prevdate = recorddate

