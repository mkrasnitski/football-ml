import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_data(year):
	stats = pd.read_csv(f'{year}/{year}_stats.csv', index_col=0)
	results = pd.read_csv(f'{year}/{year}_results.csv')

	train_data = []
	train_labels = []

	for i, (teamA, teamB, A_win, B_win) in results.iterrows():
		if A_win or B_win:
			train_data.append(stats.loc[[teamA, teamB]].values.flatten())
			train_labels.append((A_win, B_win)) # index of winner

	return np.array(train_data), np.array(train_labels)

train_data, train_labels = get_data(2018)
print(train_data.shape, train_labels.shape)

model = keras.Sequential([
	keras.layers.Dense(train_data.shape[-1], activation=tf.nn.sigmoid, input_shape=[train_data.shape[-1]]),
	keras.layers.Dense(2, activation=tf.nn.softmax),
])
optimizer = keras.optimizers.Adam(lr=0.0001, decay=0.00001)
model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

model.summary()
history = model.fit(train_data, train_labels, epochs=10000, verbose=2)

history_dict = history.history
acc = history_dict['accuracy']
loss = history_dict['loss']

epochs = range(1, len(acc) + 1)

plt.plot(epochs, loss, label='Training loss')
plt.plot(epochs, acc, label='Training Accuracy')
plt.title('Training stats')
plt.xlabel('Epochs')
plt.ylabel('Stats')
plt.legend()

plt.show()