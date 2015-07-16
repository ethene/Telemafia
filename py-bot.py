 #!/usr/bin/python
 # -*- coding: utf-8 -*-

#To create an instance of the telegram.Bot:

import telegram 
from threading import Timer 
import sys
import random
#from messaging import sendMessage, sendChat
import logging
sys.path.insert(0,'..')
import token

#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(format='%(asctime)s:%(levelname)s -%(message)s', filename='../bot.log', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())

logging.debug(token.token())

bot = telegram.Bot(token=token.token())
startTimer=1
nightTimer=10
polling_timeout=60

bot_me=bot.getMe()

bot_firstname=bot_me.first_name
bot_username=bot_me.username

def logit(message):
	if message!='':
		logging.info(message)

logit('Bot ready: '+ bot_firstname+' '+bot_username)
			
def sendMessage(uid, message, reply_markup):
	if uid>0:
		bot.sendMessage(chat_id=uid, text=message, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=reply_markup)

def sendChat(g,message,exceptUID):
	players=games[g]['players']
	for player in players.keys():
		uid=players[player]
		if uid!=0 and uid!=exceptUID:
			reply_markup = telegram.ReplyKeyboardHide()
			sendMessage(uid,message,reply_markup)

def sendMafiaChat(g, message, exceptUID):
	players=games[g]['players']
	mafia=games[g]['mafia']
	for m in mafia:
		uid=players[m]
		logging.debug('sending mafia message to: '+m)
		if uid!=0 and uid!=exceptUID:
			reply_markup = None
			sendMessage(uid,message,reply_markup)

def getUserName(message):
	try:
		username='@'+message.from_user.username
	except:
		username=message.from_user.first_name+' '+message.from_user.last_name
	return username.encode('ascii','ignore')

def startCountDown(g):
	global games, current_game
	logging.debug('start timer fired')

	#creating new game to join and passing roles
	current_game+=1
	games[current_game]={'players': players2, 'state': 'joining', 'mafia':[], 'doctor':[], 'police':[], 'barman':[], \
'citizen':[], 'mafia_vote':{}, 'doctor_vote':[], 'barman_vote':[]}

	games[g]['state']='night'
	chatMessage='Game has started. Now sending the roles'
	sendChat(g, chatMessage, 0)
	roles(g)

def stopNightMode(g):
	global games
	logit('Night should be finished')
	games[g]['night_timer']=None
	nightResults(g)
	#print games

def nightResults(g):
	global games
	chatMessage='Night is over. Let\'s see what happened...\n'
	#check mafia kills
	mafia_move=games[g]['mafia_vote']
	doc_move=games[g]['doctor_vote']
	police_move=games[g]['police_vote']
	barman_move=games[g]['barman_vote']

	if len([v for v in mafia_move.values() if v!=None])>0:
		victims=list(set(games[g]['mafia_vote'].values()))
		if len(victims)>1:
			random.shuffle(victims)
			
		chatMessage+='Mafia has selected to kill '+victims[0]+'\n'
		if victims[0] in games[g]['doctor_vote'].values():
			chatMessage+='but doctor saved the victim\n'
		else:
			games[g]['killed'].append(victims[0])
			chatMessage+='who played as '+police_check(g, victims[0])+'\n'

	if len([v for v in doc_move.values() if v!=None])>0>0:
		chatMessage+='Doctor tested his drugs on '+doc_move.values()[0]+'\n'
	if len([v for v in police_move.values() if v!=None])>0:
		chatMessage+='Police checked '+police_move.values()[0]+' ID\n'
	if len([v for v in barman_move.values() if v!=None])>0:
		chatMessage+='Barman drunk with '+barman_move.values()[0]+'\n'
	sendChat(g, chatMessage, 0)
	daymessaging(g)

def getLivePlayers(g):
	live_players=[p for p in games[g]['players'].keys() if p not in games[g]['killed']]
	live_players=list(reversed(live_players))
	return live_players

