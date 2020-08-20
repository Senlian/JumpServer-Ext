#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


status='200 ok'
print(status[:3].isdigit())
print(status[3] ==' ')
print(len(status)>=4)
assert len(status)>=4, "Status must be at least 4 characters"