import telebot
from telebot import types
from questions import EnglishQuestions
import logging
from boto.s3.connection import S3Connection
import os
print(os.environ)

s3 = S3Connection(os.environ['bot_token'])
bot = telebot.TeleBot(bot_token)

logging.basicConfig(level=logging.INFO)
user_dict = {"test_started":"False",
			"test_finished":"False",
			"message_chat_id":"", 
			"test":"","level":0,
			 "question_number":0,
			 "right_results":0,
			 "wrong_results":0,
			 "sum":0}

class User:
    def __init__(self, name):
        self.right_results = right_results
        self.wrong_results = None
        self.sum = None


@bot.message_handler(commands=['test', 'q'])
def say_hello(message):
    logging.info('def say_hello')


    markup = telebot.types.InlineKeyboardMarkup()
    item_yes = types.InlineKeyboardButton(text='Yes, sure!', callback_data = 'yes')
    item_no = types.InlineKeyboardButton(text='Not now, sorry!', callback_data = 'no')
    markup.row(item_yes, item_no)
    
    bot.send_message(message.chat.id, text="Hi, dear! Let's start the test?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def check_hello(call):
    logging.info('def check_hello(call)')
    if call.data == 'yes':
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.id, text = "Super!\n\
Ready! Steady! Go!")
        user_dict["test_started"] = True
        user_dict["test_finished"] = False
        user_dict ["test"] = ''
        user_dict["level"] = 0
        user_dict ["question_number"] = 0
        user_dict["right_results"] = 0
        user_dict["wrong_results"] = 0
        user_dict["sum"] = 0
        ask_level(call)
    elif call.data == 'no':
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.id, text = "Maybe next time. Goodbye, dear!")

    else:
        get_level(call)
   
@bot.callback_query_handler(func=lambda call: True)
def get_level(call):
    logging.info('def get_level(call)')
    if call.data == '1':
       test = EnglishQuestions.level_1
       user_dict["test"]=test
       user_dict["level"] = 1
       bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.id, text = f"Answer {len(test)} questions, dear!")
       ask_question_step(call.message)

    elif call.data == '2':
        test = EnglishQuestions.level_2
        user_dict["test"]=test
        user_dict["level"] = 2
        ask_question_step(call.message)

    elif call.data == '3':
        test = EnglishQuestions.level_3
        user_dict["test"]=test
        user_dict["level"] = 3
        ask_question_step(call.message)
    else:
        check_answer_step(call)

@bot.callback_query_handler(func=lambda call: True)
def check_answer_step(call):
        logging.info("check_answer_step(call)")
        question_number = user_dict['question_number']
        if call.data == user_dict['test'][question_number]['right_answer'] and question_number < len(user_dict['test']):       
            answer = f"Congrats! \n\
The answer '{user_dict['test'][question_number]['right_answer']}' is correct!"
            bot.send_message(call.message.chat.id, answer)
            user_dict ['right_results'] += 1
            user_dict ['sum'] += 1
            user_dict['question_number'] += 1
            question_number = user_dict['question_number']
            if question_number < len(user_dict['test']):
                ask_question_step(call.message)
            else:           
                bot.send_message(call.message.chat.id, \
                    f"The test is over!\n\
Your result:\n\
right answers: {user_dict['right_results']} \n\
wrong answers: {user_dict['wrong_results']} \n\
total number of questions: {user_dict['sum']}")
                user_dict["test_finished"] = True
                user_dict["message_chat_id"] = call.message.chat.id
                send_result()


        elif call.data != user_dict['test'][question_number]['right_answer'] and question_number < len(user_dict['test']): 
            answer = f"I'm sorry! It's false! \n\
The answer '{user_dict['test'][question_number]['right_answer']}' was correct!"
            bot.send_message(call.message.chat.id, answer)
            user_dict ['wrong_results'] += 1
            user_dict['question_number'] += 1
            user_dict ['sum'] += 1
            question_number = user_dict['question_number']
            if question_number < len(user_dict['test']):
                ask_question_step(call.message)
            else: 
                bot.send_message(call.message.chat.id, \
                    f"The test is over!\n\
Your result:\n\
right answers: {user_dict['right_results']} \n\
wrong answers: {user_dict['wrong_results']} \n\
total number of questions: {user_dict['sum']}")
                user_dict["test_finished"] = True
                user_dict["message_chat_id"] = call.message.chat.id
                send_result()
        else:
            get_level(call)

@bot.callback_query_handler(func=lambda m: True)
def ask_question_step(message):
    logging.info('ask_question_step(message)')
    question_number = user_dict['question_number']
    test = user_dict["test"]
    question = f"Question # {question_number+1} out of {len(user_dict['test'])}\n\
Level {user_dict['level']}\n\
\n\
QUESTION:\n\
{user_dict['test'][question_number]['question']}\n\
ANSWERS:\n\
{test[question_number]['answers']}"
    

    markup_inline = types.InlineKeyboardMarkup()
    item_a = types.InlineKeyboardButton(text = 'A', callback_data = 'a')
    item_b = types.InlineKeyboardButton(text = 'B', callback_data = 'b')
    markup_inline.row(item_a, item_b)

    item_c = types.InlineKeyboardButton(text = 'C', callback_data = 'c')
    item_d = types.InlineKeyboardButton(text = 'D', callback_data = 'd')
    markup_inline.row(item_c, item_d)
    
   
    
    bot.send_message(message.chat.id, text = question, reply_markup = markup_inline)
 
@bot.callback_query_handler(func=lambda call: True)
def ask_level(message):
    logging.info('def ask_level')
    markup = telebot.types.InlineKeyboardMarkup()
    item_1 = types.InlineKeyboardButton(text='Level 1', callback_data = '1')
    item_2 = types.InlineKeyboardButton(text='Level 2', callback_data = '2')
    item_3 =types.InlineKeyboardButton(text='Level 3', callback_data = '3')
    markup.row(item_1, item_2, item_3)
    
    bot.send_message(message.from_user.id, text="Choose the level, please", reply_markup=markup)

def send_result():
    logging.info('def send_result')
    if user_dict["test_started"] == True and user_dict["test_finished"] == True:
        result = user_dict['right_results']
        level = user_dict['level']
        message_chat_id = user_dict["message_chat_id"]
        bot.send_message(message_chat_id,
f"You've passed the test level {user_dict['level']}\n\
Your result is {result} scores")
        if level == 1 and result == 40:
            bot.send_message(message_chat_id, "Your result indicates that you should take New English File Pre-intermediate level.")
        if level == 1 and result < 40:
            bot.send_message(message_chat_id, "Your result indicates that you should take New English File Elementary level.")
        if level == 2 and result == 40:
            bot.send_message(message_chat_id, "Your result indicates that you should take English File Intermediate level.")
        if level == 2 and result < 40:
            bot.send_message(message_chat_id, "Your result indicates that you should take New English File Pre-intermediate level.")
        if level == 3 and result == 40:
            bot.send_message(message_chat_id, "Your result indicates that you should take English File Intermediate level.")
        if level == 3 and result < 40:
            bot.send_message(message_chat_id, "Your result indicates that you should take New English File Pre-intermediate level.")
        
bot.polling()

#в конце дописать do you want to analyse your result or see recommendations
#и вывести неправильные ответы юзера и правильный ответ на этот вопрос. дать ссылку на правило.
