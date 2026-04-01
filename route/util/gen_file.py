import uuid
import os
from flask import current_app, request
from werkzeug.utils import secure_filename

def unique_filename(filename):
    """
    生成唯一的文件名，防止文件名冲突。
    """
    name, ext = os.path.splitext(filename)
    unique_str = str(uuid.uuid4())
    unique_name = name + "_" + unique_str + ext
    return unique_name


def process_image_uploads(new_data, image_fields):
    """
    处理图片上传并更新模型实例的相应字段。

    :param new_data: 数据库模型实例
    :param image_fields: 包含图片字段名称的列表
    """
    upload_folder = 'static/images'

    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    for image_field in image_fields:
        image_file = request.files.get(image_field)
        if image_file and image_file.filename:
            filename = unique_filename(secure_filename(image_file.filename))
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            print(image_path)
            setattr(new_data, image_field, '/static/images/' + filename)