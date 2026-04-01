import os


class Config:
    HOST = 'localhost'
    USER = 'root'
    PASSWORD = '123456'
    DATABASE = 'lstm_music_rec'
    PORT = 3306
    CHARSET = 'utf8mb4'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hjjy')  # 应用的密钥
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset={CHARSET}')  # 数据库 URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用 SQLAlchemy 的事件系统
    SESSION_TYPE = 'filesystem'
     # 默认的 templates 文件夹路径（相对于基础路径）
    TEMPLATES_FOLDER = os.path.join(BASE_DIR, 'templates')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')