def daymessaging(g):
	global games
	games[g]['state']='day'
	chatMessage='Now you all you can discuss and kill the possible mafia.\n'
	live_players=getLivePlayers(g)
	print live_players
	chatMessage+='You can vote by using /vote # or !#, where # is the player name or number. \n'
	for p in live_players:
		chatMessage+=str(live_players.index(p)+1)+': '+p+'\n'
	sendChat(g, chatMessage, 0)

def joining(g, uid, message):
	global games, current_game
	out=''
	username=getUserName(message)
	text=message.text

	if username not in games[g]['players'].keys():
		logit('Adding user to the game')
		games[g]['players'][username]=uid
		pl=games[g]['players']	
		chatMessage=username+' joined the game.\n Current Players: '+ ' '.join(pl)
		sendChat(g, chatMessage, 0)
		
		NeedMorePlayers=5-len(players)
		if NeedMorePlayers>0:
			out='Need '+str(NeedMorePlayers)+' more to start the game'

		#state=games[max(games.keys())][0]
		if len(players)==5:
			t = Timer(startTimer, startCountDown, args=[g])
			logit('Firing timer to start the game for '+str(startTimer)+' sec')
			t.start()	
			chatMessage='Now we are ready to roll. Game will start in '+str(startTimer)+' seconds.'
			sendChat(g, chatMessage, 0)
	else:
		if text=='/start' or text=='/join':
			out='You\'ve already joined. Please, wait until the game is started.'
		else:
			logging.debug('Sending chat message')
			out=''
			chatMessage=username+': '+text
			sendChat(g, chatMessage, uid)
	return(out)

def roles(g):
	global games
	players=games[g]['players'].keys()	
	PlayerLen=len(players)
	PlayerLen = 10 if PlayerLen>10 else PlayerLen
	current_layout=rolesLayout[PlayerLen]

	random.shuffle(players)
	while players:
  		player = players.pop()
  		print player
  		reply_markup = telegram.ReplyKeyboardHide()
  		if current_layout['mafia']>0:
  			games[g]['mafia'].append(player)
  			games[g]['mafia_vote'][player]=None
  			current_layout['mafia']-=1
  			sendMessage(games[g]['players'][player], 'You are playing mafia in this game', reply_markup)  			
  		elif current_layout['doctor']>0:
  			games[g]['doctor'].append(player)
  			games[g]['doctor_vote'][player]=None
  			current_layout['doctor']-=1
  			sendMessage(games[g]['players'][player], 'You are playing doctor in this game', reply_markup)
  		elif current_layout['police']>0:
  			games[g]['police'].append(player)
  			games[g]['police_vote'][player]=None
  			current_layout['police']-=1
  			sendMessage(games[g]['players'][player], 'You are playing cop in this game', reply_markup)
  		elif current_layout['barman']>0:
  			games[g]['barman'].append(player)
  			games[g]['barman_vote'][player]=None
  			current_layout['barman']-=1
  			sendMessage(games[g]['players'][player], 'You are playing barman in this game', reply_markup)
  		elif True:
  			games[g]['citizen'].append(player)  			
  			sendMessage(games[g]['players'][player], 'You are just a citizen in this game', reply_markup)
  	
#  	logging.debug(games[g])

	logit('We have the roles, switching to night mode')
	games[g]['state']='night'
	nightmessaging(g)

def runBotMoves(g):
	global games
	playes=games[g]['players'].keys()
	for player in players:
		if games[g]['players'][player]==0:
			logmessage=player+' is a bot '
			if player in games[g]['mafia']:
				logmessage+='and mafia'
				actionable=[i for i in players if i not in games[g]['mafia']]
				random.shuffle(actionable)
				games[g]['mafia_vote'][player]=actionable[0]
			elif player in games[g]['police']:
				logmessage+='and police'
				games[g]['police_vote'][player]=player
			elif player in games[g]['doctor']:
				logmessage+='and doc'
				actionable=[i for i in players]
				random.shuffle(actionable)
				games[g]['doctor_vote'][player]=actionable[0]
			elif player in games[g]['barman']:
				logmessage+='and barman'
				actionable=[i for i in players]
				random.shuffle(actionable)
				games[g]['barman_vote'][player]=actionable[0]
			elif player in games[g]['citizen']:
				logmessage+='and citizen'
			logit(logmessage)

