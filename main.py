'''
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy as sa
import os

from blueprints.auth import auth_bp

basedir = os.path.abspath(os.path.dirname(__file__))

main = Flask(__name__)

#main.config["SECRET_KEY"]="topsecret"

import pandas as pd
data = pd.read_csv("C:/Users/МойПк/Project/sait/short.csv", index_col=0)
#data = pd.read_csv("D:\\JS\\site\\short.csv", index_col=0)

#Пути вставкаd
#"C:/Users/МойПк/Project/sait/short.csv"
#"D:\\JS\\site\\short.csv"

#Модуль регистрации пользователей
main.register_blueprint(auth_bp)
#>>>>>>> 892de0f6f80d11d3c20a135401c48ac11814e44c

# comments
A = data[['author', 'content']]

# search
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

name = []
stem = []
for i in range (36591):
    if data.iat[i,0] == "top250":
        name.append(data.iat[i,1])
        stem.append(data.iat[i,9])
df = pd.DataFrame({'name': name,'stem': stem})
df = df.groupby('name')['stem'].agg(' '.join).reset_index()

stem = []
for i in range (250):
    stem.append(df.iat[i,1])

tfidf = TfidfVectorizer()
mx_tf = tfidf.fit_transform(stem)

#movies


@main.route('/', methods=['POST', 'GET'])
def title(df = df, mx_tf = mx_tf):
    if request.method == "POST":
        return search(df, mx_tf)
    else:
        return render_template("title.html")

@main.route('/search/', methods=['POST', 'GET'])
def search(df = df, mx_tf = mx_tf):
    if request.method == "POST":
        name = request.form['movname']
        i = df.index [df['name']== name ]. tolist ()
        print(type(i[0]))
        find_nearest_to = df.iat[i[0], 1]

        new_entry = tfidf.transform([find_nearest_to])

        # расчет косинусного расстояния
        cosine_similarities = linear_kernel(new_entry, mx_tf).flatten()

        #запишем все попарные результаты сравнений
        df['cos_similarities'] = cosine_similarities

        # и отсортируем по убыванию (т.к. cos(0) = 1)
        df = df.sort_values(by=['cos_similarities'], ascending=[0])

        mov = []
        for i in range(5):
            mov.append(df.iat[i,0])
        print(mov)
        return render_template("search.html", movie=mov)
    else:
        mov = []
        return render_template("search.html", movie = mov)


@main.route('/movies/')
def movies():
    return render_template("movies.html", movie = df)

@main.route('/movies/<string:movname>')
def audience_detail(movname, data = data):
    name = movname
    g = data.index [data['movie_name'] == name ].tolist ()
    return render_template("movie_detail.html", movie=data, mas = g)

@main.route('/podborki/')
def podborki():
    return render_template("podborki.html")

@main.route('/podborka/')
def podborka():
    return render_template("podborka.html")

@main.route('/pod/')
def pod():
    return render_template("pod.html")

# Новая часть

@main.route('/favorites/')
def favorites():
    return render_template("favorites.html")

@main.route('/podborki/editor/')
def editor():
    return render_template("editor.html")


if __name__ == "__main__":
    main.run(debug=True)
'''
'''
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt_identity,
    create_access_token
)
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация приложения
app = Flask(__name__)

# Конфигурация
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "default-secret-key")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", 
    "postgresql://username:password@localhost:5432/sait_auth"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Инициализация расширений
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Модель пользователя
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')

# Загрузка данных CSV
try:
    data = pd.read_csv("C:\РекЛаб\sait\short.csv", index_col=0)
    name = []
    stem = []
    for i in range(36591):
        if data.iat[i, 0] == "top250":
            name.append(data.iat[i, 1])
            stem.append(data.iat[i, 9])
    df = pd.DataFrame({'name': name, 'stem': stem})
    df = df.groupby('name')['stem'].agg(' '.join).reset_index()
    stem = [df.iat[i, 1] for i in range(250)]
    tfidf = TfidfVectorizer()
    mx_tf = tfidf.fit_transform(stem)
except Exception as e:
    print(f"Ошибка загрузки данных: {e}")
    data = pd.DataFrame()
    df = pd.DataFrame()
    mx_tf = None

# Регистрация Blueprints
from blueprints.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Роуты приложения
@app.route('/', methods=['POST', 'GET'])
def title():
    if request.method == "POST":
        return search()
    return render_template("title.html")

@app.route('/search/', methods=['POST', 'GET'])
def search():
    if request.method == "POST" and mx_tf is not None:
        name = request.form['movname']
        try:
            i = df.index[df['name'] == name].tolist()[0]
            find_nearest_to = df.iat[i, 1]
            new_entry = tfidf.transform([find_nearest_to])
            cosine_similarities = linear_kernel(new_entry, mx_tf).flatten()
            df['cos_similarities'] = cosine_similarities
            df_sorted = df.sort_values(by=['cos_similarities'], ascending=[0])
            mov = [df_sorted.iat[i, 0] for i in range(5)]
            return render_template("search.html", movie=mov)
        except:
            pass
    return render_template("search.html", movie=[])

@app.route('/movies/')
def movies():
    return render_template("movies.html", movie=df)

@app.route('/movies/<string:movname>')
def audience_detail(movname):
    name = movname
    g = data.index[data['movie_name'] == name].tolist()
    return render_template("movie_detail.html", movie=data, mas=g)

# Защищенные роуты
@app.route('/favorites/')
@jwt_required()
def favorites():
    current_user = get_jwt_identity()
    return render_template("favorites.html", user=current_user)

@app.route('/podborki/editor/')
@jwt_required()
def editor():
    current_user = get_jwt_identity()
    if current_user.get("role") != "admin":
        return jsonify({"error": "Доступ запрещен"}), 403
    return render_template("editor.html")

# Остальные роуты
@app.route('/podborki/')
def podborki():
    return render_template("podborki.html")

@app.route('/podborka/')
def podborka():
    return render_template("podborka.html")

@app.route('/pod/')
def pod():
    return render_template("pod.html")

# Инициализация БД
def create_tables():
    with app.app_context():
        db.create_all()
        # Создаем тестового администратора, если его нет
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
'''
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt_identity,
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies
)
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация приложения
app = Flask(__name__)

