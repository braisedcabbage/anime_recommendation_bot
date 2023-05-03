import telebot
from jikanpy import Jikan
import pandas as pd
import requests
from random import choice
import config  # put your token in config file!!!

jikan = Jikan()
all_genres = jikan.genres(type='anime')['data']
list_of_genres = [g['name'] for g in all_genres]
list_of_urls = [g['url'] for g in all_genres]
animes = [[] for g in all_genres]
for i in range(len(all_genres)):
    page = requests.get(all_genres[i]['url'])
    page_data = page.text.split("h2_anime_title")
    for k in range(1, len(page_data)):
        j = 0
        while page_data[k][j] != '=' and j < len(page_data[k]):
            j += 1
        j += 2
        link = ""
        while page_data[k][j] != '\"' and page_data[k][j] != "\'":
            link += page_data[k][j]
            j += 1
        animes[i].append(link)
# <h2 class="h2_anime_title"><a href="   !!!!!!!!!!
genre_and_anime = pd.DataFrame({'url': list_of_urls, 'animes': animes}, index=list_of_genres)
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     "Hello! I'll send you a list of anime genres now and you can choose the one you wanna watch. I'll send you a link to a random anime of that genre")
    bot.send_message(message.chat.id, "\n".join(list_of_genres))


@bot.message_handler(content_types=['text'])
def send_link(message):
    try:
        bot.send_message(message.chat.id, choice(genre_and_anime.loc[message.text]['animes']))
    except KeyError:
        bot.send_message(message.chat.id, 'You probably typed it wrong')


bot.polling(non_stop=True)
