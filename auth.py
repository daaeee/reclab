

from flask import Flask, render_template, url_for, request, redirect, Blueprint, flash
from flask_bcrypt import Bcrypt
import pymysql

#функция проверки слова на допустимые символы
def word_agreed (word):
    word=str(word)
    for char in word:
        if char not in "ABCDEFGHIJKLMNOPQRSTUWVXYZabcdefghijklmnopqrstuvwxyz.,_!?%№@;-1234567890":
            return False
    return True


#СОздаем новый модуль
auth_bp=Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        # Получение данных из формы
        username = request.form.get('username')
        password = request.form.get('password')
        pw_confirm = request.form.get('pw_confirm')

        # Проверка ввода во все поля
        if not username or not password or not pw_confirm:
            flash('Заполните все поля', 'error')
            return redirect(url_for('auth.register'))

        # Проверка паролей
        if pw_confirm != password:
            flash('Пароли должны совпадать', 'error')
            return redirect(url_for('auth.register'))

        # Проверка на длину пароля
        if len(password) < 8:
            flash('Пароль должен быть не менее 8 символов', 'error')
            return redirect(url_for('auth.register'))

        # Проверка пароля на допустимые символы
        if not word_agreed(password):
            flash('Пароль должен содержать только латинские буквы, цифры и символы ".,_!?%№@;-"', 'error')
            return redirect(url_for('auth.register'))

        # Хеширование пароля
        bcrypt = Bcrypt()
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        # Работа с базой данных
        from db_connection import conn
        try:
            conn.ping(reconnect=True)
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE uname = %s", (username,))
                res = cursor.fetchone()
                if res['count'] > 0:
                    flash('Пользователь с таким именем уже существует', 'error')
                else:
                    sql_script = "INSERT INTO users (uname, password) VALUES (%s, %s);"
                    cursor.execute(sql_script, (username, hashed_pw))
                    conn.commit()
                    flash('Вы зарегистрированы! Войдите в личный кабинет', 'success')
        except Exception as e:
            flash(f'Произошла ошибка: {e}', 'error')
        finally:
            conn.close()

    return render_template("base.html")  # Добавьте вашу форму регистрации

