#!/usr/bin/python3
# -*- coding: utf-8 -*-
#print("content-Type: text/plain\n")

import cgi, cgitb

# cgitb.enable()
storage = cgi.FieldStorage()
print('Content-Type: text/html\n')
print('Status: 200 OK')
# data = storage.getvalue('data')
# recieve = data + ":Success!"
# print(recieve)