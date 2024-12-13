import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Load the dataset with the correct delimiter
file_path = 'natives (1).tsv'  # Update with your file's path
data = pd.read_csv(file_path, sep=';')

# Check for any missing data in the 'Category' column
data = data.dropna(subset=['Category'])

# Combine the 'Package', 'Class', and 'Method' columns to form a text feature
data['text'] = data['Package'] + ' ' + data['Class'] + ' ' + data['Method']

# Split the dataset into features (X) and labels (y)
X = data['text']
y = data['Category']  # Using the 'Category' column as the target variable

# Split the dataset into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Convert the text data into numerical vectors using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train a Logistic Regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_train_tfidf, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test_tfidf)

# Evaluate the model's performance
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
