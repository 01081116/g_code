import pickle
import numpy as np
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences


# 加载模型和字典（只加载一次）
MODEL_PATH = './build_model/lstm_model.h5'
WORD_DICT_PATH = './build_model/word_dict.pk'
LABEL_DICT_PATH = './build_model/label_dict.pk'
INPUT_SHAPE = 50

_model = None
_word_dict = None
_label_dict = None


def _load_resources():
    """懒加载模型和字典"""
    global _model, _word_dict, _label_dict
    
    if _model is None:
        _model = load_model(MODEL_PATH)
    
    if _word_dict is None:
        with open(WORD_DICT_PATH, 'rb') as f:
            _word_dict = pickle.load(f)
    
    if _label_dict is None:
        with open(LABEL_DICT_PATH, 'rb') as f:
            _label_dict = pickle.load(f)
    
    return _model, _word_dict, _label_dict


def predict(text, debug=False):
    """
    使用LSTM模型进行情感分类
    参数:
        text: 输入文本
        debug: 是否打印调试信息
    返回:
        sentiment: 情感倾向 (1=正面, -1=负面)
        score: 情感得分
    """
    model, word_dict, label_dict = _load_resources()
    
    # 反转label字典，用于获取标签名
    # label_dict: {原始标签: 索引}，如 {1: 0, 0: 1} 表示标签1对应索引0
    inv_label_dict = {v: k for k, v in label_dict.items()}
    
    # 文本编码
    x = [[word_dict.get(char, 0) for char in text]]
    x = pad_sequences(maxlen=INPUT_SHAPE, sequences=x, padding='post', value=0)
    
    # 模型预测
    output = model.predict(x, verbose=0)
    probabilities = output[0]
    
    # label_dict: {1: 0, 0: 1} 表示：索引0=正面(标签1)，索引1=负面(标签0)
    positive_prob = probabilities[label_dict[1]]  # 正面概率
    negative_prob = probabilities[label_dict[0]]  # 负面概率
    
    if debug:
        print(f"正面概率: {positive_prob:.4f}, 负面概率: {negative_prob:.4f}")
    
    # 判断情感倾向
    # 情感得分统一用正面概率表示：正面文本得分高，负面文本得分低
    if positive_prob > negative_prob:
        sentiment = 1
    else:
        sentiment = -1
    score = float(positive_prob)
    
    return sentiment, score


if __name__ == '__main__':
    # 测试 - 使用训练数据风格的文本
    test_texts = [
        '太开心了哈哈哈鼓掌',      # 正面风格
        '好喜欢这首歌爱你',        # 正面风格  
        '太难过了泪泪泪',          # 负面风格
        '真的好衰啊怒',            # 负面风格
    ]
    
    for text in test_texts:
        sentiment, score = predict(text, debug=True)
        print(f"文本: {text}")
        print(f"情感倾向: {'正面' if sentiment == 1 else '负面'}, 情感得分: {score:.4f}\n")
