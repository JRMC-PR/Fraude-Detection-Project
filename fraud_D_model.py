#!/usr/bin/env python 3
""" Train a Random Forest model to predict fraudulent accounts """


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt


# Step 1: Load the dataset
data_path = "client_info.csv"  # Replace with your dataset path
df = pd.read_csv(data_path)

# Step 2: Simulate a target variable (example logic for fraud detection)
df['is_fraud'] = (df['account_status'] == 'suspended').astype(int)  # Example: 'suspended' accounts are fraudulent

# Step 3: Encode all categorical features
# Extract email provider
df['email_provider'] = df['email'].apply(lambda x: x.split('@')[-1])

# Encode categorical columns using LabelEncoder
categorical_cols = ['account_status', 'email_provider']
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Prepare features and target
X = df.drop(['client_id', 'first_name', 'last_name', 'address', 'email', 'phone_number',
             'account_creation_date', 'is_fraud'], axis=1)
y = df['is_fraud']

# Step 4: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 5: Train the Random Forest model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Step 6: Evaluate the model
y_pred = model.predict(X_test)
classification_rep = classification_report(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
roc_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

# Print evaluation results
print("Classification Report:\n", classification_rep)
print("Confusion Matrix:\n", conf_matrix)
print("ROC-AUC Score:", roc_auc)

# Step 7: Feature Importance
feature_importances = pd.Series(model.feature_importances_, index=X.columns)
plt.figure(figsize=(10, 6))
feature_importances.sort_values(ascending=False).plot(kind='bar', title='Feature Importance')
plt.ylabel('Importance')
plt.show()
