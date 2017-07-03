import time
#from pyshorteners import Shortener

token = '317025779:AAFLih4bH_BjKIm8_giC-wD1geEd8d_tLCI'
goRegister = False

'''
def shorten(url):
    api_key = 'AIzaSyAhJBP72yUB84wr2pEBuGgYpC0ir4-Z1IM'
    shortener = Shortener('Google', api_key=api_key)
    print("My short url is {}".format(shortener.short(url)))
    return shortener.short(url)
'''


def log(**kwargs):
    try:
        log.logs += 1
        print("IN LOG!!!")
    except AttributeError:
        log.logs = 0
    res = '-----------------------------------------------------------\n'
    res += 'Log#' + str(log.logs) + ' at ' + str(time.asctime(time.localtime(time.time()))) + '\n'
    for i in range(len(kwargs)):
        ln = list(kwargs.popitem())
        res += str(ln[0]) + " : " + str(ln[1]) + '\n'
    print(res)
