 #!/usr/bin/python
 # -*- coding: utf-8 -*-

#To create an instance of the telegram.Bot:

import telegram 
from threading import Timer 
import sys
import random
#from messaging import sendMessage, sendChat
sys.path.insert(0,'..')
import token

print token.token()
bot = telegram.Bot(token=token.token())
startTimer=3

bot_me=bot.getMe()

bot_firstname=bot_me.first_name
bot_username=bot_me.username

print 'Bot ready: '+ bot_firstname+' '+bot_username
			
def sendMessage(uid, message, reply_markup):
	if uid>0:
		bot.sendMessage(chat_id=uid, text=message, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=reply_markup)

def sendChat(g,message,exceptUID,games):
	players=games[g]['players']
	for player in players.keys():
		uid=players[player]
		if uid!=0 and uid!=exceptUID:
			reply_markup = telegram.ReplyKeyboardHide()
			sendMessage(uid,message,reply_markup)

def getUserName(message):
	try:
		username='@'+message.from_user.username
	except:
		username=message.from_user.first_name+' '+message.from_user.last_name
	return username.encode('ascii','ignore')

def startCountDown(g):
	global games, current_game
	print 'timer fired'

	#creating new game to join and passing roles
	current_game+=1
	games[current_game]={'players': players2, 'state': 'joining', 'mafia':[], 'doctor':[], 'police':[], 'barman':[], \
'citizen':[], 'mafia_vote':[], 'doctor_vote':[], 'barman_vote':[]}

	games[g]['state']='night'
	chatMessage='Game has started. Now sending the roles'
	sendChat(g, chatMessage, 0, games)
	roles(g)

	
def joining(g, uid, message):
	global state, games, current_game
	out=''
	username=getUserName(message)
	text=message.text

	if username not in games[g]['players'].keys():
		print 'Adding user to the game'
		games[g]['players'][username]=uid
		pl=games[g]['players']	
		chatMessage=username+' joined the game.\n Current Players: '+ ' '.join(pl)
		sendChat(g, chatMessage, 0, games)
		
		NeedMorePlayers=5-len(players)
		if NeedMorePlayers>0:
			out='Need '+str(NeedMorePlayers)+' more to start the game'

		#state=games[max(games.keys())][0]
		if len(players)==5:
			t = Timer(startTimer, startCountDown, args=[g])
			print 'Firing timer to start the game'
			t.start()	
			chatMessage='Now we are ready to roll. Game will start in '+str(startTimer)+' seconds.'
			sendChat(g, chatMessage, 0, games)
	else:
		if text=='/start' or text=='/join':
			out='You\'ve already joined. Please, wait until the game is started.'
		else:
			print 'Sending chat message'
			out=''
			chatMessage=username+': '+text
			sendChat(g, chatMessage, uid, games)
	return(out)

def roles(g):
	global games
	players=games[g]['players'].keys()	
	print players
	PlayerLen=len(players)
	PlayerLen = 10 if PlayerLen>10 else PlayerLen
	current_layout=rolesLayout[PlayerLen]
	print current_layout

	random.shuffle(players)
	while players:
  		player = players.pop()
  		print player
  		reply_markup = telegram.ReplyKeyboardHide()
  		if current_layout['mafia']>0:
  			games[g]['mafia'].append(player)
  			current_layout['mafia']-=1
  			sendMessage(games[g]['players'][player], 'You are playing mafia in this game', reply_markup)  			
  		elif current_layout['doctor']>0:
  			games[g]['doctor'].append(player)
  			current_layout['doctor']-=1
  			sendMessage(games[g]['players'][player], 'You are playing doctor in this game', reply_markup)
  		elif current_layout['police']>0:
  			games[g]['police'].append(player)
  			current_layout['police']-=1
  			sendMessage(games[g]['players'][player], 'You are playing cop in this game', reply_markup)
  		elif current_layout['barman']>0:
  			games[g]['barman'].append(player)
  			current_layout['barman']-=1
  			sendMessage(games[g]['players'][player], 'You are playing barman in this game', reply_markup)
  		elif True:
  			games[g]['citizen'].append(player)  			
  			sendMessage(games[g]['players'][player], 'You are just a citizen in this game', reply_markup)
  	print games[g]
	#print current_layout.values()
	#message='roles'

	print 'We have the roles, switching to night mode'
	games[g]['state']='night'
	nightmessaging(g)
	#print message
	#return (message)

