import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, 
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    confusion_matrix
)
import numpy as np

from .dataset import load_training_data
from .features import build_vectorizer


DB_PATH = "db/soulsense.db"
MODEL_PATH = "Emotion_Classification/model.pkl"


def train():
    """Train emotion classifier with comprehensive evaluation metrics"""
    print("\n" + "="*60)
    print("Training Emotion Classification Model")
    print("="*60 + "\n")
    
    texts, labels = load_training_data(DB_PATH)
    print(f"📊 Loaded {len(texts)} training samples")

    vectorizer = build_vectorizer()
    X = vectorizer.fit_transform(texts)

    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=0.2, random_state=42
    )
    
    print(f"   Training samples: {X_train.shape[0]}")
    print(f"   Test samples: {X_test.shape[0]}")

    print("\n🔄 Training Logistic Regression model...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # Predictions
    train_preds = model.predict(X_train)
    test_preds = model.predict(X_test)

    # Calculate comprehensive metrics
    train_acc = accuracy_score(y_train, train_preds)
    test_acc = accuracy_score(y_test, test_preds)
    
    precision = precision_score(y_test, test_preds, average='weighted', zero_division=0)
    recall = recall_score(y_test, test_preds, average='weighted', zero_division=0)
    f1 = f1_score(y_test, test_preds, average='weighted', zero_division=0)
    
    print(f"\n✅ Training Complete!")
    print(f"\n📊 Performance Metrics:")
    print(f"   Training Accuracy:  {train_acc:.4f} ({train_acc*100:.2f}%)")
    print(f"   Test Accuracy:      {test_acc:.4f} ({test_acc*100:.2f}%)")
    print(f"   Precision (weighted): {precision:.4f}")
    print(f"   Recall (weighted):    {recall:.4f}")
    print(f"   F1-Score (weighted):  {f1:.4f}")
    
    print("\n📋 Detailed Classification Report:")
    class_names = ['Negative', 'Neutral', 'Positive']
    print(classification_report(y_test, test_preds, target_names=class_names, zero_division=0))
    
    print("\n📈 Confusion Matrix:")
    cm = confusion_matrix(y_test, test_preds)
    print(cm)

    # Save model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    joblib.dump(
        {"model": model, "vectorizer": vectorizer},
        MODEL_PATH
    )

    print(f"\n✅ Emotion classification model saved: {MODEL_PATH}")


if __name__ == "__main__":
    train()
