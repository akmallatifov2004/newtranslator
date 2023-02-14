from flask import Flask, request

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from deep_translator import GoogleTranslator#, DeepL
from gtts import gTTS
from PIL import Image
import pytesseract

import time, os

secret = "1234"
TOKEN = "1234"
bot = telebot.TeleBot(TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url="https://username.pythonanywhere.com/{}".format(secret))


app = Flask(__name__)

@app.route('/{}'.format(secret), methods=["POST"])
def telegram_webhook():
    req = request.stream.read().decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(req)])
    return "200"


class msgtexts:
    greeting = '''
<b>Отправьте любой текст на любом языке</b>
<b>Или отправьте фото с английским текстом</b>

<i>для дополнительной информации нажмите </i> /info
'''
    info = '''
• Перевод текста (язык текста определяется автоматически)
• Перевод текста из фото (пока распознаёт только английский)
• Озвучка переведенного текста
• Инлайн режим

<b>сервер:</b> <code>pythonanywhere</code>
<b>язык:</b> <code>Python</code>
<b>API:</b> <code>Google Translate</code>

@akmal_tg  @akibots
'''

users = []
users_firstname = {}

@bot.message_handler(commands=['start', 'help'])
def command_hello(message):
    bot.reply_to(message, msgtexts.greeting, parse_mode='html')

@bot.message_handler(commands=['info'])
def command_info(message):
    bot.reply_to(message, msgtexts.info, parse_mode='html')

@bot.message_handler(commands=['showusers'])
def command_showusers(message):
    try:
        global users, users_firstname
        text = ''
        for id in users:
    	    text += (f'<a href="tg://user?id={id}">{users_firstname[id]}</a>; ')
        bot.send_message(message.chat.id, text, parse_mode='html')
    except Exception as e:
        bot.send_message(message.chat.id, e, parse_mode='html')

@bot.message_handler(content_types=['text'])
def getuserstext(message):
    global users, users_firstname

    if message.chat.id not in users:
        try:
            users.append(message.chat.id)
            users_firstname[message.chat.id] = str(message.from_user.first_name)

            print(message.from_user.first_name, message.chat.id)
        except Exception as e:
            print(e)


    try:
        statuses = ['creator', 'administrator', 'member']
        user_status = bot.get_chat_member(chat_id='@akibots', user_id=message.from_user.id).status

        if user_status in statuses:
            pass
        else:
            bot.send_message(message.chat.id, 'Чтобы пользоваться ботом, пожалуйста подпишитесь на наш канал @akibots ✅')
            return
    except Exception as channel_member_error:
        print('channel_member_error:', channel_member_error)


    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Русский / Russian", callback_data="ru"))
    markup.add(InlineKeyboardButton("Английский / English", callback_data="en"))
    markup.add(InlineKeyboardButton("Французский / Français", callback_data="fr"))
    markup.add(InlineKeyboardButton("Немецкий / Deutsch", callback_data="de"))
    markup.add(InlineKeyboardButton("Корейский / 한국인", callback_data="ko"))
    markup.add(InlineKeyboardButton("Турецкий / Türk", callback_data="tr"))
    markup.add(InlineKeyboardButton("Арабский / عرب", callback_data="ar"))

    text = f'<code>{message.text}</code>'
    bot.reply_to(message, text, reply_markup=markup, parse_mode='html')

@bot.message_handler(content_types=['photo'])
def photo_translate(message):
    try:
        bot.send_message(message.chat.id, f'<b>загрузка 🔄</b>', parse_mode='html')

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = (f'img_tt_{message.chat.id}_{int(time.time())}.jpg')

        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
        text = pytesseract.image_to_string(Image.open(file_name))

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Русский / Russian", callback_data="ru"))
        markup.add(InlineKeyboardButton("Английский / English", callback_data="en"))
        markup.add(InlineKeyboardButton("Французский / Français", callback_data="fr"))
        markup.add(InlineKeyboardButton("Немецкий / Deutsch", callback_data="de"))
        markup.add(InlineKeyboardButton("Корейский / 한국인", callback_data="ko"))
        markup.add(InlineKeyboardButton("Турецкий / Türk", callback_data="tr"))
        markup.add(InlineKeyboardButton("Арабский / عرب", callback_data="ar"))

        text = f'<code>{str(text)}</code>'
        bot.reply_to(message, text, reply_markup=markup, parse_mode='html')

        try:
            os.remove(file_name)
        except:
            pass

    except Exception as photo_translate_error:
        bot.reply_to(message, '⚠️ ошибка')
        print('photo_translate_error: ', photo_translate_error)

