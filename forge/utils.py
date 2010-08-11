def renumerate(collection):
    for index in xrange(len(collection) - 1, -1, -1):
        yield (index, collection[index])
