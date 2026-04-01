from sqlalchemy import DateTime, func, ForeignKey, text, Text,Float,Double,TIMESTAMP,DECIMAL,DATE,CHAR,BIGINT,SMALLINT
from sqlalchemy.orm import relationship

from route import db



class Dict_table(db.Model):
    __tablename__ = 'dict_table'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '敏感词',
    }
    id = db.Column(db.Integer, primary_key=True, nullable=False, comment='编号')
    keyword = db.Column(db.String(55), nullable=True, comment='敏感词')
    is_show = db.Column(db.String(55), nullable=True, comment='是否启用')

