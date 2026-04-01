from sqlalchemy import DateTime, func, ForeignKey, text, Text,Float,Double,TIMESTAMP,DECIMAL,DATE,CHAR,BIGINT,SMALLINT
from sqlalchemy.orm import relationship
from route import db
class Songs(db.Model):
    __tablename__ = 'songs'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '歌曲数据',
    }
    album_name = db.Column(db.String(255), nullable=True, comment='专辑')
    cover_url = db.Column(db.String(255), nullable=True, comment='封面')
    id = db.Column(db.Integer, primary_key=True, nullable=False, comment='ID')
    playlist_id = db.Column(BIGINT, nullable=True, comment='歌单ID')
    popularity = db.Column(Float, nullable=True, comment='欢迎度')
    singer_name = db.Column(db.String(255), nullable=False, comment='歌手')
    song_id = db.Column(BIGINT, nullable=True, comment='歌曲ID')
    song_name = db.Column(db.String(255), nullable=False, comment='歌曲名称')