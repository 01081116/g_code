from flask import Blueprint, render_template, request, jsonify
from route import db
from models.user import User
from sqlalchemy import and_
from route.util.conver_bool import convert_to_bool
from route.util.gen_file import process_image_uploads
from sqlalchemy.exc import OperationalError, IntegrityError, DataError,SQLAlchemyError
# 创建蓝图
user = Blueprint('user', __name__)

#列表
@user.route('/user/list', endpoint='user_list', methods=['GET'])
def user_list():
    username = request.args.get('username', '')
    per_page = int(request.args.get('per_page', 10))
    page = int(request.args.get('page', 1))
    sort_by = request.args.get('sort_by', 'id')
    query = User.query
    if username:
        query = query.filter(User.username.contains(username))

    offset = (page - 1) * per_page
    results = query.offset(offset).limit(per_page).all()

    total = query.count()
    total_pages = (total + per_page - 1) // per_page

    return render_template('user/user_list.html', **locals())

#添加
@user.route('/user/add', endpoint='user_add', methods=['POST'])
def user_add():
    try:
        image_fields = getattr(User, '__image_fields__', [])
        # 获取 JSON 数据并创建 Data 实例
        data = request.form.to_dict()
        for key, value in data.items():
            data[key] = convert_to_bool(value)
        new_data = User(**data)
        process_image_uploads(new_data, image_fields)
        # 添加并提交到数据库
        db.session.add(new_data)
        db.session.commit()

        return jsonify({'status': 200, 'message': '添加成功'})
    except Exception as e:
        # 回滚事务并返回错误消息
        error_response = handle_exception(e)
        return jsonify(error_response)

# 编辑
@user.route('/user/edit', endpoint='user_edit', methods=['GET', 'POST'])
def user_edit():
    if request.method == 'POST':
        try:
            # 获取表单数据
            data = request.form.to_dict()
            for key, value in data.items():
                data[key] = convert_to_bool(value)
            id = data.get('id', int)
            # 查询要更新的记录
            result = User.query.filter_by(id=id).first()
            if not result:
                return jsonify({'status': 500, 'message': '未找到相关数据'})
            # 更新数据
            for key, value in data.items():
                setattr(result, key, value)
            image_fields = getattr(User, '__image_fields__', [])
            process_image_uploads(result, image_fields)
            db.session.commit()
            return jsonify({'status': 200, 'message': '修改成功'})
        except Exception as e:
            error_response = handle_exception(e)
            return jsonify(error_response)
    else:
        id = request.args.get('id')
        print(id)
        results = User.query.filter_by(id=id).first()  # 查询单个记录
        return render_template('user/user_edit.html', **locals())

#单个删除
@user.route('/user/del',endpoint='user_del',methods=['POST'])
def user_del():
    data = request.get_json()
    id = data.get('ID')
    results = User.query.filter_by(id=int(id)).first()
    if results:
        db.session.delete(results)
        db.session.commit()
        return jsonify({'status': 200, 'message': '删除成功'})
    else:
        return jsonify({'status': 500, 'message': '未找到相关数据'})

#批量删除
@user.route('/user/batch_delete', methods=['POST'])
def user_batch_delete():
    data = request.get_json()
    id_list = data.get('ids', [])
    try:
        # 删除 id_list 中包含的用户记录
        User.query.filter(User.id.in_(id_list)).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'status': 200, 'message': '删除成功'})
    except Exception as e:
        error_response = handle_exception(e)
        return jsonify(error_response)


def handle_exception(e):
    if isinstance(e, OperationalError):
        error_message = str(e)
        if 'Incorrect date value' in error_message:
            return {'status': 500, 'message': '数据格式错误'}
        return {'status': 500, 'message': '操作错误，请检查您的数据。'}

    elif isinstance(e, IntegrityError):
        return {'status': 500, 'message': '数据完整性错误，例如重复的唯一值。'}

    elif isinstance(e, DataError):
        return {'status': 500, 'message': '数据格式错误，例如字段长度超出限制。'}

    # 其他 SQLAlchemy 异常
    elif isinstance(e, Exception):
        return {'status': 500, 'message': '内部服务器错误，请稍后再试。'}

    return {'status': 500, 'message': '未知错误发生。'}