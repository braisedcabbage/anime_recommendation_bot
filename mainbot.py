import telebot
from jikanpy import Jikan
import pandas as pd
import requests
from random import choice
import config  # put your token in config file!!!
from telebot import types
from bs4 import BeautifulSoup

jikan = Jikan()
all_genres = jikan.genres(type='anime')['data']
list_of_genres = [g['name'].lower() for g in all_genres]
list_of_ids = [g['mal_id'] for g in all_genres]
genre_and_anime = pd.DataFrame({'id': list_of_ids}, index=list_of_genres)
bot = telebot.TeleBot(config.token)
genre = []


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     "Hello! I'll send you a list of anime genres now and you can choose the one you wanna watch, just type it here. I'll send you a link to a random anime of that genre")
    bot.send_message(message.chat.id, "\n".join(list_of_genres))


@bot.message_handler(commands=['help'])
def bot_help(message):
    bot.send_message(message.chat.id, 'To get a recommendation, choose one genre from the list and type it')


@bot.message_handler(commands=['list'])
def see_list(message):
    bot.send_message(message.chat.id, "\n".join(list_of_genres))


@bot.message_handler(content_types=['text'])
def ask_score(message):
    genre.append(message.text.lower())
    if genre[-1] not in list_of_genres:
        bot.send_message(message.chat.id, 'You probably typed it wrong')
        genre.clear()
        return
    markup = types.InlineKeyboardMarkup(row_width=3)
    item1, item2, item3, item4, item5, item6, item7, item8, item9 = types.InlineKeyboardButton(
        '1', callback_data=1), types.InlineKeyboardButton('2', callback_data=2), types.InlineKeyboardButton('3',
                                                                                                            callback_data=3), types.InlineKeyboardButton(
        '4', callback_data=4), types.InlineKeyboardButton('5', callback_data=5), types.InlineKeyboardButton('6',
                                                                                                            callback_data=6), types.InlineKeyboardButton(
        '7', callback_data=7), types.InlineKeyboardButton('8', callback_data=8), types.InlineKeyboardButton('9',
                                                                                                            callback_data=9)
    markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
    bot.send_message(message.chat.id, 'Tell me the minimum score of an anime you wanna see', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def choose_anime(call):
    try:
        if call.message:
            try:
                genre_id = genre_and_anime.loc[genre[-1]]['id']
                link = f'https://myanimelist.net/anime.php?cat=anime&q=&type=0&score={call.data}&status=0&p=0&r=0&sm=0&sd=0&sy=0&em=0&ed' \
                       f'=0&ey=0&c%5B%5D=a&c%5B%5D=b&c%5B%5D=c&c%5B%5D=f&genre%5B%5D={genre_id}'
                anime = requests.get(link)
                table = BeautifulSoup(anime.text, 'lxml')
                table = table.find('div', class_="js-categories-seasonal js-block-list list")
                table = table.find_all('a', class_='hoverinfo_trigger fw-b fl-l')
                link_list = [anime['href'] for anime in table]
                bot.send_message(call.message.chat.id, choice(link_list))
            except AttributeError:
                bot.send_message(call.message.chat.id, 'Try again, probably this score is too high')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Tell me the minimum score of an anime you wanna see', reply_markup=None)
    except Exception as e:
        print(repr(e))
    finally:
        genre.clear()


bot.polling(non_stop=True)