def nightmessaging(g):
	global games
	logit('Sending out messages to night players')
	sendChat(g, 'Morning comes in '+str(nightTimer)+' seconds.\n Sleep or play if you can!', 0)	
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
	logit('roles sent')
	#starting night timer
	t = Timer(nightTimer, stopNightMode, args=[g])
	logging.debug('Firing timer to wake up in '+str(nightTimer)+' sec')
	t.start()
	games[g]['night_timer']=t
	#here we can play for bot users
	runBotMoves(g)
	
	#print games

def police_check(g, user):
	result=''
	if user in games[g]['mafia']:
		result='mafia'
	elif user in games[g]['doctor']:
		result='doctor'
	elif user in games[g]['police']:
		result='police'
	elif user in games[g]['barman']:
		result='barman'
	elif user in games[g]['citizen']:
		result='citizen'
	return result

	
def night(g, uid, message):
	#good ides to start a night timer
	out=''
	logmessage=''
	global games
	text=message.text
	#find role
	username=getUserName(message)
	if username in games[g]['mafia']:
		logmessage='this is mafia'
		if text in games[g]['players']:
			#saving mafia vote
			games[g]['mafia_vote'][username]=text
			#sending mafia chat update if >1 mafia
			if len(games[g]['mafia'])>1:
				mafia_message='mafiozo '+username+' voted to kill '+text
				if len(list(set(games[g]['mafia_vote'].values())))>1:
					mafia_message+='\n Victim will be randomly selected in the morning.'					
				sendMafiaChat(g, mafia_message, 0)
			out='Vote for '+text+' accepted!'
			#warn for uniqueness
	elif username in games[g]['doctor']:
		logmessage='this is a doctor'
		if text in games[g]['players']:
			#saving doctor vote
			games[g]['doctor_vote'][username]=text
	elif username in games[g]['police']:
		logmessage='this is police and '
		if games[g]['police_vote'][username]==None:
		#perform police checks
			out+=text+' is '+police_check(g, text)
		else:
			out='Sorry, but now you need a sleep'
		logmessage+=out

		games[g]['police_vote'][username]=text
	elif username in games[g]['barman']:
		logmessage='this is a barman'
		if text in games[g]['players']:
			#saving barman vote
			games[g]['barman_vote'][username]=text
	else:
		logmessage='citizen sleeps...'
	logit(logmessage)
	logmessage=''

	logging.info(games[g])
	#check if we need more checks/votes and then maybe kill the night timer
	ReadyToWakeUp=True
	if len(games[g]['police'])>0:
		if games[g]['police_vote'].values()[0]!=None:
			logmessage='police_voted '
		else:
			ReadyToWakeUp=False
	if len(games[g]['doctor'])>0:
		if games[g]['doctor_vote'].values()[0]!=None:
			logmessage+='doc_voted '
		else:
			ReadyToWakeUp=False
	if len(games[g]['barman'])>0:
		if games[g]['barman_vote'].values()[0]!=None:
			logmessage+='barman_voted '
		else:
			ReadyToWakeUp=False
	if len(games[g]['mafia'])>0:
		mafia_votes_list=list(set(games[g]['mafia_vote'].values()))
		if len(mafia_votes_list)==1 and mafia_votes_list[0]!=None:
			logmessage+='mafia_voted '
		else:
			ReadyToWakeUp=False

	logit(logmessage)

	if ReadyToWakeUp:
		logit('Ready To Wake Up')
		games[g]['night_timer'].cancel()
		t = Timer(5, stopNightMode, args=[g])
		logging.debug('Firing timer to wake up in '+str(5)+' sec')
		t.start()
		
	#save action

	#print out
	return (out)

