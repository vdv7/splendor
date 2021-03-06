#Splendor STAP interface



import random,json
import splendor

try: input=raw_input
except: pass


COLORS=splendor.game.colors
STAP_COLORS=dict(zip(COLORS+'x',[2,3,4,5,6,7]))

RESERVE='RESERVE'
BUY='BUY'
DRAW2='DRAW TWO OF A SINGLE COLOR'
DRAW3='DRAW THREE DIFFERENT COLORS'



TEMPLATE='''
:root {
--color2: #F5CBA7;
--color3: #ABEBC6;
--color4: #A9CCE3;
--color5: #F5B7B1;
--color6: #FEF9E7;
--color7: linear-gradient(to right, var(--color2), var(--color3), var(--color4), var(--color5), var(--color6));
}
* {font-family:arial narrow}
[v] > div {vertical-align:top}
[level="2"]{display:inline-block}
[id="Public Cards"] [level="2"]{display:block}
[id="Public Cards"] [level="3"]{display:inline-block;}
[id="Public Chips"] [level="2"]{margin-left:15px;vertical-align:middle}
[id="Public Chips"] [level="3"]{display:inline-block;}
[type="boolean"][select="-1"]{
	font-family:impact;
	font-size:11pt;
	min-width:0px;
	padding:2px;
	background:none;
	box-shadow:none;
	color:black;
}
#Nobles [level="2"]{border:solid 1px lightgray;border-radius:5px}
.chip {
	font-size:10pt;
	width:1.5em;
	height:1.5em;
	border-radius:1.5em;
	text-align:center;
	vertical-align:top;
	border:solid 1px gray;
	display:inline-block
}
.production {display:inline-block;border-radius:3px;border:solid 1px lightgray}
.card {width:10em;border-radius:5px}
.actions {position:absolute;top:0px;right:0px}
.actions [type="boolean"] {display:block}
'''


def ui(data): print(json.dumps(data))

def err(e): ui({'error':e})

def text_game_state(game,player,buyable=[],draw2=[],draw3=[]):
	screen=[]
	#players
	players=[]
	for i, p in enumerate(game.players):
		chip_info = []
		for c in COLORS:
			if p.bonus[c]: chip_info.append(text_production(c,p.bonus[c]))
			if p.chips[c]: chip_info.append(text_chip(c,p.chips[c]))
		if p.chips['x'] > 0:
			chip_info.append(text_chip('x',p.chips['x']))
		playerInfo=[{"id":"VP","v":p.points}]
		if chip_info: playerInfo.append({"id":"Resources","v":chip_info})
		if p.nobles: playerInfo.append({"id":"Nobles","v":len(p.nobles)})
		if p.reserve: playerInfo.append({"id":"Reserved","v":len(p.reserve)})
		players.append({"id":"Player %d"%(i+1),
						"emp":int(i==player),
						"v":playerInfo })
	screen.append(players)
	#cards
	reserve=game.players[player].reserve
	allowReserve=len(reserve)<splendor.game.MAX_RESERVED and player==game.current_player
	cardRows=[]
	for level in [3,2,1]:
		cardRows.append([text_card(c,c in buyable,allowReserve) for c in game.tableau[level]])
	if reserve: screen.append({"id":"My Reserved Cards","v":[text_card(c,c in buyable) for c in reserve]})
	screen.append({"id":"Public Cards","v":cardRows})
	#chips
	chips=[text_chip('x',game.chips['x'])]
	#if draw3 or draw2: chips.append({'id':DRAW_CHIPS,'v':False})
	#chips+=[{'id':c,'v':[False,text_chip(c,game.chips[c])]} for c in COLORS+'x' if game.chips[c]]
	chips+=[{'id':c,'title':'','v':[False,text_chip(c,game.chips[c])]} for c in COLORS if game.chips[c]]
	screen.append({"id":"Public Chips","v":chips,'select':2})
	#nobles
	screen.append({"id":"Nobles","v":[text_noble(n) for n in game.nobles]})
	return screen

def text_chip(color,value=None):
	r={'bg':STAP_COLORS[color],'tags':['chip']}
	if value: r['v']=value
	return r

def text_production(color,value=None):
	return {'bg':STAP_COLORS[color],'v':value,"tags":["production"]}

