from dotenv import load_dotenv
import re
from pypika import Query, Table, Field
import mysql.connector
import src.model.error
from passlib.context import CryptContext
import os, binascii
from pydantic import BaseModel
from typing import Annotated, Union
from datetime import datetime
from src.model import user
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

db_user_name = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')

mydb = mysql.connector.connect(
  host="neo-tool.net",
  user=db_user_name,
  password=db_password,
  database="NeoToolTest"
)

def check_if_sql_input_is_unsafe(input: str):
    if input.find('--') != -1:
        return True
    if input.find(';') != -1:
        return True
    if re.search("/[\t\r\n]|(--[^\r\n]*)|(\/\*[\w\W]*?(?=\*)\*\/)/gi", input):
        return True
    return False

def create_new_api_key(user_id):
    if check_if_sql_input_is_unsafe(str(user_id)):
        return False
    users = Table('users')
    api_key = binascii.b2a_hex(os.urandom(48)).decode('utf-8')
    hashed_api_key = pwd_context.hash(api_key)
    sql = Query.update(users).set(users.API_KEY, hashed_api_key).where(users.iduser == user_id)
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(str(sql).replace('"', ''))
    mydb.commit()
    return api_key
#print(create_new_api_key(6))
def get_user(table, username: str):
    if check_if_sql_input_is_unsafe(username):
        return False
    user_table = Table(table)
    sql = Query.from_(user_table).select(
        user_table.iduser, 
        user_table.gge_id, 
        user_table.gge_name, 
        user_table.gge_world,
        user_table.sub, 
        user_table.client, 
        user_table.telegram_id, 
        user_table.last_ip,
        user_table.last_socket_id, 
        user_table.gge_connection, 
        user_table.lts, 
        user_table.api_key
        ).where(
        user_table.gge_name == username
        )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(str(sql).replace('"', ''))
    result_set = cursor.fetchone()

    return user.User(**result_set)