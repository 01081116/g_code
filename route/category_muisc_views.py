from flask import Blueprint, render_template, request, jsonify
from route import db
from models.music_category import Category_muisc, Music_category
from sqlalchemy import and_
from route.util.conver_bool import convert_to_bool
from route.util.gen_file import process_image_uploads
from sqlalchemy.exc import OperationalError, IntegrityError, DataError, SQLAlchemyError

# 创建蓝图
category_muisc = Blueprint('category_muisc', __name__)


# 列表
@category_muisc.route('/category_muisc/list', endpoint='category_muisc_list', methods=['GET'])
def category_muisc_list():
    album_name = request.args.get('album_name', '')
    singer_name = request.args.get('singer_name', '')
    song_name = request.args.get('song_name', '')
    per_page = int(request.args.get('per_page', 10))
    page = int(request.args.get('page', 1))
    sort_by = request.args.get('sort_by', 'id')
    music_categories = Music_category.query.all()  # 获取所有音乐类别
    query = Category_muisc.query
    if album_name:
        query = query.filter(Category_muisc.album_name.contains(album_name))
    if singer_name:
        query = query.filter(Category_muisc.singer_name.contains(singer_name))
    if song_name:
        query = query.filter(Category_muisc.song_name.contains(song_name))

    offset = (page - 1) * per_page
    results = query.offset(offset).limit(per_page).all()

    total = query.count()
    total_pages = (total + per_page - 1) // per_page

    return render_template('category_muisc/category_muisc_list.html', **locals())


# 添加
@category_muisc.route('/category_muisc/add', endpoint='category_muisc_add', methods=['POST'])
def category_muisc_add():
    try:
        data = request.form.to_dict()
        print(data)

        # 直接获取用户选择的 category_id
        category_id = data.get('category')  # 获取用户选择的类别ID

        # 将 category_id 添加到数据中
        data['category_id'] = int(category_id)  # 这里直接使用 category_id

        # 只保留需要的字段，确保没有额外的字段
        required_fields = ['album_name', 'cover_url', 'playlist_id', 'popularity', 'singer_name', 'song_id',
                           'song_name', 'category_id']
        filtered_data = {field: data[field] for field in required_fields if field in data}

        # 创建新记录
        new_data = Category_muisc(**filtered_data)

        # 处理图片上传（保留原有逻辑）
        image_fields = getattr(Category_muisc, '__image_fields__', [])
        process_image_uploads(new_data, image_fields)

        # 添加并提交到数据库
        db.session.add(new_data)
        db.session.commit()

        return jsonify({'status': 200, 'message': '添加成功'})
    except Exception as e:
        print(e)
        error_response = handle_exception(e)

        return jsonify(error_response)


# 编辑
@category_muisc.route('/category_muisc/edit', endpoint='category_muisc_edit', methods=['GET', 'POST'])
def category_muisc_edit():
    if request.method == 'POST':
        try:
            # 获取表单数据并转换类型
            data = request.form.to_dict()
            print(data)

            def convert(value, target_type):
                return target_type(value) if value else None

            # 定义字段转换
            field_conversions = {
                'category_id': (int, data.get('category')),
                'popularity': (float, data.get('popularity')),
                'song_id': (int, data.get('song_id')),
                'playlist_id': (int, data.get('playlist_id')),
                'id': (int, data.get('id')),
            }

            # 执行转换
            for field, (type_func, value) in field_conversions.items():
                data[field] = convert(value, type_func)

            # 查询要更新的记录
            result = Category_muisc.query.filter_by(id=data['id']).first()
            if not result:
                return jsonify({'status': 500, 'message': '未找到相关数据'})

            # 更新记录
            for key in ['album_name', 'playlist_id', 'popularity', 'singer_name', 'song_id', 'song_name', 'category_id']:
                setattr(result, key, data[key])

            # 处理封面图片上传
            image_fields = getattr(Category_muisc, '__image_fields__', [])
            if 'cover_url' in request.files and request.files['cover_url']:
                process_image_uploads(result, image_fields)

            db.session.commit()
            return jsonify({'status': 200, 'message': '修改成功'})
        except Exception as e:
            print(e)
            error_response = handle_exception(e)
            return jsonify(error_response)
    else:
        id = request.args.get('id')
        results = Category_muisc.query.filter_by(id=id).first()  # 查询单个记录
        music_categories = Music_category.query.all()  # 获取所有音乐类别
        return render_template('category_muisc/category_muisc_edit.html', results=results, music_categories=music_categories)

# 单个删除
@category_muisc.route('/category_muisc/del', endpoint='category_muisc_del', methods=['POST'])
def category_muisc_del():
    data = request.get_json()
    id = data.get('ID')
    results = Category_muisc.query.filter_by(id=int(id)).first()
    if results:
        db.session.delete(results)
        db.session.commit()
        return jsonify({'status': 200, 'message': '删除成功'})
    else:
        return jsonify({'status': 500, 'message': '未找到相关数据'})


# 批量删除
@category_muisc.route('/category_muisc/batch_delete', methods=['POST'])
def category_muisc_batch_delete():
    data = request.get_json()
    id_list = data.get('ids', [])
    try:
        # 删除 id_list 中包含的用户记录
        Category_muisc.query.filter(Category_muisc.id.in_(id_list)).delete(synchronize_session=False)
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
