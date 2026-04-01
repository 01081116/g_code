def convert_to_bool(value):
    """
    将字符串形式的布尔值转换为实际的布尔值。
    """
    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
    return value  # 对于非字符串类型的值，直接返回原值