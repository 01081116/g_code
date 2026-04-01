import pickle

import jieba
import numpy as np
import pandas as pd
from keras.utils import np_utils
from keras.models import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.layers import LSTM, Dense, Embedding, Dropout, Bidirectional
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.regularizers import l2
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
from sklearn.metrics import precision_score, accuracy_score, recall_score, f1_score, confusion_matrix, roc_curve, auc

rcParams['font.family'] = 'SimHei'


def segment_text(text, stopwords):
    """对文本进行分词并去除停用词"""
    words = jieba.lcut(str(text))
    return [word for word in words if word not in stopwords and word.strip()]


def load_data(filepath, input_shape=20):
    """加载并预处理数据"""
    df = pd.read_csv(filepath)
    df.dropna(inplace=True)

    labels, vocabulary = list(df['label'].unique()), list(df['review'].unique())

    string = ''
    for word in vocabulary:
        string += word
    vocabulary = set(string)

    # 字典列表
    word_dictionary = {word: i + 1 for i, word in enumerate(vocabulary)}
    with open('./word_dict.pk', 'wb') as f:
        pickle.dump(word_dictionary, f)
    inverse_word_dictionary = {i + 1: word for i, word in enumerate(vocabulary)}
    label_dictionary = {label: i for i, label in enumerate(labels)}
    with open('./label_dict.pk', 'wb') as f:
        pickle.dump(label_dictionary, f)
    output_dictionary = {i: labels for i, labels in enumerate(labels)}

    vocab_size = len(word_dictionary.keys())
    label_size = len(label_dictionary.keys())

    # 序列填充
    x = [[word_dictionary[word] for word in sent] for sent in df['review']]
    x = pad_sequences(maxlen=input_shape, sequences=x, padding='post', value=0)
    y = [[label_dictionary[sent]] for sent in df['label']]
    y = [np_utils.to_categorical(label, num_classes=label_size) for label in y]
    y = np.array([list(_[0]) for _ in y])

    return x, y, output_dictionary, vocab_size, label_size, inverse_word_dictionary


def load_test(text, input_shape=50):
    """加载测试数据"""
    with open('./word_dict.pk', mode='rb') as fr:
        word_dictionary = pickle.load(fr)

    inverse_word_dictionary = {i: word for word, i in word_dictionary.items()}
    x = [[word_dictionary.get(word, 0) for word in text]]
    x = pad_sequences(maxlen=input_shape, sequences=x, padding='post', value=0)

    return x, inverse_word_dictionary


def create_LSTM(n_units, input_shape, output_dim, vocab_size, label_size, use_bidirectional=True):
    """
    创建LSTM模型
    参数:
        n_units: LSTM单元数
        input_shape: 输入序列长度
        output_dim: Embedding维度
        vocab_size: 词汇表大小
        label_size: 标签类别数
        use_bidirectional: 是否使用双向LSTM
    """
    model = Sequential()

    # Embedding层
    model.add(Embedding(input_dim=vocab_size + 1, output_dim=output_dim,
                        input_length=input_shape, mask_zero=True))

    # LSTM层 - 可选双向
    if use_bidirectional:
        model.add(Bidirectional(LSTM(n_units, return_sequences=False, 
                                      kernel_regularizer=l2(0.001),
                                      recurrent_regularizer=l2(0.001))))
    else:
        model.add(LSTM(n_units, return_sequences=False,
                       kernel_regularizer=l2(0.001),
                       recurrent_regularizer=l2(0.001)))

    model.add(Dropout(0.3))
    model.add(Dense(64, activation='relu', kernel_regularizer=l2(0.001)))
    model.add(Dropout(0.2))
    model.add(Dense(label_size, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.summary()

    return model


def model_train(input_shape, filepath, model_save_path):
    """训练LSTM模型"""
    x, y, output_dictionary, vocab_size, label_size, inverse_word_dictionary = load_data(filepath, input_shape)
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.1, random_state=42)

    # 模型参数
    n_units = 128
    batch_size = 256
    epochs = 30
    output_dim = 64

    # 创建模型
    model = create_LSTM(n_units, input_shape, output_dim, vocab_size, label_size, use_bidirectional=True)

    # 回调函数（增加patience，让模型有更多机会收敛）
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6)

    # 训练模型
    history = model.fit(
        train_x, train_y,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,
        callbacks=[early_stop, reduce_lr],
        verbose=1
    )

    # 保存模型
    model.save(model_save_path)

    # 绘制训练曲线
    plot_training_history(history, 'lstm')

    # 模型评估
    evaluate_model(model, test_x, test_y, 'lstm')


def plot_training_history(history, model_name):
    """绘制训练过程曲线"""
    plt.figure(figsize=(12, 4))

    # Loss曲线
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Loss over Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    # Accuracy曲线
    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Accuracy over Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'{model_name}_训练过程.png')
    plt.show()


def evaluate_model(model, test_x, test_y, model_name):
    """评估模型性能"""
    y_pred = [np.argmax(pred) for pred in model.predict(test_x)]
    y_true = [np.argmax(true) for true in test_y]

    # 计算指标
    precision = precision_score(y_true, y_pred, average='weighted')
    acc = accuracy_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred, average='weighted')
    f1 = f1_score(y_true, y_pred, average='weighted')

    print(f"\n{'=' * 40}")
    print(f"Precision: {precision:.4f}")
    print(f"Accuracy: {acc:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"{'=' * 40}\n")

    # 保存评估结果
    with open(f'{model_name}_评估.txt', 'w', encoding='utf-8') as file:
        file.write(f"Precision: {precision:.4f}\n")
        file.write(f"Accuracy: {acc:.4f}\n")
        file.write(f"Recall: {recall:.4f}\n")
        file.write(f"F1 Score: {f1:.4f}\n")

    # 混淆矩阵
    conf_matrix = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap='Blues')
    plt.xlabel('Predicted labels')
    plt.ylabel('True labels')
    plt.title('Confusion Matrix')
    plt.savefig(f'{model_name}_混淆矩阵.png')
    plt.show()

    # ROC曲线
    fpr, tpr, _ = roc_curve(y_true, y_pred)
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend(loc="lower right")
    plt.savefig(f'{model_name}_ROC曲线.png')
    plt.show()


if __name__ == '__main__':
    filepath = 'data/clean.csv'
    input_shape = 50
    model_save_path = './lstm_model.h5'

    model_train(input_shape, filepath, model_save_path)
