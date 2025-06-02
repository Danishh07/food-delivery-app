import sys
print(sys.path)
try:
    import requests
    print('Requests module found')
except ImportError:
    print('Requests module missing')
