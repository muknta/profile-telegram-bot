import os
from telebot import TeleBot, types
from telebot.types import Message
from flask import Flask, request
from config import API_TOKEN, HEROKU_URL
from db_helper import db


bot = TeleBot(API_TOKEN)
server = Flask(__name__)

sentences = {
	'help': 'This bot created as task for Momentum Bots',
	'menu': 'Menu',
	'settings': 'Settings',
	'get_name': 'Enter your name (2-20 characters):',
	'get_age': 'Enter your age (1-200):',
	'get_gender': 'Choose your gender:'
}
MIN_NAME_LEN = 2
MAX_NAME_LEN = 20

# users = {}

# class User:
# 	def __init__(self, name):
# 		self.name = name
# 		self.age = None
# 		self.gender = None


@server.route('/{}'.format(API_TOKEN), methods=['POST'])
def get_message():
	bot.process_new_updates([types.Update.de_json(request.stream.read().decode("utf-8"))])
	return "ok", 200

@server.route("/", methods=['GET'])
def webhook():
	bot.remove_webhook()
	bot.set_webhook(url='{}/{}'.format(HEROKU_URL, API_TOKEN))
	return "ok", 200


def check_any_command(cmd):
	commands = {
		'/start': start,
		'/help': help,
		'/menu': menu,
		'/info': get_info,
		'/settings': change_info,
		'/change_name': process_info,
		'/change_age': process_info,
		'/change_gender': process_info,
		'/delete': delete_info
	}
	return commands.get(cmd)


def is_natural_age(n: str):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer() \
        	and float(n) > 0 and float(n) < 200


def process_exception(message: Message, error: str):
	bot.reply_to(message, f'Exception: {error}')
	start(message)


@bot.message_handler(commands=['start'])
def start(message: Message):
	markup = types.ReplyKeyboardRemove(selective=False)
	msg = bot.send_message(message.chat.id, sentences['get_name'], reply_markup=markup)
	bot.register_next_step_handler(msg, process_name_step)


@bot.message_handler(commands=['help'])
def help(message: Message):
	bot.reply_to(message, sentences['help'])


@bot.message_handler(commands=['menu'])
def menu(message: Message):
	try:
		chat_id = message.chat.id

		markup = types.ReplyKeyboardMarkup(row_width=2)
		info_btn = types.KeyboardButton('Info')
		settings_btn = types.KeyboardButton('Settings')
		markup.add(info_btn, settings_btn)

		msg = bot.send_message(chat_id, sentences['menu'], reply_markup=markup)
		bot.register_next_step_handler(msg, process_menu)
	except Exception as e:
		process_exception(message, e)


def process_menu(message: Message):
	try:
		chat_id = message.chat.id
		param = message.text
		if param in ['Info', '/info']:
			get_info(message)
		elif param in ['Settings', '/settings']:
			change_info(message)
		else:
			func = check_any_command(param)
			if func:
				func(message)
			else:
				menu(message)
	except Exception as e:
		process_exception(message, e)


@bot.message_handler(commands=['info'])
def get_info(message: Message):
	try:
		chat_id = message.chat.id
		# user = users[chat_id]
		data = db.get_data(chat_id)
		print(data)
		user_data = ''
		for tupl in data:
			user_data = '''Name: {} \nAge: {} \nGender: {}
					'''.format(tupl[0], tupl[1], tupl[2])	
		# user_data = '''Name: {} \nAge: {} \nGender: {}
		# 			'''.format(user.name, user.age, user.gender)

		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(chat_id, user_data, reply_markup=markup)
		menu(message)
	except Exception as e:
		process_exception(message, e)


@bot.message_handler(commands=['settings'])
def change_info(message: Message):
	try:
		chat_id = message.chat.id

		markup = types.ReplyKeyboardMarkup(row_width=2)
		name_btn = types.KeyboardButton('Change name')
		age_btn = types.KeyboardButton('Change age')
		gender_btn = types.KeyboardButton('Change gender')
		back_btn = types.KeyboardButton('Back')
		markup.add(name_btn, age_btn, gender_btn, back_btn)

		msg = bot.send_message(chat_id, sentences['settings'], reply_markup=markup)
		bot.register_next_step_handler(msg, process_info)
	except Exception as e:
		process_exception(message, e)


@bot.message_handler(commands=['change_name', 'change_age', 'change_gender'])
def process_info(message: Message):
	try:
		chat_id = message.chat.id
		param = message.text

		markup = types.ReplyKeyboardMarkup()
		back_btn = types.KeyboardButton('Back')
		markup.add(back_btn)
		if param in ['Change name', '/change_name']:
			msg = bot.send_message(chat_id, sentences['get_name'], reply_markup=markup)
			bot.register_next_step_handler(msg, process_name)
		elif param in ['Change age', '/change_age']:
			msg = bot.send_message(chat_id, sentences['get_age'], reply_markup=markup)
			bot.register_next_step_handler(msg, process_age)
		elif param in ['Change gender', '/change_gender']:
			bot.send_message(chat_id, 'if you wanna change', reply_markup=markup)
			set_gender(message)
		elif param == 'Back':
			menu(message)
		else:
			func = check_any_command(param)
			if func:
				func(message)
			else:
				change_info(message)
	except Exception as e:
		process_exception(message, e)


