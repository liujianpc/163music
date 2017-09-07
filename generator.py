
def gen():
    for x in xrange(4):
        yield x

g = gen()
for x in g:
    print x