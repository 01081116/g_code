from sqlalchemy import DateTime, func, ForeignKey, text, Text,Float,Double,TIMESTAMP,DECIMAL,DATE,CHAR,BIGINT,SMALLINT
from sqlalchemy.orm import relationship
from route import db
class New_playlists(db.Model):
    __tablename__ = 'new_playlists'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '歌单数据',
    }
    author = db.Column(Text, nullable=True, comment='作者')
    gdid = db.Column(BIGINT, nullable=True, comment='歌单id')
    id = db.Column(db.Integer, primary_key=True, nullable=False, comment='ID')
    page = db.Column(BIGINT, nullable=True, comment='页面编号')
    play_count = db.Column(Double, nullable=True, comment='播放次数')
    playlist_cover = db.Column(Text, nullable=True, comment='歌单封面')
    playlist_link = db.Column(Text, nullable=True, comment='歌单链接')
    playlist_title = db.Column(Text, nullable=True, comment='歌单标题')
    type = db.Column(Text, nullable=True, comment='歌单类型')