# Конфигурация безопасности
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY", os.urandom(32)),
    JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", os.urandom(32)),
    JWT_ACCESS_TOKEN_EXPIRES=datetime.timedelta(hours=1),
    JWT_TOKEN_LOCATION=['cookies'],
    JWT_COOKIE_SECURE=False,  # True в production с HTTPS
    JWT_COOKIE_HTTPONLY=True,
    JWT_COOKIE_SAMESITE='Lax',
    SQLALCHEMY_DATABASE_URI=os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:daeee@localhost:5432/reclab"
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True}
)

# Инициализация расширений
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Модель пользователя
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')

# Загрузка данных CSV с обработкой ошибок
def load_movie_data():
    try:
        csv_path = os.path.join("C:/", "РекЛаб", "sait", "short.csv")
        data = pd.read_csv(csv_path, index_col=0)
        
        # Фильтрация и обработка данных
        top250 = data[data.iloc[:, 0] == "top250"]
        df = top250.iloc[:, [1, 9]].groupby('movie_name')['stem'].agg(' '.join).reset_index()
        
        tfidf = TfidfVectorizer()
        mx_tf = tfidf.fit_transform(df['stem'].values[:250])
        
        return data, df, mx_tf, tfidf
    except Exception as e:
        app.logger.error(f"Ошибка загрузки данных: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), None, None

data, df, mx_tf, tfidf = load_movie_data()

# Регистрация Blueprints
from blueprints.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Основные роуты с улучшенной обработкой
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        password = request.form.get('password', '').strip()
        
        if not nickname or not password:
            return render_template("title.html", 
                                error="Все поля обязательны",
                                nickname=nickname), 400
        
        try:
            user = User.query.filter_by(username=nickname).first()
            if not user or not check_password_hash(user.password_hash, password):
                return render_template("title.html",
                                    error="Неверный логин или пароль",
                                    nickname=nickname), 401
            
            access_token = create_access_token(identity={
                'username': user.username,
                'role': user.role
            })
            
            response = make_response(redirect(url_for('movies')))
            set_access_cookies(response, access_token)
            return response
            
        except Exception as e:
            app.logger.error(f"Auth error: {str(e)}")
            return render_template("title.html",
                                error="Ошибка сервера",
                                nickname=nickname), 500
    
    return render_template("title.html")

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    unset_jwt_cookies(response)
    return response

# Поиск фильмов с улучшенной обработкой
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        if mx_tf is None:
            return render_template("search.html", error="Данные не загружены"), 503
        
        movname = request.form.get('movname', '').strip()
        if not movname:
            return render_template("search.html", error="Введите название фильма"), 400
        
        try:
            matches = df[df['name'].str.contains(movname, case=False, regex=False)]
            if matches.empty:
                return render_template("search.html", error="Фильм не найден"), 404
            
            first_match = matches.iloc[0]
            new_entry = tfidf.transform([first_match['stem']])
            cosine_sim = linear_kernel(new_entry, mx_tf).flatten()
            
            top_movies = (
                df.assign(similarity=cosine_sim)
                .nlargest(5, 'similarity')['name']
                .tolist()
            )
            
            return render_template("search.html", movie=top_movies)
        except Exception as e:
            app.logger.error(f"Search error: {str(e)}")
            return render_template("search.html", error="Ошибка при поиске"), 500
    
    return render_template("search.html")

# Остальные роуты с улучшенной безопасностью
@app.route('/movies')
def movies():
    return render_template("movies.html", movie=df)

@app.route('/movies/<string:movname>')
@jwt_required(optional=True)
def movie_detail(movname):
    try:
        indices = data.index[data['movie_name'] == movname].tolist()
        if not indices:
            return render_template("error.html", message="Фильм не найден"), 404
        return render_template("movie_detail.html", movie=data, mas=indices)
    except Exception as e:
        app.logger.error(f"Movie detail error: {str(e)}")
        return render_template("error.html", message="Ошибка сервера"), 500

# Защищенные роуты
@app.route('/favorites')
@jwt_required()
def favorites():
    current_user = get_jwt_identity()
    return render_template("favorites.html", user=current_user)

@app.route('/editor')
@jwt_required()
def editor():
    current_user = get_jwt_identity()
    if current_user.get("role") != "admin":
        return render_template("error.html", message="Доступ запрещен"), 403
    return render_template("editor.html")

# Кэширование статики
@app.after_request
def add_cache_headers(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=86400'
        response.headers['Vary'] = 'Accept-Encoding'
    return response

# Обработка ошибок
@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', message="Некорректный запрос"), 400

@app.errorhandler(401)
def unauthorized(e):
    return render_template('error.html', message="Требуется авторизация"), 401

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', message="Доступ запрещен"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message="Страница не найдена"), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('error.html', message="Метод не разрешен"), 405

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message="Внутренняя ошибка сервера"), 500

# Инициализация БД
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)