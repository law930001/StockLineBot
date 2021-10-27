## import packages

import datetime, os, requests
from io import StringIO
import pandas as pd

from flask import (
    Flask, request, abort
)
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


##  --- initialize ---

app = Flask(__name__)

## key for line api

line_bot_api = LineBotApi('7afgitwFniNy4e8bgBVt6T/ZtMr1v5ku4S/A1e4jIwzEsEQbAsJSGZE89HX/u4wk8JMEnCXi7AKL8G7Jj5o/j9BC7ar9FlCtHBls43TsQW5EYPJ7DCv4lxV3LbZRO7YHv13rxauIM8K+ok7vMNdtYwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('bd9b74df8c4e8e12781e0d8c8d967bf9')

## --- end initialize ---

## --- dealing webhook ---

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

## --- end dealing webhook ---

## --- define function

## check if the input is valid

def isValid(validation, string_to_check):
    if string_to_check[0] != validation: # /t 1203/
        return False
    if len(string_to_check) >= 2 and string_to_check[1] != ' ': # /#1203/
        return False
    if (len(string_to_check.split(' ')) > 3): # /# 1203 2019 01/
        return False
    return True

## set the format of reply

def reply_format():
    reply_text  = "查詢格式:\n"
    reply_text += "\"# <證券代號>\"\n" 
    reply_text += "\"# <證券名稱>\"\n" 
    reply_text += "\"# <證券代號> <時間>\"\n"
    reply_text += "\"# <證券名稱> <時間>\"\n"
    reply_text += "注:若無設定時間則默認現在時間\n\n"
    reply_text += "例:\n"
    reply_text += "\"# 1203\"\n"
    reply_text += "\"# 台積電 20180108\""
    return reply_text

## return true if arg is in the first place of string_to_check

def isContain(arg, string_to_check):
    if len(string_to_check) < len(arg):
        return False
    for i in range(0,len(arg)):
        if arg[i] != string_to_check[i]:
            return False
    return True

## --- end define function

## --- meassage handler ---

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    org_text = event.message.text
    users_list = []
    # stocks_list = []

    ## initialize

    with open("users.dat", 'r') as file:
        users_list = file.readlines()

    ## add profile to users list

    if isinstance(event.source, SourceUser):
        if (event.source.user_id + "\n") not in users_list:
            users_list.append(event.source.user_id + "\n")
            with open('users.dat', 'a') as file:
                file.write(event.source.user_id + '\n')
            ## make history file
            with open("./users_history/" + str(event.source.user_id), 'w') as file:
                file.close()
    ## add in history list
    if org_text[0] == '#' or org_text[0] == '@' or org_text[0] == '&':
        with open("./users_history/" + str(event.source.user_id), 'a') as file:
            file.write(org_text + '\n')

    ## sending cat's picture

    if org_text == 'cat':
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url='https://i2.wp.com/beebom.com/wp-content/uploads/2016/01/Reverse-Image-Search-Engines-Apps-And-Its-Uses-2016.jpg?resize=640%2C426',
                preview_image_url='https://i2.wp.com/beebom.com/wp-content/uploads/2016/01/Reverse-Image-Search-Engines-Apps-And-Its-Uses-2016.jpg?resize=640%2C426'
            )
        )

    ## --- main require ---

    elif isValid("#", org_text):

        ## --- check the validation of the time ---

        today_time = datetime.datetime.now() + datetime.timedelta(hours = 8) # jet lag
        today_time_g = str(today_time.date()).replace("-", "") # 20180101

        today_year = today_time_g[0:4]
        today_month = today_time_g[4:6]
        today_date = today_time_g[6:]

        # sort the input by num of parameters

        pars = org_text.split(' ')
        num_of_par = len(pars)

        if num_of_par == 1:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text = reply_format()))
            return 0
        elif num_of_par == 2:
            if today_time.hour < 14:
                line_bot_api.push_message(event.source.user_id, TextSendMessage(text = "目前時間小於15pm，請重新查詢"))
                return 0
            date_to_check = today_time_g
        elif num_of_par == 3:
            if len(pars[2]) != 8:
                line_bot_api.push_message(event.source.user_id, TextSendMessage(text = "時間格式錯誤，請重新查詢"))
                return 0
            date_to_check = org_text.split(' ')[2]
        
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text = "日期: " + date_to_check))

        # check the validation of the date

        year = date_to_check[0:4]
        month = date_to_check[4:6]
        date = date_to_check[6:]

        # must bigger than 2004/02/11
        if int(year) < 2004:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text = "年份不能小於2004年02月11日，請重新查詢"))
            return 0
        elif int(year) == 2004 and int(month) < 2:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text = "月份不能小於2004年02月11日，請重新查詢"))
            return 0
        elif int(year) == 2004 and int(month) == 2 and int(date) < 11:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text = "日期不能小於2004年02月11日，請重新查詢"))
            return 0
        # must lower than today
        if int(year) > int(today_year):
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text = "年份不能大於今天，請重新查詢"))
            return 0
        elif int(year) == int(today_year) and int(month) > int(today_month):
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text = "月份不能大於今天，請重新查詢"))
            return 0
        elif int(year) == int(today_year) and int(month) == int(today_month) and int(date) > int(today_date):
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text = "日期不能大於今天，請重新查詢"))
            return 0
        # must not be saturday or sunday
        weekday = int(datetime.datetime(int(year), int(month), int(date)).strftime("%w"))
        if weekday == 6 or weekday == 0:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text = "該時間為星期六或日，請重新查詢"))
            return 0
        
        ## --- end check the validation of the time ---

        # get valid date
        valid_date = year + month + date

        # if not exist, then download the file
        if os.path.isfile("./csv/" + valid_date + ".csv") != True: # not exist
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text='請稍候，資料下載中...'))
            # download the stock
            timeout_int = 0
            while(1):
                try:
                    r = requests.get('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + valid_date + '&type=ALL', timeout = 20)
                    break
                except:
                    if timeout_int == 3:
                        line_bot_api.push_message(event.source.user_id, TextSendMessage(text='無回應，請稍候再嘗試'))
                        return 0
                    timeout_int += 1
                    line_bot_api.push_message(event.source.user_id, TextSendMessage(text='伺服器連線中...'))
            # turn to table
            try:
                df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                                     for i in r.text.split('\n') 
                                                     if len(i.split('",')) == 17 and i[0] != '='])
                                         ), header=0)
                # save to file
                df.to_csv("./csv/" + valid_date + ".csv", index = False)
                #reply
                reply_text = valid_date + " 資料下載完成"
                line_bot_api.push_message(event.source.user_id, TextSendMessage(text=reply_text))
            except:
                line_bot_api.push_message(event.source.user_id, TextSendMessage(text='資料不完整'))
                return 0
        
        # reply informations

        reply_text = ""
        if pars[1].isdigit(): # 以代號查詢
            df = pd.read_csv("./csv/" + valid_date + ".csv", index_col = '證券代號')
            if pars[1] in df.index:
                for i in range(0, 15):
                    reply_text += str(df.columns[i]) + ": " + str(df.loc[pars[1],df.columns[i]])
                    if i < 14:
                        reply_text += '\n'
            else:
                reply_text = "此證券代號不存在"
        else:                 # 以名稱查詢
            df = pd.read_csv("./csv/" + valid_date + ".csv", index_col = '證券名稱')
            if pars[1] in df.index:
                for i in range(0, 15):
                    reply_text += str(df.columns[i]) + ": " + str(df.loc[pars[1],df.columns[i]])
                    if i < 14:
                        reply_text += '\n'
            else:
                reply_text = "此證券名稱不存在"
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text=reply_text))

    ## --- end main require ---

    ## format

    elif org_text == "format":
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text=reply_format()))


    ## main menu

    elif org_text == "menu":
        line_bot_api.reply_message(
            event.reply_token,
            ImagemapSendMessage(
                base_url = 'https://upload.cc/i1/2019/01/16/CA1gVW.png#',
                alt_text = '請使用智慧型手機查看內容',
                base_size = BaseSize(height = 1040, width = 1040),
                actions = [
                    MessageImagemapAction(
                        text = "format",
                        area = ImagemapArea(
                            x = 0, y = 0, width = 1040, height = 346
                        )
                    ),
                    MessageImagemapAction(
                        text = "code_list",
                        area = ImagemapArea(
                            x = 0, y = 346, width = 1040, height = 346
                        )
                    ),
                    MessageImagemapAction(
                        text = "name_list",
                        area = ImagemapArea(
                            x = 0, y = 692, width = 1040, height = 346
                        )
                    )
                ]
            )
        )

    ## history list

    elif org_text == "history_list":
        reply_text = "歷史紀錄(前10個): "
        with open("./users_history/" + str(event.source.user_id), 'r') as file:
            file_list = file.readlines()
            for i in range(0, len(file_list)):
                if i == 10:
                    break
                reply_text += '\n' + file_list[len(file_list) - i - 1].strip()
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text=reply_text))

    ## code list

    elif org_text == "code_list":
        reply_text =  "證券代號列表查詢格式:\n"
        reply_text += "\"@\"\n"
        reply_text += "\"@ <數字>\"\n"
        reply_text += "\"@ 1\"\n"
        reply_text += "\"@ 12\"\n"
        reply_text += "\"@ 122\"\n"
        reply_text += "\"@ 1220\""

        line_bot_api.push_message(event.source.user_id, TextSendMessage(text=reply_text))

    elif org_text[0] == '@':
        ## check input
        if(len(org_text.split(' ')) > 2): # /@ 1 2/
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="格式錯誤，請重新輸入"))
            return 0
        if len(org_text.split(' ')[0]) != 1: # /@1/
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="格式錯誤，請重新輸入"))
            return 0

        ## valid
        reply_text = "「" + org_text + "」\n" + "以下為查詢結果:"
        if len(org_text) == 1:
            for i in range(1,10):
                reply_text += '\n' + str(i) + 'xxx'
        else:
            pars = org_text.split(' ')
            no_found = True
            with open("code_name_list.csv", "r") as file:
                file_list = file.readlines()
                for line in file_list:
                    line_split = line.strip().split(',')
                    if isContain(pars[1], line_split[0]):
                        no_found = False
                        reply_text += '\n' + line_split[0] + ' ' + line_split[1]
                if no_found == True:
                    reply_text += "\n無資料"
        try:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text=reply_text))
        except:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="資料太多無法傳送，請縮小範圍"))

    ## name list

    elif org_text == "name_list":
        reply_text =  "證券名稱查詢格式:\n"
        reply_text += "\"& <證券名稱>\""

        line_bot_api.push_message(event.source.user_id, TextSendMessage(text=reply_text))


    elif org_text[0] == '&':
        ## check input
        if(len(org_text.split(' ')) > 2): # /& 1 2/
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="格式錯誤，請重新輸入"))
            return 0
        if len(org_text.split(' ')[0]) != 1: # /&1/
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="格式錯誤，請重新輸入"))
            return 0

        ## valid
        pars = org_text.split(' ')
        if len(org_text) == 1:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="請輸入想查詢的證券名稱\n\"& <證券名稱>\""))
            return 0
        reply_text = "「" + org_text + "」\n" + "以下為查詢結果:"
        with open("code_name_list.csv", "r") as file:
            file_list = file.readlines()
            for line in file_list:
                line_split = line.strip().split(',')
                if len(line_split) == 2 and pars[1] == line_split[1]:
                    reply_text += '\n' + line_split[0] + " " + line_split[1]

        line_bot_api.push_message(event.source.user_id, TextSendMessage(text=reply_text))

    ## --- developer's options ---

    ## os

    elif org_text[0] == '!':
        os.system(org_text.replace('!', ''))

    ## send to users

    elif org_text == '$send':
        send_text = "Sending to\n"
        for uid in users_list:
            line_bot_api.push_message(uid, TextSendMessage(text='Hello'))
            send_text += uid
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=send_text))

    ## list all user

    elif org_text == '$list':
        list_text = "List\n"
        for uid in users_list:
            list_text += uid
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=list_text))

    ## delete all users profile

    elif org_text == '$delete':
        delete_text = "Deleting all " + str(len(users_list)) +  " users\n"
        for user in range(0, len(users_list)):
            delete_text += users_list[user]
        with open("users.dat", 'w') as file:
            file.close()        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=delete_text))

    ## --- end controler options---

    ## else commands' reply

    else :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='此指令不存在，請檢查指令')
        )

## --- end meassage handler ---

## run the app

if __name__ == "__main__":
    app.run()