def check_voted(g, voted, username, live_players):
	global games
	out=''
	try:
		games[g]['day_votes'][username]=live_players[int(voted)-1]
		out='Your vote for '+live_players[int(voted)-1]+' is accepted'
	except:	
		print 'except'
		if voted in live_players:
			games[g]['day_votes'][username]=voted
			out='Your vote for '+voted+' is accepted'
		else:
			out='Your vote was not counted'
	return(out)

def day(g, uid, message):
	global games
	username=getUserName(message)
	text=message.text
	out=''
	voted=''
	live_players=getLivePlayers(g)
	print 'day mode'
	if username in live_players:
		print 'live player'
		if text[:1]=='!':
			print '!'
			voted=text[1:]
			print voted
			out=check_voted(g, voted, username, live_players)
		elif text[:5]=='/vote':
			print '/vote'
			voted=text[6:]
			print voted
			out=check_voted(g, voted, username, live_players)
		else:
			outMessage=text
			sendChat(g, outMessage, uid)			
	else:
		out='You have been killed. Just enjoy.'
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
6:{'mafia': 2, 'doctor': 1, 'police': 1, 'barman': 0}, 7:{'mafia': 2, 'doctor': 1, 'police': 1, 'barman': 0}, \
8:{'mafia': 2, 'doctor': 1, 'police': 1, 'barman': 0}, 9:{'mafia': 3, 'doctor': 1, 'police': 1, 'barman': 1}, \
10:{'mafia': 3, 'doctor': 1, 'police': 1, 'barman': 1}} 

state_flow={'joining':joining,'roles':roles,'night':night,'day':day,'results':results}
state='joining'

games={current_game: {'players': players, 'state': state, 'mafia':[], 'doctor':[], 'police':[], 'barman':[], \
'citizen':[], 'mafia_vote':{}, 'doctor_vote':{}, 'barman_vote':{}, 'police_vote':{}, 'day_votes':{}, 'killed':[]}} #mafia, doc, police, barman

while (True):
	logit('polling for updates for '+str(polling_timeout)+' seconds')
	updates=None

	updates=bot.getUpdates(offset=current_offset, limit=100, timeout=polling_timeout)
	message=''
	reply_markup = telegram.ReplyKeyboardHide()
	if updates!=[]: 
		logit('\nUpdate found')
	#print dir(updates)
	#print updates

	for u in updates:
		uid=u.message.from_user.id
		logit('from: '+str(uid))
		logit(u.message.text)
		#looking for a game for UID
		game_found=False
		#print dir(games.keys())
		for g in games.keys():
			#print games[g][0].values()
			if uid in games[g]['players'].values():
				#add check if player is in active game 
				game_found=True
				game=g
				logit('Game found for this user: '+str(g))

		#if game not found - join one
		if not(game_found):
			if u.message.text=='/start' or u.message.text=='/join' or u.message.text.decode('utf-8')==telegram.Emoji.RAISED_HAND.decode('utf-8'):
				game=max(games.keys())
				logit('joining')
			else:
				game=0
				logit('game not found but he is not joining yet')
				custom_keyboard = [[telegram.Emoji.RAISED_HAND]]
				reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
				message='High five to join, bro'
				#remove below - this is debugging
				game=max(games.keys())

		#logit('game: '+str(game))
		if game >0:
			#bot.sendChatAction(chat_id=uid, action=telegram.ChatAction.FIND_LOCATION)
			logit('Game phase: '+str(games[game]['state']))
			message=state_flow[games[game]['state']](game,uid,u.message)
		
		if message!='':
			print games
			sendMessage(uid, message, reply_markup)

		current_offset=u.update_id+1