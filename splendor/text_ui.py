import random

import splendor


colors = 'kwrgb'

def text_game_state(game):
    rows = []
    n = ''.join('%14s' % text_noble(n) for n in game.nobles)
    rows.append(n)
    rows.append('-'*76)
    for level in [3, 2, 1]:
        lev = ''.join('%19s' % text_card(c) for c in game.tableau[level])
        rows.append(lev)
    rows.append('-'*76)

    chips = []
    for c in colors+'x':
        chips.append('%d%s' % (game.chips[c], c))
    rows.append('  '.join(chips))
    rows.append('='*76)



    for i, p in enumerate(game.players):
        current = '*' if game.current_player == i else ' '
        chip_info = []
        for c in colors:
            bonus = p.bonus[c]
            chips = p.chips[c]
            if bonus > 0:
                if chips > 0:
                    chip_info.append('%d[+%d]%s' % (chips, bonus, c))
                else:
                    chip_info.append('[+%d]%s' % (bonus, c))
            else:
                chip_info.append('%d%s' % (chips, c))
        if p.chips['x'] > 0:
            chip_info.append('%dx' % (p.chips['x']))
        if len(p.reserve) > 0:
            reserve = ' '.join(text_card(c) for c in p.reserve)
        else:
            reserve = ''
        if len(p.nobles) > 0:
            nobles = ' '.join(text_noble(n) for n in p.nobles)
        else:
            nobles = ''

        rows.append('%sP%d [%d] %s %s %s' % (current, i, p.points, 
                                            ':'.join(chip_info), nobles, reserve))

    return '\n'.join(rows)

def text_noble(noble):
    cost = []
    for c in colors:
        v = getattr(noble, c)
        if v > 0:
            cost.append('%d%s' % (v, c))
    return '[%d](%s)' % (noble.points, ':'.join(cost))


def text_card(card):
    points = '+%d' % card.points if card.points > 0 else ''

    cost = []
    for c in 'kwrgb':
        v = getattr(card, c)
        if v > 0:
            cost.append('%d%s' % (v, c))

    return '[%s%s](%s)' % (card.bonus, points, ':'.join(cost))

def text_action(func, args):
    name = func.__name__
    if name == 'draw_three':
        return 'Draw Three: %s %s %s' % tuple(args.keys())
    elif name == 'draw_two':
        return 'Draw Two: %s' % args['color']
    elif name == 'reserve_card':
        return 'Reserve: %s' % text_card(args['card'])
    elif name == 'play':
        return 'Play: %s' % text_card(args['card'])
    else:
        return name, args

def run(n_players, seed=None):
    game = splendor.Splendor(n_players=n_players, seed=seed)

    while game.winners is None:
        print(text_game_state(game))

        p = game.players[game.current_player]
        actions = p.valid_actions()

        if len(actions) == 0:
            game.pass_turn()
        else:
            for i, action in enumerate(actions):
                print('%3d: %s' % (i, text_action(*action)))
            choice = input('>>')
            if choice == 'r':
                c = random.randrange(len(actions))
            else:
                c = int(choice)
            func, args = actions[c]
            func(**args)

    print(text_game_state(game))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Splendor')
    parser.add_argument('--n_players', type=int, default=2, help='number of players')
    parser.add_argument('--seed', type=int, default=None, help='random number seed')
    args = parser.parse_args()

    run(args.n_players, args.seed)