def text_noble(noble):
	cost = []
	for c in COLORS:
		v = getattr(noble, c)
		if v > 0:
			cost.append((v,c))
	return [{"id":"VP","v":noble.points},[text_production(col,num) for num,col in cost]]

def text_card(card,allowBuy,allowReserve=None):
	cost = []
	for c in COLORS:
		v = getattr(card, c)
		if v > 0: cost.append(text_chip(c,v))
	actions=[{'id':BUY,'v':False,'eB':int(allowBuy)}]
	if allowReserve: actions.append({'id':RESERVE,'v':False})
	return {'tags':['card'],'bg':STAP_COLORS[card.bonus],
			'v':[ {'id':"VP",'v':card.points}, {"id":"Cost","v":cost}, {'id':json.dumps(card),'v':actions,'tags':['actions'],'title':''} ]}


def run(n_players, n_random=0, seed=None):
	types = ['player']*n_players + ['random']*n_random
	random.shuffle(types)
	game = splendor.Splendor(n_players=len(types), seed=seed)

	last_actions = []
	
	ui(dict(template=TEMPLATE,patronym=1))
	
	while game.winners is None:
		#grab all potential actions
		actions = game.players[game.current_player].valid_actions()
		input2action={}
		#display for human player
		if types[game.current_player] == 'player':
			player=game.current_player
			if len(actions) == 0:
				game.pass_turn()
			else:
				draw3=[]
				draw2=[]
				buyable=[]
				for func,args in actions:
					if func.__name__=='draw_three':
						draw3.append({'v':[text_chip(c) for c in args.keys()],'e':[40]})
						colors=sorted(args)
						input2action[(DRAW3,tuple(colors))]=func,args
					elif func.__name__=='draw_two':
						draw2.append({'v':[text_chip(args['color']),text_chip(args['color'])],'e':[40]})
						input2action[(DRAW2,args['color'])]=func,args
					elif func.__name__=='reserve_card':
						input2action[(json.dumps(args['card']),RESERVE)]=func,args
					elif func.__name__=='play':
						buyable.append(args['card'])
						input2action[(json.dumps(args['card']),BUY)]=func,args
					else:
						err([func.__name__,args])
				screen=text_game_state(game,player,buyable,draw2,draw3)
				#screen.append({"id":"last actions","v":last_actions})
				ui(None)
				ui(screen)
				selectedColors={}
				while True:
					try:
						choice=json.loads(input())
						c=tuple(choice[1])
						if c in input2action:
							break
						elif c[-1]==DRAW2:
							c=(DRAW2,list(selectedColors.keys())[0])
							break
						elif c[-1]==DRAW3:
							c=(DRAW3,tuple(sorted(selectedColors)))
							break
						elif c[0] in COLORS:
							selectedColors[c[0]]=choice[-1]
							selectedColors={k:v for k,v in selectedColors.items() if v}
							if len(selectedColors)==1 and (DRAW2,list(selectedColors.keys())[0]) in input2action:
								ui([{'$':'Public Chips','v':[{'id':DRAW2,'v':False,'select':-1}]}])
							else:
								ui([{'$':'Public Chips','v':[{'id':DRAW2,'v':None}]}])
							if len(selectedColors)==3:
								ui([{'$':'Public Chips','v':[{'id':DRAW3,'v':False,'select':-1}]}])
							else:
								ui([{'$':'Public Chips','v':[{'id':DRAW3,'v':None}]}])
					except Exception as e:
						err(repr(e))
				func, args = input2action[c]
				func(**args)
				last_actions = []
		#do actions for non-human players
		elif types[game.current_player] == 'random':
			c = random.randrange(len(actions))
			func,args=actions[c]
			#TODO: add last action
			#last_actions.append('Player %d: %s' % (game.current_player, text_action(func, args)))
			func(**args)
	#exit screen
	screen=text_game_state(game,player)
	screen.append('Thank you for playing.')
	ui(None)
	ui(screen)


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Splendor')
	parser.add_argument('--n_random', type=int, default=random.randrange(1,4), help='number of random AI players')
	parser.add_argument('--seed', type=int, default=None, help='random number seed')
	args = parser.parse_args()

	run(n_players=1, n_random=args.n_random, seed=args.seed)

