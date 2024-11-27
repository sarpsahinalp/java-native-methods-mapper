import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder

# Load the dataset with the correct delimiter
file_path = 'natives (1).tsv'
data = pd.read_csv(file_path, sep=';')

# Check for any missing data in the 'Category' column
data = data.dropna(subset=['Category'])

# Combine the 'Package', 'Class', and 'Method' columns to form a text feature
data['text'] = data['Package'] + ' ' + data['Class'] + ' ' + data['Method']

# Split the dataset into features (X) and labels (y)
X = data['text']
y = data['Category']  # Using the 'Category' column as the target variable

# Encode labels as integers (required for neural network)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split the dataset into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Convert the text data into numerical vectors using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# --- Random Forest Model ---
# Train a Random Forest Classifier
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_tfidf, y_train)

# Make predictions with Random Forest
rf_y_pred = rf_model.predict(X_test_tfidf)

# Evaluate the Random Forest model's performance
print("Random Forest Classifier Accuracy:", accuracy_score(y_test, rf_y_pred))
print("\nRandom Forest Classification Report:\n", classification_report(y_test, rf_y_pred))

# --- Neural Network Model ---
# Convert target labels to one-hot encoding for neural network
y_train_onehot = to_categorical(y_train, num_classes=len(label_encoder.classes_))
y_test_onehot = to_categorical(y_test, num_classes=len(label_encoder.classes_))

# Build a simple neural network model
nn_model = Sequential()
nn_model.add(Dense(512, activation='relu', input_dim=X_train_tfidf.shape[1]))
nn_model.add(Dropout(0.5))  # Dropout layer for regularization
nn_model.add(Dense(256, activation='relu'))
nn_model.add(Dense(len(label_encoder.classes_), activation='softmax'))  # Output layer for multi-class classification

# Compile the model
nn_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the neural network model
nn_model.fit(X_train_tfidf, y_train_onehot, epochs=10, batch_size=32, validation_data=(X_test_tfidf, y_test_onehot),
             verbose=1)

# Make predictions with the neural network
nn_y_pred = nn_model.predict(X_test_tfidf)
nn_y_pred_classes = nn_y_pred.argmax(axis=1)

# Evaluate the neural network model's performance
print("\nNeural Network Model Accuracy:", accuracy_score(y_test, nn_y_pred_classes))
print("\nNeural Network Classification Report:\n", classification_report(y_test, nn_y_pred_classes))

# --- Save Models ---
# Save the trained Random Forest model and vectorizer
joblib.dump(rf_model, 'random_forest_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

# Save the neural network model
nn_model.save('neural_network_model.h5')

# Optionally, save label encoder to decode predictions
joblib.dump(label_encoder, 'label_encoder.pkl')
