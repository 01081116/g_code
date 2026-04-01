from sqlalchemy import DateTime, func, ForeignKey, text, Text,Float,Double,TIMESTAMP,DECIMAL,DATE,CHAR,BIGINT,SMALLINT
from sqlalchemy.orm import relationship
from route import db
class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '用户',
    }
    id = db.Column(db.Integer, primary_key=True, nullable=False, comment='ID')
    password = db.Column(db.String(32), nullable=True, comment='密码')
    username = db.Column(db.String(32), nullable=True, comment='用户名')