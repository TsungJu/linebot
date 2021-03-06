# -*- coding: utf-8 -*-
# 載入需要的模組
from __future__ import unicode_literals
import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

import configparser
import urllib
import re
import random
import psycopg2

from flask import render_template

app = Flask(__name__)

# LINE bot information
config = configparser.ConfigParser()
config.read('config.ini')
line_bot_api = LineBotApi(config.get('line-bot','channel_access_token'))
handler = WebhookHandler(config.get('line-bot','channel_secret'))

# For wake heroku app up
@app.route("/")
def wake():
    return render_template("wake.html")

def prepare_username_check(text):
    text_list = text.split(':')
    username = text_list[1]
    return username

def username_check(username):
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    postgres_check_query = f"""
        SELECT count(username)
        FROM account
        WHERE username = '{username}';
    """

    cursor.execute(postgres_check_query)
    username_count = cursor.fetchone()
    if username_count[0] == 0:
        return False
    else:
        return True

# Receive LINE information
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# learn you how to talk
@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        if event.message.text == "Does igogosport marley put on the shelf...":
            request_page1 = requests.get("https://store.igogosport.com/collections/refurbish?page=1")
            request_page2 = requests.get("https://store.igogosport.com/collections/refurbish?page=2")
            if 'Marley Liberate Air' in request_page1.text or 'Marley Liberate Air' in request_page2.text:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text='Marley Liberate Air put on the shelf'))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text='No Not Yet'))
        elif "Google image : " in event.message.text:
            try:
                images = event.message.text.split(':')
                q_string = {'tbm':'isch','q':images[1]}
                url = f"https://www.google.com/search?{urllib.parse.urlencode(q_string)}/"
                headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
                req = urllib.request.Request(url,headers = headers)
                conn = urllib.request.urlopen(req)
                print('[API Log] fetch conn finish')

                pattern = 'img data-src="\S*"'
                img_list = []

                for match in re.finditer(pattern,str(conn.read())):
                    img_list.append(match.group()[14:-1])
                
                random_img_url = img_list[random.randint(0,len(img_list)+1)]
                print('[API Log] fetch img url finish')

                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        original_content_url=random_img_url,
                        preview_image_url=random_img_url
                    )
                )

                #For split test
                #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=images[1]))
            except:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))
        elif event.message.text == "check user_id":
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=str(event.source.user_id)))
        elif "Is username exist check:" in event.message.text:
            username = prepare_username_check(event.message.text)
            reply = username_check(username)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=str(reply)))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run()