import sqlite3


class DBHelper:
	def __init__(self, dbname="profile.sqlite3"):
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname, check_same_thread=False)


	def setup(self):
		stmt = '''CREATE TABLE IF NOT EXISTS profile (
        					chat_id TEXT PRIMARY KEY,
        					name TEXT,
        					age INTEGER,
        					gender TEXT);'''
		cursor = self.conn.cursor()
		cursor.execute(stmt)
		self.conn.commit()


	def check_row(self, chat_id):
		stmt = '''SELECT count(*)
        			FROM profile
        			WHERE chat_id = (?);'''
		args = (chat_id, )
		cursor = self.conn.cursor()
		return self.conn.execute(stmt, args)


	def append_row(self, chat_id):
		stmt = '''INSERT INTO profile (chat_id) VALUES (?);'''
		args = (chat_id, )
		cursor = self.conn.cursor()
		cursor.execute(stmt, args)
		self.conn.commit()


	def update_row(self, chat_id, item, value):
		stmt = '''UPDATE profile
        		SET ({}) = (?)
        		WHERE chat_id = (?);'''.format(item)
		args = (value, chat_id)
		cursor = self.conn.cursor()
		cursor.execute(stmt, args)
		self.conn.commit()


	def delete_row(self, chat_id):
		stmt = '''DELETE FROM profile
        			WHERE chat_id = (?);'''
		args = (chat_id, )
		cursor = self.conn.cursor()
		cursor.execute(stmt, args)
		self.conn.commit()


	def get_data(self, chat_id):
		stmt = '''SELECT name, age, gender
        			FROM profile
					WHERE chat_id = (?);'''
		args = (chat_id, )
		cursor = self.conn.cursor()
		return cursor.execute(stmt, args)


db = DBHelper()
# db.setup()