def translatetext(message, language):
    try:
        translated = GoogleTranslator(source='auto', target=language).translate(message.text)
        bot.send_message(message.chat.id, f'<code>{translated}</code>', parse_mode='html')
        ttstext(message, translated, language)
        return translated
    except Exception as e:
        return f'ошибка! {e}'


def ttstext(message, sentence, lng):
    try:
        filename = ('tts_' + f'{message.chat.id}_{int(time.time())}.ogg')

        speech = gTTS(text=sentence, lang=lng, slow=False)
        speech.save(filename)

        with open(filename, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)

        try:
            os.remove(filename)
        except Exception as e:
            print(e)
    except Exception as e:
        bot.send_message(message.chat.id, f'ошибка! {e}')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

    if call.data == 'ru':
        translatetext(call.message, 'ru')
    elif call.data == 'en':
        translatetext(call.message, 'en')
    elif call.data == 'fr':
        translatetext(call.message, 'fr')
    elif call.data == 'de':
        translatetext(call.message, 'de')
    elif call.data == 'ko':
        translatetext(call.message, 'ko')
    elif call.data == 'tr':
        translatetext(call.message, 'tr')
    elif call.data == 'ar':
        translatetext(call.message, 'ar')


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(query):
    global users, users_firstname
    try:
        text = query.query

        global users, users_firstname
        if query.from_user.id not in users:
            try:
                users.append(query.from_user.id)
                users_firstname[query.from_user.id] = str(query.from_user.first_name)

                print(query.from_user.first_name, query.from_user.id)
            except Exception as e:
                print(e)


        try:
            statuses = ['creator', 'administrator', 'member']
            user_status = bot.get_chat_member(chat_id='@akibots', user_id=query.from_user.id).status

            if user_status in statuses:
                pass
            else:
                substext = 'Чтобы пользоваться ботом, пожалуйста подпишитесь на наш канал @akibots ✅'

                subscr = types.InlineQueryResultArticle(
                id='1', title="Подпишитесь",
                description=substext,
                input_message_content=types.InputTextMessageContent(
                message_text=substext, parse_mode='html')
                )

                bot.answer_inline_query(query.id, [subscr])
        except Exception as channel_member_error:
            print('channel_member_error:', channel_member_error)


        rutext = GoogleTranslator(source='auto', target='ru').translate(text)
        ru = types.InlineQueryResultArticle(
                id='1', title="Русский",
                description=rutext,
                input_message_content=types.InputTextMessageContent(
                message_text=rutext, parse_mode='html')
        )
        entext = GoogleTranslator(source='auto', target='en').translate(text)
        en = types.InlineQueryResultArticle(
                id='2', title="Английский / English",
                description=entext,
                input_message_content=types.InputTextMessageContent(
                message_text=entext, parse_mode='html')
        )
        frtext = GoogleTranslator(source='auto', target='fr').translate(text)
        fr = types.InlineQueryResultArticle(
                id='3', title="Французский / Français",
                description=frtext,
                input_message_content=types.InputTextMessageContent(
                message_text=frtext, parse_mode='html')
        )
        detext = GoogleTranslator(source='auto', target='de').translate(text)
        de = types.InlineQueryResultArticle(
                id='4', title="Немецкий / Deutsch",
                description=detext,
                input_message_content=types.InputTextMessageContent(
                message_text=detext, parse_mode='html')
        )
        kotext = GoogleTranslator(source='auto', target='ko').translate(text)
        ko = types.InlineQueryResultArticle(
                id='5', title="Корейский / 한국인",
                description=kotext,
                input_message_content=types.InputTextMessageContent(
                message_text=kotext, parse_mode='html')
        )
        trtext = GoogleTranslator(source='auto', target='tr').translate(text)
        tr = types.InlineQueryResultArticle(
                id='6', title="Турецкий / Türk",
                description=trtext,
                input_message_content=types.InputTextMessageContent(
                message_text=trtext, parse_mode='html')
        )
        artext = GoogleTranslator(source='auto', target='ar').translate(text)
        ar = types.InlineQueryResultArticle(
                id='7', title="Арабский / عرب",
                description=artext,
                input_message_content=types.InputTextMessageContent(
                message_text=artext, parse_mode='html')
        )

        bot.answer_inline_query(query.id, [ru, en, fr, de, ko, tr, ar])
    except Exception as e:
        print(e)

print("bot has been started")
# bot.polling(none_stop=True)
