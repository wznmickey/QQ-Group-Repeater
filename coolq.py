from aiocqhttp import CQHttp, ApiError, jsonify, request
import os
import random
from Repeater import Repeater
import logging
import asyncio
import time
from util import load_json, purgeMsg
from datetime import datetime, timezone,timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from queue import Queue
from pytz import timezone
used_timezone=timezone('Asia/Shanghai')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=os.path.join(os.path.abspath(os.path.dirname(__file__)),
                          'coolq.log'),
    filemode='w+')

bot = CQHttp(api_root='http://127.0.0.1:5700/')

GroupDict = dict()
SETTINGS = load_json('settings.json')
REPLY = load_json('data/reply.json')
msgQueue = Queue()

#app = bot.server_app
# @app.route('/danmu/coolq')
# async def danmu():
#    if request.remote_addr and request.remote_addr != '127.0.0.1':
#        return None
#    re = []
#    while not msgQueue.empty():
#        re.append(msgQueue.get())
#    return jsonify(re)


@bot.on_message('private')
async def handle_private(context):
    # await bot.send(context, message=context['message'])
    # if context['user_id'] in SETTINGS['ADMIN']:
    #    for group_id in SETTINGS['REPOST_GROUP']:
    #        await bot.send({'group_id': group_id}, message=context['message'])
    # else
    try:
        re = await Repeater().responseMsg(context)
        print({"msg": context['message'], "ans": re})
        await bot.send({'user_id': context['user_id']}, message=re) if (len(re) > 0) else 0
    except Exception as e:
        print({"msg": context['message'], "ans": "ERROR"})
        logging.exception(e)


@bot.on_message('group')
async def handle_msg(context):
    
    groupId = context['group_id']
     
    #if groupId in SETTINGS['DANMU_GROUP']:
    #    msgQueue.put({
    #        'sender': context['user_id'],
    #        'msg': context['message']
    #        # 'msg': purgeMsg(context['message'])
    #    })
    
    if groupId not in SETTINGS['ALLOW_GROUP']:
        
        return
   
    global GroupDict
    try:
        if (GroupDict.get(groupId) == None):
            GroupDict[groupId] = Repeater()
        re = await GroupDict[groupId].responseMsg(context)
        print({"msg": context['message'], "ans": re})
        await bot.send({'group_id': groupId}, message=re) if (len(re) > 0) else 0
    except Exception as e:
        print({"msg": context['message'], "ans": "ERROR"})
        logging.exception(e)


@bot.on_notice('group_increase')
async def handle_group_increase(context):
    if context['group_id'] not in SETTINGS['ALLOW_GROUP']:
        return
    re = random.choice(REPLY['on_group_increase'])
    await bot.send(context, message=re, auto_escape=True)


@bot.on_request('group', 'friend')
async def handle_group_request(context):
    return {'approve': True}


async def send_early_msg():
    #await 
    time.sleep(int(random.random() * 0) + 15)
    print(string_datetime)
    for group_id in SETTINGS['MEMTION_GROUP']:
        time.sleep(int(random.random() * 0) + 15)
        time_format = '%Y-%m-%d %H:%M:%S'
        show_datetime = datetime.now(used_timezone)
        string_datetime = show_datetime.strftime(time_format)
        re = random.choice(REPLY['on_early'])
        await bot.send({'group_id': group_id}, message=(re+'当前时间为'+string_datetime))


async def send_new_day_msg():
    for group_id in SETTINGS['MEMTION_GROUP']:
        re = random.choice(REPLY['on_new_day'])
        time.sleep(int(random.random() * 0) + 15)
        await bot.send({'group_id': group_id}, message=re)


def sche():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_early_msg, 'cron', hour='07', minute='45' ,timezone=used_timezone) 
    scheduler.add_job(send_new_day_msg, 'cron', hour='00', minute='00',timezone=used_timezone)
    scheduler.start()


if __name__ == '__main__':
    sche() 
    bot.run(host='0.0.0.0', port=8090)
    
