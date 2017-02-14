#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import time
import sys
import logging
from telebot import types
import globales

TOKEN = '354808058:AAGz5zTP9-FKUQawnFixQWy1UxjO70Z2bcs'

knownUsers = []
userStep = {}

commands = {
              'go': 'Empezar a usar el bot',
              'help': 'ayuda sobre los comandos',
              'sensor': 'recibes los valores de los sensores',
              'video': 'manda el video'
}

hideBoard = types.ReplyKeyboardRemove()

bot = telebot.TeleBot(TOKEN)

video = ' '

cid= ' '
#3575750
#Cambia la direccion del video
def cambiarDireccion():
	global video
	video = open(globales.direccion, 'rb')

#had to use the /start command and are therefore known to the bot)
def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        return 0

#Comando iniciar sesion
@bot.message_handler(commands=['go'])
def command_start(m):
	global cid
	cid = m.chat.id
	if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
		knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
		userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
		bot.send_message(cid, "Hola, extranjero, déjame conocerte...")
		bot.send_message(cid, "Ahora te conozco...")
		command_help(m)  # show the new user the help page
	else:
		bot.send_message(cid, "Ya te conozco, no necesito buscarte de nuevo!")
	print (cid)

#Ayuda
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "Los siguientes comandos disponibles son: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page

#Mandar el video
@bot.message_handler(commands=['video'])
def mandarVideo():
	global video
	global cid
	userStep[cid] = 1
	bot.send_message(cid, "!!!Alerta!!!")
	bot.send_message(cid, "!!!Intrusos!!!")
	bot.send_message(cid, "Espere unos segundos para recibir el video...")
	bot.send_video(cid, video)
	userStep[cid] = 0

#Mandar sensores
@bot.message_handler(commands=['sensor'])
def sensores(m):
	global video
	global cid
	userStep[cid] = 1
	bot.send_message(cid, "Temperatura: "+ str(globales.temperatura)+"º")
	bot.send_message(cid, "Humedad: "+str(globales.humedad)+"%")
	bot.send_message(cid, "Gas: "+str(globales.gas))
	bot.send_message(cid, "Luz: "+str(globales.luz))
	userStep[cid] = 0

#Para mensajes no reconocidos
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
    bot.send_message(m.chat.id, "No te entiendo \"" + m.text + "\"\nEscribe /help para mas ayuda")


def arrancar():
	bot.polling()
