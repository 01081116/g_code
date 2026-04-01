from sqlalchemy import DateTime, func, ForeignKey, text, Text,Float,Double,TIMESTAMP,DECIMAL,DATE,CHAR,BIGINT,SMALLINT
from sqlalchemy.orm import relationship

from route import db



class Music_comment(db.Model):
    __tablename__ = 'music_comment'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '音乐评论',
    }
    id = db.Column(db.Integer, primary_key=True, nullable=False, comment='编号')
    user_id = db.Column(db.String(55), nullable=True, comment='用户id')
    music_id = db.Column(db.String(55), nullable=True, comment='音乐id')
    content = db.Column(Text, nullable=True, comment='评论内容')
    create_time = db.Column(TIMESTAMP, nullable=True, comment='创建时间')

