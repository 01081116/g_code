from route import db

class Admin(db.Model):
    __tablename__ = 'admin'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci',
        'mysql_row_format': 'Dynamic',
        'mysql_auto_increment': '1',
        'comment': '管理员表'
    }

    id = db.Column(db.Integer, primary_key=True,  comment='编号')
    name = db.Column(db.String(100), unique=True,  comment='管理员账号')
    pwd = db.Column(db.String(100),  comment='管理员密码')


    def __repr__(self):
        return '<Admin %r>' % self.username

    def check_pwd(self, pwd):
        return self.pwd == pwd