import datetime
import psycopg2
import paramiko
from config import Config

cfg = Config()

class Database: 
	def __init__(self):
		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(cfg.host, port=cfg.port, username=cfg.username, password=cfg.password)

			print("A connection to the server has been established")

			self.conn = psycopg2.connect(
  			database = cfg.database,
			user = cfg.user,
			password = cfg.password_data,
			host = cfg.host_data,
			port = cfg.port_data
			)
			print ("Database connection established")
		except Exception as err:
			print(str(err))

	# функция для работы с таблицей
	async def get_count(self):
		with self.conn.cursor() as cursor:
			cursor.execute("""SELECT COUNT(*) FROM users;""")
			return cursor.fetchone()[0]

	async def table_users(self, user_id: int, username: str, first_name: str, send_message: bool, referral: bool):
		with self.conn.cursor() as cursor:
			if referral:
				cursor.execute("""INSERT INTO users (user_id, username, first_name, send_message, referral_from) VALUES (%s, %s, %s, %s, (SELECT users.user_id FROM referrals INNER JOIN users ON referrals.user_from = users.id WHERE referrals.referral = %s));""", (user_id, username, first_name, send_message, user_id))
			else:
				cursor.execute("""INSERT INTO users (user_id, username, first_name, send_message) VALUES (%s, %s, %s, %s);""", (user_id, username, first_name, send_message))
			self.conn.commit()

	# table transaction
	async def table_trans(self, user_id: int, num: int, time: datetime, source: str):
		with self.conn.cursor() as cursor:
			cursor.execute("""INSERT INTO transactions (user_id, num, time, source) VALUES ((SELECT id FROM users WHERE user_id=%s), %s, %s, %s) RETURNING id;""", (user_id, num, time, source))
			id = cursor.fetchone()[0]
			self.conn.commit()
			return id

	async def add_message_for_trans(self, id: int, message_id: int):
		with self.conn.cursor() as cursor:
			cursor.execute("""UPDATE transactions SET message_id = %s WHERE id = %s;""", (message_id, id))
			self.conn.commit()

	# table orders
	async def table_orders(self, id_user: int, id_message: int, week: bool, num: int):
		with self.conn.cursor() as cursor:
			cursor.execute("""INSERT INTO orders (id_user, id_message, week, num) VALUES ((SELECT id FROM users WHERE user_id=%s), %s, %s, %s);""", (id_user, id_message, week, num))
			self.conn.commit()

	async def sendMessage(self, user_id: int, send_message: bool):
		with self.conn.cursor() as cursor:
			cursor.execute("""UPDATE users SET send_message = %s WHERE user_id = %s;""", (send_message, user_id))
			self.conn.commit()

	async def add_time(self, user_id: int, time: datetime):
		with self.conn.cursor() as cursor:
			cursor.execute("""UPDATE users SET time = %s WHERE user_id = %s;""", (time, user_id))
			self.conn.commit()

	async def change_token(self, user_id: int, tokens: int, add = False):
		with self.conn.cursor() as cursor:
			if add:
				cursor.execute("""UPDATE users SET tokens = (SELECT tokens FROM users WHERE user_id = %s) + %s WHERE user_id = %s;""", (user_id, tokens, user_id))
			else:
				cursor.execute("""UPDATE users SET tokens = %s WHERE user_id = %s;""", (tokens, user_id))
			self.conn.commit()

	async def delete_trans(self, id: int):
		with self.conn.cursor() as cursor:
			cursor.execute("""DELETE FROM transactions WHERE id = %s;""", (id, ))
			self.conn.commit()

	async def delete_orders(self, id_user: int):
		with self.conn.cursor() as cursor:
			cursor.execute("""DELETE FROM orders WHERE id_user = %s;""", (id_user, ))
			self.conn.commit()

	# admins operations
	async def add_admins(self, id_user: int, name: str):
		with self.conn.cursor() as cursor:
			cursor.execute("""INSERT INTO admins (admin_id, admins_name) VALUES (%s, %s);""", (id_user, name))
			self.conn.commit()

	async def delete_admins(self, id_user: int):
		with self.conn.cursor() as cursor:
			cursor.execute("""DELETE FROM admins WHERE admin_id = %s;""", (id_user, ))
			self.conn.commit()

	async def set_user_token(self, id_user: int, admin_id: int, ):
		with self.conn.cursor() as cursor:
			cursor.execute("""UPDATE admins SET id_user = (SELECT id FROM users WHERE user_id=%s) WHERE admin_id = %s;""", (id_user, admin_id))
			self.conn.commit()

	# referrals operations
	async def add_referral(self, new_user: int, user_from: int):
		with self.conn.cursor() as cursor:
			cursor.execute("""INSERT INTO referrals (referral, user_from) VALUES (%s, (SELECT id FROM users WHERE user_id=%s));""", (new_user, user_from))
			self.conn.commit()

	async def delete_referral(self, referral: int):
		with self.conn.cursor() as cursor:
			cursor.execute("""DELETE FROM referrals WHERE referral = %s;""", (referral, ))
			self.conn.commit()

	# referrals analytics
	async def add_referral_for_analytics(self, user_id: int):
		with self.conn.cursor() as cursor:
			cursor.execute("""INSERT INTO sold_tokens (user_id) VALUES ((SELECT id FROM users WHERE user_id=%s));""", (user_id, ))
			self.conn.commit()
	
	async def add_count_for_analytics(self, user_id: int, count: int):
		with self.conn.cursor() as cursor:
			cursor.execute("""UPDATE sold_tokens SET counts=(SELECT counts FROM sold_tokens WHERE user_id=(SELECT id FROM users WHERE user_id = %s)) + %s WHERE user_id = (SELECT id FROM users WHERE user_id = %s);""", (user_id, count, user_id))
			self.conn.commit()