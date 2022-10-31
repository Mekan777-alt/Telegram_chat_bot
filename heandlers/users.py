import datetime
from config import dp
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from context import UserState
from keyboards.buttons import back_markup, back_message
import smtplib
from app import cmd_start
import psycopg2 as ps
all_info = ''


async def send_mail(mail, text):
    sender = 'iMediatorChatBot@yandex.ru'
    password = '!QZ2wxas'
    mail_lib = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    mail_lib.login(sender, password)
    msg = 'From: %s\r\nTo: %s\r\nContent-Type: text/plain; charset="utf-8"\r\nSubject: %s\r\n\r\n' % (
        sender, mail, 'Заявка')
    msg += text
    mail_lib.sendmail(sender, mail, msg.encode('utf8'))
    mail_lib.quit()


@dp.message_handler(text=['Описать проблему и оставить данные', 'Все понятно, готов оставить заявку'], state=None)
async def cmd_two(message: types.Message):
    markup = ReplyKeyboardRemove()
    await message.answer('Я вас понял. Оставьте свои контактные данные и мы с вами свяжемся в ближайшее время')
    await UserState.name.set()
    await message.answer('Введите пожалуйста ФИО:', reply_markup=markup)


@dp.message_handler(state=UserState.name)
async def cmd_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        await UserState.next()
        await message.answer('Город:', reply_markup=back_markup())


@dp.message_handler(text=back_message, state=UserState.city)
async def process_name_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer('Изменить имя с <b>' + data['name'] + '</b>?')
    await UserState.name.set()


