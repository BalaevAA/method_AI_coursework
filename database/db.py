import sqlite3


class database:
    def __init__(self, path_models):
        self.con =  sqlite3.connect(path_models, check_same_thread=False)
        self.cur = self.con.cursor()
        self.create_db()
    
    def create_db(self):
        try:
            self.cur.execute("create table models(chat_id, model_id)")
            self.con.commit()
        except:
            print("models already exists")

        try:
            self.cur.execute("create table bans(chat_id, user_id, mistakes_counts)")
            self.con.commit()
        except:
            print("bans already exists")

    def new_chat(self, chat_id):
        self.cur.execute(f"insert into models(chat_id, model_id) values({chat_id}, 1)")
        self.con.commit()

    def change_model(self, chat_id, model_id):
        self.cur.execute(f"update models set model_id={model_id} where chat_id={chat_id}")
        self.con.commit()

    def get_model_id(self, chat_id):
        try:
            res = self.cur.execute(f"select model_id from models where chat_id={chat_id}").fetchone()[0]
        except:
            self.new_chat(chat_id)
            return 1
        return res
    
    def get_ban_counts(self, chat_id, user_id):
        try:
            res = self.cur.execute(f"select mistakes_counts from bans where chat_id={chat_id} and user_id={user_id}").fetchone()[0]
        except:
            self.cur.execute(f"insert into bans(chat_id, user_id, mistakes_counts) values({chat_id}, {user_id}, 0)")
            return 0
        return res
    
    def set_ban_counts(self, chat_id, user_id, number_of_ban):
        self.cur.execute(f"update bans set mistakes_counts={number_of_ban} where user_id={user_id} and chat_id={chat_id}")
        self.con.commit() 
    
