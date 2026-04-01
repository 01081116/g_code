from flask import Blueprint, render_template, request, jsonify, url_for, session, redirect
from models.admin_model import *

admin_login = Blueprint('admin_login', __name__)

@admin_login.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'})

        # 从数据库中查询用户
        admin = Admin.query.filter_by(name=username).first()

        if admin and admin.check_pwd(password):  # 使用模型中的check_pwd方法
            # 用户认证通过，创建会话
            session['admin_id'] = admin.id
            # return jsonify({'success': True, 'redirect_url': url_for('admin.codetemplate_list')})
            return jsonify({'success': True, 'redirect_url': url_for('admin_login.pwd')})
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'})

    return render_template('admin_login/login.html')

@admin_login.route('/logout', methods=['GET'])
def logout():
    session.pop('admin_id', None)  # 清除会话中的用户信息
    return redirect(url_for('admin_login.login'))

@admin_login.route('/pwd/', methods=["GET", "POST"])
def pwd():
    """
    后台密码修改
    """
    if request.method == "POST":
        old_pwd = request.json.get("old_pwd")
        new_pwd = request.json.get("new_pwd")

        admin = Admin.query.filter_by(id=session["admin_id"]).first()
        if not admin or admin.pwd != old_pwd:
            return jsonify({"status": "err", "msg": "旧密码错误！"})

        # 更新密码
        admin.pwd = new_pwd
        db.session.add(admin)
        db.session.commit()
        return jsonify({"status": "ok", "msg": "修改密码成功！"})

    return render_template("admin_login/pwd.html")