def nightmessaging(g):
	print 'Sending out messages to night players'
	
	mafia=games[g]['mafia']
	doctors=games[g]['doctor']
	police=games[g]['police']
	barman=games[g]['barman']
	citizen=games[g]['citizen']
	players=games[g]['players']
	for p in mafia:
		actionable=[i for i in players.keys() if i not in mafia]
		custom_keyboard = [[k] for k in actionable]
		#print actionable
		#print custom_keyboard
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
		sendMessage(players[p], 'Hey, mafia, kill someone', reply_markup)
	for p in doctors:
		custom_keyboard = [[k] for k in players]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
		sendMessage(players[p], 'Hey, doc, heal somebody', reply_markup)
	for p in police:
		actionable=[i for i in players if i not in police]
		custom_keyboard = [[k] for k in actionable]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
		sendMessage(players[p], 'Hey, police, check somebody', reply_markup)
		#print actionable
		#print custom_keyboard
	for p in barman:
		actionable=[i for i in players if i not in barman]
		custom_keyboard = [[k] for k in actionable]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
		sendMessage(players[p], 'Hey, barman, drink with someone', reply_markup)
	for p in citizen:
		reply_markup = telegram.ReplyKeyboardHide()
		sendMessage(players[p], 'zzzz...', reply_markup)
	print 'roles sent'

def night(g, uid, message):
	#good ides to start a night timer
	out=''
	global games
	text=message.text
	#find role
	username=getUserName(message)
	if username in games[g]['mafia']:
		print 'this is mafia'
		if text in games[g]['players']:
			#saving mafia vote
			games[g]['mafia_vote'].append(text)
			#sending mafia chat update if >1 mafia
			#warn for uniqueness
	elif username in games[g]['doctor']:
		print 'this is a doctor'
		if text in games[g]['players']:
			#saving doctor vote
			games[g]['doctor_vote'].append(text)
	elif username in games[g]['police']:
		print 'this is police'
		#perform police checks
		if text in games[g]['mafia']:
			out=text+' is mafia'
			print 'mafia found'
		elif text in games[g]['doctor']:
			out=text+' is doctor'
			print 'doc found'
		elif text in games[g]['barman']:
			out=text+' is barman'
			print 'barman found'
		elif text in games[g]['citizen']:
			out=text+' is citizen'
			print 'citizen found'
	elif username in games[g]['barman']:
		print 'this is a barman'
		if text in games[g]['players']:
			#saving barman vote
			games[g]['barman_vote'].append(text)
	elif True:
		print 'citizen sleeps...'

	print games[g]
	#check if we need more checks/votes and then maybe kill the night timer

	#save action

	print out
	return (out)

def day(g, uid, message):
	out='day'
	print out
	return (out)

def results(g, uid, message):
	out='results'
	print out
	return (out)

current_offset=0
messages=[]
current_game=1
players={'@alpha':0,'@gamma':0,'@sigma':0,'@kappa':0}
players2={'@alpha2':0,'@beta2':0,'@gamma2':0,'@sigma2':0} 
# potential problem - User can change username during game - but this is unlikely
rolesLayout={5: {'mafia': 1, 'doctor': 1, 'police': 1, 'barman': 0}, \
6:{'mafia': 2, 'doctor': 1, 'police': 1, 'barman': 0}, 7:{'mafia': 2, 'doctor': 2, 'police': 1, 'barman': 0}, \
8:{'mafia': 2, 'doctor': 2, 'police': 1, 'barman': 0}, 9:{'mafia': 2, 'doctor': 2, 'police': 1, 'barman': 1}, \
10:{'mafia': 2, 'doctor': 2, 'police': 1, 'barman': 1}} 

state_flow={'joining':joining,'roles':roles,'night':night,'day':day,'results':results}
state='joining'

games={current_game: {'players': players, 'state': state, 'mafia':[], 'doctor':[], 'police':[], 'barman':[], \
'citizen':[], 'mafia_vote':[], 'doctor_vote':[], 'barman_vote':[]}} #mafia, doc, police, barman

while (True):
	print 'Getting updates:'
	updates=None

	updates=bot.getUpdates(offset=current_offset, limit=100, timeout=60)
	message=''
	reply_markup = telegram.ReplyKeyboardHide()
	print 'Update found'
	#print dir(updates)
	#print updates
	for u in updates:
		uid=u.message.from_user.id
		print 'from: '+str(uid)
		print u.message.text				
		#looking for a game for UID
		game_found=False
		#print dir(games.keys())
		for g in games.keys():
			#print games[g][0].values()
			if uid in games[g]['players'].values():
				game_found=True
				game=g
				print 'Game found for this user: '+str(g)

		#if game not found - join one
		if not(game_found):
			if u.message.text=='/start' or u.message.text=='/join' or u.message.text.decode('utf-8')==telegram.Emoji.RAISED_HAND.decode('utf-8'):
				game=max(games.keys())
				print "joining the ",
			else:
				game=0
				print 'game not found but he is not joining yet'
				custom_keyboard = [[telegram.Emoji.RAISED_HAND]]
				reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
				message='High five to join, bro'
				#remove below - this is debugging
				game=max(games.keys())

		print "game: "+str(game)
		if game >0:
			#bot.sendChatAction(chat_id=uid, action=telegram.ChatAction.FIND_LOCATION)
			print "Game phase: "+str(games[game]['state'])
			message=state_flow[games[game]['state']](game,uid,u.message)
		
		if message!='':
			sendMessage(uid, message, reply_markup)

		current_offset=u.update_id+1