from route import create_app, db
from flask_migrate import Migrate

# 创建 Flask 应用实例
app = create_app()
app.secret_key = "hjjy"
# 初始化 Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(debug=True)