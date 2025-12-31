import argparse
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from src import OneHotEncoder, BagOfWords, TFIDF
from src import load_dataset, get_category_names


def train_and_evaluate(representation='bow', classifier='lr'):
    """
    Train and evaluate text classification
    
    Args:
        representation: Type of text representation ('onehot', 'bow', 'tfidf')
        classifier: Type of classifier ('lr' for Logistic Regression, 'nb' for MultinomialNB)
    """
    print("="*80)
    print(f"TEXT CLASSIFICATION - {representation.upper()} + {classifier.upper()}")
    print("="*80)
    
    # Load data
    print("\nLoading dataset...")
    X_train, y_train, X_test, y_test = load_dataset('data')
    
    # Chọn phương pháp biểu diễn
    print(f"\nRepresentation method: {representation.upper()}")
    print(f"Classifier: {classifier.upper()}")
    
    if representation == 'onehot':
        vectorizer = OneHotEncoder()
    elif representation == 'bow':
        vectorizer = BagOfWords()
    elif representation == 'tfidf':
        vectorizer = TFIDF()
    else:
        raise ValueError(f"Unknown representation: {representation}")
    
    # Fit trên train data
    print(f"\nFitting {representation.upper()} on training data...")
    X_train_vec = vectorizer.fit_transform(X_train)
    
    # Transform test data
    print(f"Transforming test data...")
    X_test_vec = vectorizer.transform(X_test)
    
    print(f"\nTraining set shape: {X_train_vec.shape}")
    print(f"Test set shape: {X_test_vec.shape}")
    print(f"Number of features: {vectorizer.vocab_size}")
    
    # Chọn classifier
    if classifier == 'lr':
        clf_name = 'Logistic Regression'
        clf = LogisticRegression(max_iter=1000, random_state=42, verbose=0)
    elif classifier == 'nb':
        clf_name = 'Multinomial Naive Bayes'
        clf = MultinomialNB()
    else:
        raise ValueError(f"Unknown classifier: {classifier}")
    
    # Train classifier
    print(f"\nTraining {clf_name}...")
    clf.fit(X_train_vec, y_train)
    
    # Predict
    print("Predicting...")
    y_train_pred = clf.predict(X_train_vec)
    y_test_pred = clf.predict(X_test_vec)
    
    # Evaluate
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"\nTrain Accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)")
    print(f"Test Accuracy:  {test_acc:.4f} ({test_acc*100:.2f}%)")
    
    # Classification report
    category_names = get_category_names()
    print(f"\n{'-'*80}")
    print("Classification Report (Test Set)")
    print(f"{'-'*80}")
    print(classification_report(
        y_test, 
        y_test_pred, 
        target_names=category_names,
        digits=4
    ))
    
    # Confusion matrix
    print(f"{'-'*80}")
    print("Confusion Matrix (Test Set)")
    print(f"{'-'*80}")
    cm = confusion_matrix(y_test, y_test_pred)
    
    # In confusion matrix với tên category
    print(f"\n{'':>12}", end='')
    for name in category_names:
        print(f"{name:>12}", end='')
    print()
    
    for i, name in enumerate(category_names):
        print(f"{name:>12}", end='')
        for j in range(len(category_names)):
            print(f"{cm[i, j]:>12}", end='')
        print()
    
    print("\n" + "="*80 + "\n")
    
    return {
        'train_accuracy': train_acc,
        'test_accuracy': test_acc,
        'vectorizer': vectorizer,
        'classifier': clf
    }


def compare_all_methods(classifier='lr'):
    """
    Compare all representation methods
    
    Args:
        classifier: Type of classifier ('lr' or 'nb')
    """
    clf_name = 'Logistic Regression' if classifier == 'lr' else 'Multinomial Naive Bayes'
    print("\n" + "="*80)
    print(f"COMPARING ALL REPRESENTATION METHODS - {clf_name.upper()}")
    print("="*80 + "\n")
    
    methods = ['onehot', 'bow', 'tfidf']
    results = {}
    
    for method in methods:
        result = train_and_evaluate(method, classifier)
        results[method] = result
        print("\n")
    
    # Summary
    print("="*80)
    print("SUMMARY COMPARISON")
    print("="*80)
    print(f"\n{'Method':<15} {'Train Acc':<15} {'Test Acc':<15} {'Features':<15}")
    print("-"*60)
    
    for method in methods:
        train_acc = results[method]['train_accuracy']
        test_acc = results[method]['test_accuracy']
        n_features = results[method]['vectorizer'].vocab_size
        print(f"{method.upper():<15} {train_acc:.4f} ({train_acc*100:.2f}%)  {test_acc:.4f} ({test_acc*100:.2f}%)  {n_features:<15}")
    
    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Text classification using Logistic Regression or Multinomial Naive Bayes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python text_classification.py -r bow -clf lr              # BoW + Logistic Regression
  python text_classification.py -r tfidf -clf nb            # TF-IDF + Naive Bayes
  python text_classification.py -r bow -clf nb              # BoW + Naive Bayes
  python text_classification.py --compare -clf lr           # Compare all (LR)
  python text_classification.py --compare -clf nb           # Compare all (NB)
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--representation', '-r',
        type=str,
        choices=['onehot', 'bow', 'tfidf'],
        help='Text representation method'
    )
    group.add_argument(
        '--compare', '-c',
        action='store_true',
        help='Compare all representation methods'
    )
    
    parser.add_argument(
        '--classifier', '-clf',
        type=str,
        choices=['lr', 'nb'],
        default='lr',
        help='Classifier: lr (Logistic Regression) or nb (Multinomial Naive Bayes)'
    )
    
    args = parser.parse_args()
    
    if args.compare:
        compare_all_methods(args.classifier)
    else:
        train_and_evaluate(args.representation, args.classifier)


if __name__ == "__main__":
    main()
