from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from config import Config
# 初始化 SQLAlchemy 扩展
db = SQLAlchemy()
# 初始化 Flask-Migrate 扩展
migrate = Migrate()


def create_app():
    app = Flask(__name__, template_folder=Config.TEMPLATES_FOLDER,
                static_folder=Config.STATIC_FOLDER)
    # 从 config.py 文件加载配置
    app.config.from_object('config.Config')

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝图
    from route.ecarts_views.views import admin_login
    app.register_blueprint(admin_login, url_prefix="/admin")

    from route.ecarts_views.front import front
    app.register_blueprint(front, url_prefix="/")
    from route.new_playlists_views import new_playlists
    app.register_blueprint(new_playlists)
    from route.songs_views import songs
    app.register_blueprint(songs)
    from route.user_views import user
    app.register_blueprint(user)
    from route.music_comment_views import music_comment
    app.register_blueprint(music_comment)
    from route.dict_table_views import dict_table
    app.register_blueprint(dict_table)
    from route.category_muisc_views import category_muisc
    app.register_blueprint(category_muisc)
    from route.music_category_views import music_category
    app.register_blueprint(music_category)


    return app
