import mysql.connector

class DataBase():
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="sql3.freesqldatabase.com",
            user="sql3512526",
            password="rSDMzrZLp1",
            database="sql3512526",
            )
        self.cursor = self.mydb.cursor()

    def add_column(self,table_name,column_name,data_type):
        update_table = (f"ALTER TABLE {table_name} ADD {column_name} {data_type}")
        self.cursor.execute(update_table)

        self.mydb.commit()

    def retrive_user_Info(self,user_ID,password):
        output = []
        find = (f"SELECT * FROM Users WHERE id= BINARY '{user_ID}' AND password= BINARY '{password}'")
        try:
            self.cursor.execute(find)
        except:
            print('fail to login')
            return output
        else:
            print('logged in')
            for i in self.cursor:
                return i
            

    def check_user_exists(self,table,user_ID):
        find = (f"SELECT * FROM {table} WHERE id= BINARY '{user_ID}'")
        try:
            self.cursor.execute(find)
        except:
            print('error')
            return False
        else:
            output = []
            for i in self.cursor:
                output.append(i)
            if len(output) != 0:
                print('user does exist')
                return True
            else:
                print('user do not exist')
                return False

    def exercute_raw_SQL(self,command=""):
        self.cursor.execute(command)
        self.mydb.commit()

    def close_db(self):
        self.mydb.close()
        self.cursor.close()