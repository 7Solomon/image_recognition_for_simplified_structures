
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.models import load_model
from sklearn.model_selection import train_test_split

import numpy as np
import os

def split_data(image_height, image_width):
  batch_size = 10

  train_datagen = ImageDataGenerator(
    rescale=1.0/255.0,  # Rescale pixel values to [0, 1]
    rotation_range=40,  # Randomly rotate images
    width_shift_range=0.3,  # Randomly shift images horizontally
    height_shift_range=0.3,  # Randomly shift images vertically
    shear_range=0.2,  # Shear transformation
    zoom_range=0.2,  # Random zoom
    horizontal_flip=True,  # Randomly flip images horizontally
    fill_mode='nearest'  # Fill mode for new pixels after rotation or shifting
  )

  data_dir = 'content/data'
  class_names = sorted(os.listdir(data_dir))

  # Split data into training and validation sets
  train_dir, validation_dir = train_test_split(
  class_names, test_size=0.2, random_state=42)

  train_generator = train_datagen.flow_from_directory(
      os.path.join(data_dir, 'train'),
      target_size=(image_height, image_width),
      batch_size=batch_size,
      class_mode='categorical'
    )

  validation_generator = train_datagen.flow_from_directory(
        os.path.join(data_dir, 'validation'),
        target_size=(image_height, image_width),
        batch_size=batch_size,
        class_mode='categorical'
    )
  return train_generator, validation_generator

def define_neural_net(image_height, image_width, num_classes):
  model = Sequential()
  model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(image_height, image_width, 3)))
  model.add(MaxPooling2D((2, 2)))
  model.add(Conv2D(128, (3, 3), activation='relu'))
  model.add(MaxPooling2D((2, 2)))
  model.add(Flatten())
  model.add(Dense(64, activation='relu'))
  model.add(Dense(num_classes, activation='softmax'))  # num classes ist len(train_data)

  model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
  return model

def train_modell():
  num_epochs = 100  # Adjust the number of epochs as needed
  image_height, image_width = 120, 120

  train_generator, validation_generator = split_data(image_height, image_width)# Ist in get Imgae in part defined
  model = define_neural_net(image_height, image_width, len(train_generator.class_indices))

  history = model.fit(train_generator, epochs=num_epochs, validation_data=validation_generator, )
  model_gen = len(os.listdir('content/models')) + 2
  model.save(f'content/models/model_{model_gen}.h5')
  print(f'---------- model_{model_gen} --------')
  print("Training accuracy:", history.history['accuracy'])
  print("Validation accuracy:", history.history['val_accuracy'])
  print("Training loss:", history.history['loss'])
  print("Validation loss:", history.history['val_loss'])
  print('---------- saved_model: -------')

def c_load_modell():
  model_gen = len(os.listdir('content/models')) + 1
  loaded_model = load_model(f'content/models/model_{model_gen}.h5')
  return loaded_model


def predict_on_data(img, loaded_model):
  img = img / 255.0       # Normalize
  img = np.expand_dims(img, axis=0)    # Add a batch dimension to the input image
  predictions = loaded_model.predict(img)
  return predictions

if __name__ == '__main__':
    train_modell()


