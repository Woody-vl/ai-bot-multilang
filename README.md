# ai-bot-multilang

## Установка зависимостей
1. Установите Python 3.10+.
2. Склонируйте репозиторий и выполните:
   ```bash
   pip install aiogram openai
   ```

## Создание `.env`
1. В корне проекта создайте файл `.env` со следующим содержимым:
   ```bash
   ACTIVE_TOKEN=TOKEN_TURKEY
   OPENAI_API_KEY=ваш_ключ
   TOKEN_TURKEY=
   TOKEN_INDONESIA=
   TOKEN_ARABIC=
   TOKEN_VIETNAM=
   TOKEN_BRAZIL=
   BOT_USERNAME=your_bot
   FREE_MESSAGES=10
   ```

## Запуск локально
1. Убедитесь, что переменные из `.env` доступны в среде.
2. Запустите бота командой:
   ```bash
   python bot.py
   ```

## Деплой на Railway
1. Зарегистрируйтесь на [Railway](https://railway.app/) и создайте новый проект.
2. Подключите репозиторий и задайте переменные окружения из `.env`.
3. Railway автоматически запустит бота по команде из `Procfile`.
4. Нажмите **Deploy** для запуска приложения.

## Функционал бота
- 10 бесплатных сообщений для каждого пользователя.
- Ответы сгенерированы моделью OpenAI GPT‑3.5.
- Учёт сообщений ведётся в базе данных SQLite.
- После окончания бесплатного лимита появляется кнопка оплаты через Telegram Stars.

## 🚀 Railway Deploy Instructions

1. Перейдите в Railway и создайте новый проект, подключив этот репозиторий.
2. В разделе **Environment Variables** добавьте переменные из `.env.example`.
3. Railway автоматически установит зависимости из `requirements.txt`.
4. Благодаря `Procfile`, бот будет запущен с командой:

python bot.py

🔁 Для смены активного токена измените `ACTIVE_TOKEN`, например на `TOKEN_INDONESIA`.
