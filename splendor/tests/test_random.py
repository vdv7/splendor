import random

import splendor

def test_random():
    for n_players in [2, 3, 4]:
        for seed in range(100):
            game = splendor.Splendor(n_players=n_players, seed=seed)

            rng = random.Random()
            rng.seed(1)
            while game.winners is None:
                p = game.players[game.current_player]
                actions = p.valid_actions()
                if len(actions) == 0:
                    game.pass_turn()
                else:
                    func, args = rng.choice(actions)
                    #print(game.current_player, func.__name__, args)
                    func(**args)
        

