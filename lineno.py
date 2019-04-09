from __future__ import print_function

from inspect import currentframe, getframeinfo

frameinfo = getframeinfo(currentframe())

print(frameinfo.filename, frameinfo.lineno)
