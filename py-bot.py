 #!/usr/bin/python
 # -*- coding: utf-8 -*-

#To create an instance of the telegram.Bot:

import telegram 
from threading import Timer 
import sys
sys.path.insert(0,'..')
import token

print token.token()
bot = telegram.Bot(token=token.token())
startTimer=30

bot_me=bot.getMe()

bot_firstname=bot_me.first_name
bot_username=bot_me.username

print 'Bot ready: '+ bot_firstname+' '+bot_username

def sendChat(g,message,exceptUID):
	players=games[g][0]
	for player in players.keys():
		uid=players[player]
		if uid!=0 and uid!=exceptUID:
			bot.sendMessage(chat_id=uid, text=message, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None)

def startCountDown(g):
	global games
	games[g][1]='roles'
	chatMessage='Game is started. Now sending the roles'
	sendChat(g, chatMessage, 0)
	print 'timer fired'

def joining(g,uid):
	global state, games, current_game
	#print pl
	username='@'+u.message.from_user.username
	if username not in games[g][0].keys():
		games[g][0][username]=uid
		pl=games[g][0]	
		chatMessage=username+' joined the game.\n Current Players: '+ ' '.join(pl)
		sendChat(g, chatMessage, 0)
		message=''
		state=games[max(games.keys())][0]
		if len(players)==5:
			current_game+=1
			games[current_game]=[players2, state]
			t = Timer(startTimer, startCountDown, args=[g])
			print 'timer start'
			t.start()	
			print 'continue'
			chatMessage='Now we are ready to roll. Game will start in '+str(startTimer)+' seconds.'
			sendChat(g, chatMessage, 0)
	else:
		if u.message.text=='/start' or u.message.text=='/join':
			message='You\'ve already joined. Please, wait until the game is started.'
		else:
			message=''
			chatMessage=username+': '+u.message.text
			sendChat(g, chatMessage, uid)
	return(message)

def roles(g,uid):
	print g
	message='roles'
	print message
	return (message)

def night(g,uid):
	message='night'
	print message
	return (message)

def day(g,uid):
	message='day'
	print message
	return (message)

def results(g,uid):
	message=results
	print message
	return (message)

current_offset=0
messages=[]
current_game=1
players={'@alpha':0,'@beta':0,'@gamma':0,'@sigma':0}
players2={'@alpha2':0,'@beta2':0,'@gamma2':0,'@sigma2':0}
roles={5: [2,1,1,1,0], 6:[2,2,1,1,0], 7:[2,2,2,1,0], 8:[3,2,2,1,0], 9:[3,2,2,1,1], 10:[4,2,2,1,1]} 
#citizen, mafia, doc, police

state_flow={'joining':joining,'roles':roles,'night':night,'day':day,'results':results}
state='joining'

games={current_game: [players, state]}

while (True):
	print 'Getting updates:'
	updates = bot.getUpdates(offset=current_offset, limit=100, timeout=60)
	message=''
	print 'Update found'
	#print dir(updates)
	#print updates
	for u in updates:
		uid=u.message.from_user.id
		print u.message.text				
		#looking for a game for UID
		game_found=False
		#print dir(games.keys())
		for g in games.keys():
			print games[g][0].values()
			if uid in games[g][0].values():
				game_found=True
				game=g

		#if game not found - join one
		if not(game_found):
			print 'game not found'
			if u.message.text=='/start' or u.message.text=='/join':
				game=max(games.keys())
			else:
				game=0
				message='Type /start or /join to play the game'

		print "game: "+str(game)
		if game >0:
			#bot.sendChatAction(chat_id=uid, action=telegram.ChatAction.FIND_LOCATION)
			message=state_flow[games[game][1]](game,uid)
		
		if message!='':
			bot.sendMessage(chat_id=uid, text=message, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None)	
	
		current_offset=u.update_id+1

'''
To fetch images sent to your Bot:

>>> updates = bot.getUpdates()
>>> print [u.message.photo for u in updates if u.message.photo]
To reply messages you’ll always need the chat_id:

>>> chat_id = bot.getUpdates()[-1].message.chat_id
To post a text message:

>>> bot.sendMessage(chat_id=chat_id, text="I'm sorry Dave I'm afraid I can't do that.")
To post an Emoji (special thanks to Tim Whitlock):

>>> bot.sendMessage(chat_id=chat_id, text=telegram.Emoji.PILE_OF_POO)
To post a audio file:

>>> bot.sendAudio(chat_id=chat_id, audio=open('tests/telegram.ogg', 'rb'))
To tell the user that something is happening on bot’s side:

>>> bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
To create Custom Keyboards:

>>> custom_keyboard = [[ telegram.Emoji.THUMBS_UP_SIGN, telegram.Emoji.THUMBS_DOWN_SIGN ]]
>>> reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
>>> bot.sendMessage(chat_id=chat_id, text="Stay here, I'll be back.", reply_markup=reply_markup)
To hide Custom Keyboards:

>>> reply_markup = telegram.ReplyKeyboardHide()
>>> bot.sendMessage(chat_id=chat_id, text="I'm back.", reply_markup=reply_markup)
'''