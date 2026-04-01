from sqlalchemy import DateTime, func, ForeignKey, text, Text, Float, Double, TIMESTAMP, DECIMAL, DATE, CHAR, BIGINT, \
    SMALLINT
from sqlalchemy.orm import relationship

from route import db


class Music_category(db.Model):
    __tablename__ = 'music_category'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '音乐类别',
    }
    id = db.Column(db.Integer, primary_key=True, nullable=False, comment='编号')
    category = db.Column(db.String(55), nullable=True, comment='类别')


class Category_muisc(db.Model):
    __image_fields__ = ['cover_url']
    __tablename__ = 'category_muisc'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '分类音乐',
    }

    album_name = db.Column(db.String(255), nullable=True, comment='专辑')
    cover_url = db.Column(db.String(255), nullable=True, comment='封面')
    id = db.Column(db.Integer, primary_key=True, nullable=False, comment='ID')
    playlist_id = db.Column(BIGINT, nullable=True, comment='歌单ID')
    popularity = db.Column(Float, nullable=True, comment='欢迎度')
    singer_name = db.Column(db.String(255), nullable=False, comment='歌手')
    song_id = db.Column(BIGINT, nullable=True, comment='歌曲ID')
    song_name = db.Column(db.String(255), nullable=False, comment='歌曲名称')

    # 新增 category_id 列，用于外键关联
    category_id = db.Column(db.Integer, db.ForeignKey('music_category.id'), nullable=True, comment='音乐类别ID')

    # 添加与 Music_category 的关系
    category = relationship('Music_category', backref='category_muiscs')


class Collect(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, comment='ID')
    music_id = db.Column(BIGINT, nullable=True, comment='歌曲ID')
    user_id = db.Column(db.Integer, nullable=False, comment='用户ID')
