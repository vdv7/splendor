import collections

types = ['w', 'k', 'r', 'g', 'b']

Card = collections.namedtuple('Card', ['level', 'bonus', 'points',
                                       'k', 'w', 'r', 'b', 'g'])

template = {
    1: [[0,1,0,2,2, 0],
        [0,1,2,0,0, 0],
        [0,1,1,1,1, 0],
        [0,0,0,0,3, 0],
        [0,0,0,2,2, 0],
        [0,1,1,2,1, 0],
        [3,1,0,0,1, 0],
        [0,0,0,4,0, 1],
        ],
    2: [[0,2,2,3,0, 1],
        [2,0,3,0,3, 1],
        [0,2,4,1,0, 2],
        [0,0,5,0,0, 2],
        [0,3,5,0,0, 2],
        [6,0,0,0,0, 3],
        ],
    3: [[0,3,5,3,3, 3],
        [0,7,0,0,0, 4],
        [3,6,3,0,0, 4],
        [3,7,0,0,0, 5],
        ],
    }

def generate():
    cards = []
    for i, color in enumerate(types):
        for level, templ in template.items():
            for data in templ:
                c = Card(level=level, bonus=color, points=data[5],
                         w=data[(0+i)%5],
                         k=data[(1+i)%5],
                         r=data[(2+i)%5],
                         g=data[(3+i)%5],
                         b=data[(4+i)%5])
                cards.append(c)
    return cards