@dp.message_handler(state=UserState.city)
async def cmd_city(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    send_phone = KeyboardButton("📞 Отправить свой номер", request_contact=True)
    markup.add(send_phone)
    markup.add(back_message)
    async with state.proxy() as data:
        data['city'] = message.text
        await UserState.next()
        await message.answer('Номер телефона:', reply_markup=markup)


@dp.message_handler(text=back_message, state=UserState.phone_number)
async def process_city_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer('Изменить город с <b>' + data['city'] + '</b>?',
                             reply_markup=back_markup())
    await UserState.city.set()


@dp.message_handler(content_types=ContentType.CONTACT, state=UserState.phone_number)
async def cmd_phone_number_markup(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardRemove()
    async with state.proxy() as data:
        if message.contact is not None:
            data['phone_number'] = message.contact['phone_number']
            await UserState.next()
            await message.answer('Почту:', reply_markup=markup)


@dp.message_handler(state=UserState.phone_number)
async def cmd_phone_number_message(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardRemove()
    async with state.proxy() as data:
        data['phone_number'] = message.text
        await UserState.next()
        await message.answer('Почту:', reply_markup=markup)


@dp.message_handler(text=back_message, state=UserState.email)
async def process_number_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer('Изменить телефон с <b>' + data['phone_number'] + '</b>?',
                             reply_markup=back_markup())
    await UserState.phone_number.set()


@dp.message_handler(state=UserState.email)
async def cmd_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
        await UserState.next()
        await message.answer('Комментарии по желанию')


@dp.message_handler(text=back_message, state=UserState.comment)
async def process_email_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer('Изменить почту с <b>' + data['email'] + '</b>?',
                             reply_markup=back_markup())
    await UserState.email.set()


@dp.message_handler(text=back_message, state=UserState.comment)
async def process_name_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer('Изменить комментарий с <b>' + data['name'] + '</b>?',
                             reply_markup=back_markup())
    await UserState.comment.set()


@dp.message_handler(state=UserState.comment)
async def cmd_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        global all_info
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Да.', 'Нет')
        data['comment'] = message.text
        time = datetime.datetime.now()
        list_name = data['name'].split()
        all_info = f"ФИО: {data['name']}\n" \
                   f"Город: {data['city']}\n" \
                   f"Телефон номер: {data['phone_number']}\n" \
                   f"Почта:  {data['email']}\n" \
                   f"Комментарии: {data['comment']}\n" \
                   f"Время и дата заявки: {time}"
        try:
            connect = ps.connect(host='92.255.76.86',
                                 port=5432,
                                 database='imediators',
                                 user='mekan99',
                                 password='Mm6347455627.')
            if len(list_name) == 2:
                with connect.cursor() as cursor:
                    cursor.execute("""INSERT INTO users (firstname, lastname, patronymic, city, phone_number, email, 
                    comment_users, where_user, date_request, user_request, search_mediators, work_mediators, payments, 
                    refusal, expectation, comment_admin) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                   (list_name[0], list_name[1], None, data['city'], data['phone_number'],
                                    data['email'],
                                    data['comment'], 'telegram', time, None, None, None, None, None, None, None))
                    connect.commit()
            else:
                with connect.cursor() as cursor:
                    cursor.execute("""INSERT INTO users (firstname, lastname, patronymic, city, phone_number, email, 
                    comment_users, where_user, date_request, user_request, search_mediators, work_mediators, payments, 
                    refusal, expectation, comment_admin) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                   (list_name[0], list_name[1], list_name[2], data['city'], data['phone_number'],
                                    data['email'],
                                    data['comment'], 'telegram', time, None, None, None, None, None, None, None))
                    connect.commit()

        except Exception as ex:
            print(f"[Error] {ex}")
        finally:
            if connect:
                connect.close()
        await send_mail('info.i.mediator@yandex.ru', all_info)
        await message.answer("Спасибо!"
                             "Мы свяжемся с вами в ближайшее время.", reply_markup=markup)

    await state.finish()


@dp.message_handler(text='Кто вы?')
async def cmd_one(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Кто такой медиатор?")
    await message.answer('Мы — сообщество профессиональных медиаторов.\n'
                         'Помогаем решать юридические, семейные и административные споры во внесудебном порядке.')
    await message.answer("К нам обращаются, если:\n"
                         "-необходимо решить спор в кратчайшие сроки\n"
                         "-при этом сохранить полную конфиденциальность\n"
                         "-а также отношения с участником спора в будущем", reply_markup=markup)


@dp.message_handler(text='Зачем мне это?')
async def cmd_two(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Кто такой медиатор?")
    await message.answer("К нам обращаются, если:\n"
                         "-необходимо решить спор в кратчайшие сроки\n"
                         "-при этом сохранить полную конфиденциальность\n"
                         "-а также отношения с участником спора в будущем", reply_markup=markup)


@dp.message_handler(text="Кто такой медиатор?")
async def who_it_mediators(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Сколько стоят услуги?", "Как долго длится медиация?")
    markup.add("Описать проблему и оставить данные")
    await message.answer('Медиатор — это нейтральное лицо, которое помогает достичь соглашения в споре.\n'
                         'Его главные задачи:\n'
                         '- перевести переговоры из эмоционального русла в конструктивное.\n'
                         '- помочь сторонам понять свои интересы и договориться о взаимовыгодном решении конфликта.\n'
                         '95% соглашений, достигнутых на процедуре медиации, исполняется сторонами добровольно!',
                         reply_markup=markup)


@dp.message_handler(text="Сколько стоят услуги?")
async def price_mediators(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Как долго длится медиация?")
    markup.add("Описать проблему и оставить данные")
    await message.answer("Это зависит от сложности и вида проблемы."
                         "Но зачастую услуги медиатора обходятся значительно дешевле услуг адвоката,"
                         "a оплата взимается с обеих сторон в равных частях и только в случае положительного "
                         "завершения спора", reply_markup=markup)


@dp.message_handler(text='Как долго длится медиация?')
async def time_mediaciya(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Интересно, но у меня остались вопросы")
    markup.add("Описать проблему и оставить данные")
    await message.answer("В среднем, требуется 2-4 медиации для достижения соглашения. Как правило, это занимает 2-3 "
                         "недели.\n "
                         "Но все случаи индивидуальны, поэтому для уточнения сроков вы можете оставить контакты. "
                         "Мы свяжемся с вами для уточнения деталей и сможем сказать более точные сроки.",
                         reply_markup=markup)


@dp.message_handler(text='Интересно, но у меня остались вопросы')
async def questions(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Все понятно, готов оставить заявку')
    markup.add("Этапы работы")
    markup.add("Где проходят переговоры?")
    markup.add("Поможет ли медиатор в моем случае?")
    markup.add("А если мне не понравится мой медиатор?")
    markup.add("Преимущества работы с медиаторами")
    markup.add("Как быстро я получу результат?")
    markup.add("Стоимость услуги?")
    await message.answer("Я подобрал для вас ответы на часто задаваемые вопросы", reply_markup=markup)


"""Блок вопросов"""


@dp.message_handler(text="Этапы работы")
async def stages_works(message: types.Message):
    await message.answer("1. Проводим консультацию, где знакомим со сроками и стоимостью\n"
                         "2. Заключаем договор, согласуем план и количество встреч\n"
                         "3. Проводим медиации и подписываем соглашение\n"
                         "4. Принимаем оплату услуги с обеих сторон в соотношении 50/50")


@dp.message_handler(text='Где проходят переговоры?')
async def negotiation(message: types.Message):
    await message.answer("Процедура медиации предварительно согласуется с обеими сторонами. "
                         "Ведь для разрешения конфликта важно обсуждение в спокойной и комфортной обстановке.\n"
                         "Если по каким-то причинам очное проведение медиации невозможно,"
                         "обсудим возможность проведения процедуры онлайн.")


@dp.message_handler(text='Поможет ли медиатор в моем случае?')
async def help_mediators(message: types.Message):
    await message.answer("Медиаторы работают со всеми конфликтными ситуациями от бракоразводных процессов и "
                         "раздела имущества до бизнес-споров."
                         "Скорее всего, ваш случай подходит под кейс для медиации. Но все равно, "
                         "можете оставить контакты и мы с вами свяжемся и ответим на все вопросы.")


@dp.message_handler(text="А если мне не понравится мой медиатор?")
async def like_mediators(message: types.Message):
    await message.answer("Это не проблема!\n"
                         "I-mediator - это сообщество профессиональных медиаторов. "
                         "Если вам по каким-либо причинам не подойдет специалист, мы поможем подобрать другого.")


@dp.message_handler(text='Преимущества работы с медиаторами')
async def advantages_mediators(message: types.Message):
    await message.answer("Наши преимущества:\n"
                         "<b>- Экономим ваши деньги.</b>\n"
                         "Услуги медиатора стоят дешевле услуг адвоката и, оплата производится обеими сторонами спора "
                         "и только после его урегулирования.\n"
                         "- Предоставляем <b> бесплатные консультации. </b>\n"
                         "Мы ответим на вопросы о необходимости и процедуре медиации в вашем случае.\n"
                         "<b>- Экономим ваше время.</b>\n"
                         "Как известно, суды могут длиться годами. Медиации позволяют достичь соглашения всего за 2-4 "
                         "недели.\n"
                         "- Гарантируем <b> конфиденциальность.</b>\n"
                         "Плюс, Более 85% соглашений по результатам медиации исполняются сторонами добровольно и без "
                         "задержек.")


@dp.message_handler(text='Как быстро я получу результат?')
async def result_mediators(message: types.Message):
    await message.answer("В среднем, требуется 2-4 медиации для достижения соглашения. Как правило, это занимает 2-3 "
                         "недели.\n"
                         "Но все случаи индивидуальны, поэтому для уточнения сроков вы можете оставить контакты. "
                         "Мы свяжемся с вами для уточнения деталей и сможем сказать более точные сроки.")


@dp.message_handler(text="Стоимость услуги?")
async def mediators_price(message: types.Message):
    await message.answer("Это зависит от сложности и вида проблемы. "
                         "Но зачастую услуги медиатора обходятся значительно дешевле услуг адвоката, а "
                         "оплата взимается с обеих сторон в равных частях и только в случае положительного "
                         "завершения спора")


@dp.message_handler(text='В начало')
async def main_menu(message: types.Message, state: FSMContext):
    await cmd_start(message, state)
