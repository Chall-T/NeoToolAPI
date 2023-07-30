from dotenv import load_dotenv
import re
from pypika import Query, Table, Field, Order, Tables
import mysql.connector
#import src.model.error
from passlib.context import CryptContext
from fastapi import HTTPException
import os, binascii
from pydantic import BaseModel
from typing import Annotated, Union, Type
from datetime import datetime
from ..model import user as user_model
from ..model import subscription as subscription_model
from ..model import metadata as metadata_model
from ..model import error as error_model
#print(dir(user_model.User))
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


def execute_sql_fetch_one(sql: str, is_returning: bool = True) -> dict:
    cursor = mydb.cursor(dictionary=True, buffered=True)
    cursor.execute(str(sql).replace('"', ''))
    mydb.commit()
    result = cursor.fetchone()
    if not result and is_returning:
        raise HTTPException(status_code=404, detail="Data not found")
    return result

def execute_sql_fetch_all(sql: str, is_returning: bool = True) -> dict:
    cursor = mydb.cursor(dictionary=True, buffered=True)
    cursor.execute(str(sql).replace('"', ''))
    mydb.commit()
    result = cursor.fetchall()
    if not result and not is_returning:
        raise HTTPException(status_code=404, detail="Data not found")
    return result

def check_if_sql_input_is_unsafe(input: str):
    if input.find('--') != -1:
        raise HTTPException(status_code=400, detail="Bad input")
    if input.find(';') != -1:
        raise HTTPException(status_code=400, detail="Bad input")
    if re.search("/[\t\r\n]|(--[^\r\n]*)|(\/\*[\w\W]*?(?=\*)\*\/)/gi", input):
        raise HTTPException(status_code=400, detail="Bad input")
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
def create_new_user(table:str, user: 'Type[user_model.User]'):
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
    result = execute_sql_fetch_one(sql)
    try:
        return user_model.User(**result)
    except:
        raise HTTPException(status_code=500, detail="error with getting the user")
def get_user_by_id(table, iduser: int):
    if check_if_sql_input_is_unsafe(iduser):
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
        user_table.iduser == iduser
        )
    result = execute_sql_fetch_one(sql)
    try:
        return user_model.User(**result)
    except:
        raise HTTPException(status_code=500, detail="error with getting the user")

def is_user_allowed(user: 'Type[user_model.User]', client_required:int) -> bool:
    if user.sub < datetime.now():
        return False
    if user.client >= client_required:
        return True
    return False
def get_logs_of_user():
    ...
def get_stats_of_user(user: 'Type[user_model.User]'):
    #events = get_all_event_names()
    
    stats_table, events = Tables('user_stats', 'events')
    sql = Query.from_(stats_table).join(
            events
        ).on(
            events.id == stats_table.event_id
        ).select(
            stats_table.id, 
            stats_table.iduser,
            (events.name).as_('event_name'),
            stats_table.event_id, 
            stats_table.count, 
            stats_table.created
        ).where(
            stats_table.iduser == user.iduser
        )
    result = execute_sql_fetch_all(sql)
    print(type(result))
    print(f'Result: {result}')
    user_stats = user_model.User_stats()
    for stat in result:
        user_stats.add_new_stat(stat)
    return user_stats

def get_all_event_names():
    events_table = Table('events')
    sql = Query.from_(events_table).select(
        events_table.id, 
        events_table.name, 
        )
    result = execute_sql_fetch_all(sql)
    stat_events = user_model.StatEvents()
    for event in result:
        stat_events.add_new_stat(user_model.StatEvent(event))
    return stat_events

def get_event_by_name(event_name:str):
    check_if_sql_input_is_unsafe(event_name)
    events_table = Table('events')
    sql = Query.from_(events_table).select(
        events_table.id, 
        events_table.name, 
        ).where(
        events_table.name == event_name
        )
    return user_model.StatEvent(**execute_sql_fetch_one(sql))

def get_event_by_id(event_id:int):
    events_table = Table('events')
    sql = Query.from_(events_table).select(
        events_table.id, 
        events_table.name, 
        ).where(
        events_table.id == event_id
        )
    return user_model.StatEvent(execute_sql_fetch_one(sql))

def create_new_stat_for_user(user: 'Type[user_model.User]', user_stat: 'Type[user_model.User_stat]'):
    check_if_sql_input_is_unsafe(str(user_stat.count))
    
    sql = Query.into('user_stats').columns(
        'iduser',
        'event_id',
        'count'
        ).insert(user.iduser, user_stat.event_id, user_stat.count)
    return execute_sql_fetch_one(sql, is_returning = False)
def update_subscription(user: 'Type[user_model.User]', new_sub):
    client, sub = subscription_model.Sub(user.client, user.sub).convert_sub(new_sub.client, new_sub.sub_in_days)
    ...

def update_telegram_id(user: 'Type[user_model.User]', telegram_id:int):
    if user.telegram_id != telegram_id:
        users_table = Table('users')
        sql = Query.update(users_table).set(users_table.telegram_id, telegram_id).where(users_table.iduser == user.iduser)
        execute_sql_fetch_one(sql)
        return True
    return False

def update_app_version(app_version: 'Type[metadata_model.AppVersion]'):
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
    return metadata_model.AppVersion(**execute_sql_fetch_one(sql))
def update_app_cdata(new_version: 'Type[metadata_model.AppVersion]') -> bool:
    last_app_version = get_last_app_data()
    if last_app_version.cdata != new_version.cdata:
        app_data_table = Table(APP_DATA)
        sql = Query.update(app_data_table).set(app_data_table.cdata, new_version.cdata).where(app_data_table.id == last_app_version.id)
        execute_sql_fetch_one(sql)
        return True
    return False
