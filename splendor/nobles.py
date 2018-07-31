import collections

types = ['w', 'k', 'r', 'g', 'b']

Noble = collections.namedtuple('Noble', ['points',
                                       'k', 'w', 'r', 'b', 'g'])

template = [[3,3,3,0,0, 3],
            [4,4,0,0,0, 3],
           ]

def generate():
    nobles = []
    for i, color in enumerate(types):
        for data in template:
            n = Noble(points=data[5],
                      w=data[(0+i)%5],
                      k=data[(1+i)%5],
                      r=data[(2+i)%5],
                      g=data[(3+i)%5],
                      b=data[(4+i)%5])
            nobles.append(n)
    return nobles





