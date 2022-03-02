from database import Database
db = Database()

class Check:
    async def isUser(self, user_id: int):
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT EXISTS(SELECT user_id FROM users WHERE user_id=%s);""", (user_id, ))
            user = cursor.fetchone()[0]
            return user # Found in database

    async def isAdmin(self, user_id: int):
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT EXISTS(SELECT id FROM admins WHERE admin_id=%s);""", (user_id, ))
            user = cursor.fetchone()[0]
            return user # Found in database
        
    async def isReferral(self, user_id: int):
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT EXISTS(SELECT id FROM referrals WHERE referral=%s);""", (user_id, ))
            user = cursor.fetchone()[0]
            return user # Found in database
    
    async def isReferrer(self, user_id: str):
        if not user_id.isdigit():
            return False
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT EXISTS(SELECT id FROM sold_tokens WHERE user_id=(SELECT id FROM users WHERE user_id=%s));""", (int(user_id), ))
            user = cursor.fetchone()[0]
            return user # Found in database

    async def onStart(self, referrer: str, referral: int):
        if not referrer.isdigit():
            return False
        with db.conn.cursor() as cursor:
            cursor.execute("""SELECT EXISTS(SELECT id FROM users WHERE user_id=%s) UNION SELECT NOT EXISTS(SELECT id FROM referrals WHERE referral=%s);""", (int(referrer), referral))
            users = cursor.fetchall()
            if len(users) == 1:
                return(users[0][0])
            else:
                return False