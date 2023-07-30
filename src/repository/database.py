from dotenv import load_dotenv
import re
from pypika import Query, Table, Field, Order
import mysql.connector
import src.model.error
from passlib.context import CryptContext
import os, binascii
from pydantic import BaseModel
from typing import Annotated, Union
from datetime import datetime
from src.model import user, subscription, metadata
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()
APP_DATA = 'app_data'
db_user_name = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
try:
    mydb = mysql.connector.connect(
    host="neo-tool.net",
    user=db_user_name,
    password=db_password,
    database="NeoToolTest"
    )
except Exception:
    print(Exception)


def execute_sql_fetch_one(sql: str) -> dict:
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(str(sql).replace('"', ''))
    mydb.commit()
    return cursor.fetchone()

def execute_sql_fetch_all(sql: str) -> dict:
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(str(sql).replace('"', ''))
    mydb.commit()
    return cursor.fetchall()

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
    execute_sql_fetch_one(sql)
    return api_key
#print(create_new_api_key(6))
def create_new_user(table:str, user:user.User):
    sql = Query.into(table).columns(
        'gge_id',
        'gge_name',
        'gge_world',
        'sub',
        'client',
        'telegram_id',
        'last_ip',
        'last_socket',
        'online'
        ).insert(
            app_version.app_version, 
            app_version.cdata)
    
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
        user_table.online, 
        user_table.lts, 
        user_table.api_key
        ).where(
        user_table.gge_name == username
        )
    return user.User(**execute_sql_fetch_one(sql))

def is_user_allowed(user: user.User, client_required:int) -> bool:
    if user.sub < datetime.now():
        return False
    if user.client >= client_required:
        return True
    return False
def get_logs_of_user():
    ...

def update_subscription(user: user.User, new_sub:subscription.Sub):
    client, sub = subscription.Sub(user.client, user.sub).convert_sub(new_sub.client, new_sub.sub_in_days)
    ...

def update_telegram_id(user:user.User, telegram_id:int):
    if user.telegram_id != telegram_id:
        users_table = Table('users')
        sql = Query.update(users_table).set(users_table.telegram_id, telegram_id).where(users_table.iduser == user.iduser)
        execute_sql_fetch_one(sql)
        return True
    return False

def update_app_version(app_version: metadata.AppVersion):
    sql = Query.into('app_data').columns(
        'app_version',
        'cdata'
        ).insert(app_version.app_version, app_version.cdata)
    return execute_sql_fetch_one(sql)
def get_last_app_data():
    app_data_table = Table(APP_DATA)
    sql = Query.from_(app_data_table).select(
        app_data_table.id, 
        app_data_table.app_version, 
        app_data_table.cdata, 
        app_data_table.date
        ).orderby('id', order=Order.desc)
    return metadata.AppVersion(**execute_sql_fetch_one(sql))
def update_app_cdata(new_version: metadata.AppVersion) -> bool:
    last_app_version = get_last_app_data()
    if last_app_version.cdata != new_version.cdata:
        app_data_table = Table(APP_DATA)
        sql = Query.update(app_data_table).set(app_data_table.cdata, new_version.cdata).where(app_data_table.id == last_app_version.id)
        execute_sql_fetch_one(sql)
        return True
    return False