def process_name(message: Message):
	try:
		chat_id = message.chat.id
		name = message.text
		if name == 'Back':
			return change_info(message)
		if len(name) >= MIN_NAME_LEN and len(name) <= MAX_NAME_LEN:
			# user = users.get(chat_id)
			# if user:
			# 	user.name = name
			# else:
			# 	users[chat_id] = User(name)
			data = db.check_row(chat_id)
			for tupl in data:
				for num in tupl:
					row_num = num
			if row_num == 0:
				db.append_row(chat_id)
			db.update_row(chat_id, 'name', name)

			menu(message)
		else:
			msg = bot.reply_to(message, sentences['get_name'])
			bot.register_next_step_handler(msg, process_name)
	except Exception as e:
		process_exception(message, e)


def process_name_step(message: Message):
	try:
		chat_id = message.chat.id
		name = message.text
		if len(name) >= MIN_NAME_LEN and len(name) <= MAX_NAME_LEN:
			# user = users.get(chat_id)
			# if user:
			# 	user.name = name
			# else:
			# 	users[chat_id] = User(name)
			data = db.check_row(chat_id)
			for tupl in data:
				for num in tupl:
					row_num = num
			if row_num == 0:
				db.append_row(chat_id)
			db.update_row(chat_id, 'name', name)

			msg = bot.reply_to(message, sentences['get_age'])
			bot.register_next_step_handler(msg, process_age_step)
		else:
			msg = bot.reply_to(message, sentences['get_name'])
			bot.register_next_step_handler(msg, process_name_step)
	except Exception as e:
		process_exception(message, e)


def process_age(message: Message):
	try:
		chat_id = message.chat.id
		age = message.text
		if is_natural_age(age):
			age = int(age)
			# user = users[chat_id]
			# user.age = age
			db.update_row(chat_id, 'age', age)

			menu(message)
		elif age == 'Back':
			change_info(message)
		else:
			msg = bot.reply_to(message, sentences['get_age'])
			bot.register_next_step_handler(msg, process_age)
	except Exception as e:
		process_exception(message, e)


def process_age_step(message: Message):
	try:
		chat_id = message.chat.id
		age = message.text
		if is_natural_age(age):
			age = int(age)
			# user = users[chat_id]
			# user.age = age
			db.update_row(chat_id, 'age', age)

			set_gender(message)
		else:
			msg = bot.reply_to(message, sentences['get_age'])
			bot.register_next_step_handler(msg, process_age_step)
	except Exception as e:
		process_exception(message, e)


def set_gender(message: Message):
	try:
		chat_id = message.chat.id

		markup = types.InlineKeyboardMarkup()
		markup.row(
			types.InlineKeyboardButton('female', callback_data='female'),
			types.InlineKeyboardButton('male', callback_data='male')
		)
		msg = bot.send_message(chat_id, sentences['get_gender'], reply_markup=markup)
		bot.register_next_step_handler(msg, process_gender)
	except Exception as e:
		process_exception(message, e)


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
	print(query, type(query))
	data = query.data
	if data in ['female', 'male']:
		bot.clear_step_handler_by_chat_id(chat_id=query.message.chat.id)
		get_gender_callback(query)


def get_gender_callback(query):
	bot.answer_callback_query(query.id)
	send_gender_result(query.message, query.data)


def send_gender_result(message: Message, gender:str):
	try:
		chat_id = message.chat.id
		bot.send_chat_action(chat_id, 'typing')
		bot.send_message(chat_id, gender)

		# user = users[chat_id]
		# user.gender = gender
		db.update_row(chat_id, 'gender', gender)
		menu(message)
	except Exception as e:
		process_exception(message, e)


def process_gender(message: Message):
	try:
		chat_id = message.chat.id
		gender = message.text
		if gender in ['male', 'female']:
			# user = users[chat_id]
			# user.gender = gender
			db.update_row(chat_id, 'gender', gender)

			menu(message)
		elif gender == 'Back':
			change_info(message)
		else:
			set_gender(message)
	except Exception as e:
		process_exception(message, e)


@bot.message_handler(commands=['delete'])
def delete_info(message: Message):
	try:
		chat_id = message.chat.id

		data = db.check_row(chat_id)
		for tupl in data:
			for num in tupl:
				row_num = num
		# if founded 1 row
		if row_num:
			db.delete_row(chat_id)
			start(message)
	except Exception as e:
		process_exception(message, e)


# @bot.message_handler(func=lambda msg: True, content_types=['text'])
# def each_input(message):
# 	bot.reply_to(message, message.text[::-1])


# bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()

# bot.polling()


if __name__ == '__main__':
	server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
