from telebot import TeleBot, types
from config import API_TOKEN


bot = TeleBot(API_TOKEN)

sentences = {
	'help': 'This bot created as task for Momentum Bots',
	'menu': 'Menu',
	'settings': 'Settings',
	'get_name': 'Enter your name (2-20 characters):',
	'get_age': 'Enter your age:',
	'get_gender': 'Choose your gender:'
}
MIN_NAME_LEN = 2
MAX_NAME_LEN = 20

users = {}

class User:
	def __init__(self, name):
		self.name = name
		self.age = None
		self.gender = None


def is_natural(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer() and float(n) > 0


@bot.message_handler(commands=['start'])
def start(message):
	msg = bot.reply_to(message, sentences['get_name'])
	bot.register_next_step_handler(msg, process_name_step)


@bot.message_handler(commands=['help'])
def help(message):
	bot.reply_to(message, sentences['help'])


@bot.message_handler(commands=['menu'])
def menu(message):
	try:
		chat_id = message.chat.id

		markup = types.ReplyKeyboardMarkup(row_width=2)
		info_btn = types.KeyboardButton('Info')
		settings_btn = types.KeyboardButton('Settings')
		markup.add(info_btn, settings_btn)

		msg = bot.send_message(chat_id, sentences['menu'], reply_markup=markup)
		bot.register_next_step_handler(msg, process_menu)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


def process_menu(message):
	try:
		chat_id = message.chat.id
		param = message.text
		# markup = types.ReplyKeyboardRemove(selective=False)
		# bot.send_message(chat_id, message, reply_markup=markup)
		if param == 'Info':
			get_info(message)
		elif param == 'Settings':
			change_info(message)
		else:
			menu(message)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


@bot.message_handler(commands=['info'])
def get_info(message):
	try:
		chat_id = message.chat.id
		user = users[chat_id]
		user_data = '''Name: {} \nAge: {} \nGender: {}
					'''.format(user.name, user.age, user.gender)
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(chat_id, user_data, reply_markup=markup)
		menu(message)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


@bot.message_handler(commands=['settings'])
def change_info(message):
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
		bot.reply_to(message, f'Exception: {e}')


@bot.message_handler(commands=['change_name', 'change_age', 'change_gender'])
def process_info(message):
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
			bot.send_message(chat_id, 'if you wanna', reply_markup=markup)
			set_gender(message)
		elif param == 'Back':
			menu(message)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


def process_name(message):
	try:
		chat_id = message.chat.id
		name = message.text
		if name == 'Back':
			return change_info(message)
		if len(name) >= MIN_NAME_LEN and len(name) <= MAX_NAME_LEN:
			user = users.get(chat_id)
			if user:
				user.name = name
			else:
				users[chat_id] = User(name)

			menu(message)
		else:
			msg = bot.reply_to(message, sentences['get_name'])
			bot.register_next_step_handler(msg, process_name)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


def process_name_step(message):
	try:
		chat_id = message.chat.id
		name = message.text
		if len(name) >= MIN_NAME_LEN and len(name) <= MAX_NAME_LEN:
			user = users.get(chat_id)
			if user:
				user.name = name
			else:
				users[chat_id] = User(name)

			msg = bot.reply_to(message, sentences['get_age'])
			bot.register_next_step_handler(msg, process_age_step)
		else:
			msg = bot.reply_to(message, sentences['get_name'])
			bot.register_next_step_handler(msg, process_name_step)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


def process_age(message):
	try:
		chat_id = message.chat.id
		age = message.text
		if is_natural(age):
			age = int(age)
			user = users[chat_id]
			user.age = age

			menu(message)
		elif age == 'Back':
			change_info(message)
		else:
			msg = bot.reply_to(message, sentences['get_age'])
			bot.register_next_step_handler(msg, process_age)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


def process_age_step(message):
	try:
		chat_id = message.chat.id
		age = message.text
		if is_natural(age):
			age = int(age)
			user = users[chat_id]
			user.age = age

			set_gender(message)
		else:
			msg = bot.reply_to(message, sentences['get_age'])
			bot.register_next_step_handler(msg, process_age_step)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


def set_gender(message):
	try:
		chat_id = message.chat.id

		markup = types.InlineKeyboardMarkup()
		markup.row(
			types.InlineKeyboardButton('female', callback_data='female'),
			types.InlineKeyboardButton('male', callback_data='male')
		)
		# markup = types.ReplyKeyboardMarkup(row_width=2)
		# female_btn = types.KeyboardButton('female')
		# male_btn = types.KeyboardButton('male')
		# back_btn = types.KeyboardButton('Back')
		# markup.add(female_btn, male_btn, back_btn)
		msg = bot.send_message(chat_id, sentences['get_gender'], reply_markup=markup)
		bot.register_next_step_handler(msg, process_gender)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
	data = query.data
	if data in ['female', 'male']:
		bot.clear_step_handler_by_chat_id(chat_id=query.message.chat.id)
		get_gender_callback(query)


def get_gender_callback(query):
	bot.answer_callback_query(query.id)
	send_gender_result(query.message, query.data)


def send_gender_result(message, gender):
	try:
		chat_id = message.chat.id
		bot.send_chat_action(chat_id, 'typing')
		bot.send_message(chat_id, gender)

		user = users[chat_id]
		user.gender = gender
		menu(message)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


def process_gender(message):
	try:
		chat_id = message.chat.id
		gender = message.text
		if gender in ['male', 'female']:
			user = users[chat_id]
			user.gender = gender
			menu(message)
		elif gender == 'Back':
			change_info(message)
		else:
			set_gender(message)
	except Exception as e:
		bot.reply_to(message, f'Exception: {e}')


# @bot.message_handler(func=lambda msg: True, content_types=['text'])
# def each_input(message):
# 	bot.reply_to(message, message.text[::-1])


bot.polling()