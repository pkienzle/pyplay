#!/usr/bin/env python

import ftplib
import os.path

def ftp_fetch(host,source,target,resume=False):
    source_path,source_file = os.path.split(source)

    server = ftplib.FTP(host)
    server.login() # uses anonymous
    #print source_path
    server.cwd(source_path)
    #server.retrlines('LIST')

    target_path,target_file = os.path.split(target)
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    if resume:
        fid = open(target,"ab")
        rest = fid.tell()
    else:
        fid = open(target,"wb")
        rest = 0

    #print 'RETR '+source_file
    try:
        server.retrbinary('RETR '+source_file, 
                          lambda block: fid.write(block), 
                          rest=rest)
    finally:
        fid.close()
        server.close()

def ftp_fetch_using_urllib(host, source, target):
    server = urllib.openurl('ftp://'+host+source)
    data = server.read()
    server.close()

    target_path,target_file = os.path.split(target)
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    fid = open(target,"wb")
    fid.write(data)
    fid.close()
