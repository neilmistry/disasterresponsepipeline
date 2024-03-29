import sys
import pandas as pd
from sqlalchemy import create_engine
import re
import pickle

import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
    
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from sklearn.model_selection import train_test_split

from sklearn.metrics import classification_report, precision_score, recall_score, f1_score

def load_data(database_filepath):
    """
    Loads data from SQL lite database
    Args:
        database_filepath: path to database
    Returns:
        (DataFrame) X: feature
        (DataFrame) Y: labels
    """
    
    engine = create_engine('sqlite:///' + database_filepath)
    df = pd.read_sql_table('df',engine)
    X = df['message']
    y = df.drop(columns=['id','message','original','genre'], axis=1)
    category_names = y.columns
    return X, y, category_names

def tokenize(text):
    """
    Tokenizes each sentence in a given text.
    Args:
        text: text string
    Returns:
        (str[]): array of clean words
    """
    
    text.lower() # convert to lowercase
    text = re.sub(r"[^a-zA-Z0-9]", " ", text) #remove punctuation
    words = word_tokenize(text) # tokenize by individual word
    words = [w for w in words if w not in stopwords.words("english")] #remove stop words
    lemmed = [WordNetLemmatizer().lemmatize(w) for w in words] #lemminization
  
    return words


def build_model():
    """Builds pipline for classification model """
    
    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', MultiOutputClassifier(RandomForestClassifier()))
    ])
    
    parameters = {
        'vect__ngram_range': ((1, 1), (1, 2)),
        'clf__estimator__min_samples_split': [2, 4],
    }
    
    cv = GridSearchCV(pipeline, param_grid=parameters)

    return cv


def evaluate_model(model, X_test, Y_test, category_names):
    """Evaluate model using testing dataset """
    
    y_preds = model.predict(X_test)
    predictions = pd.DataFrame(data=y_preds, columns=Y_test.columns, index=Y_test.index)
    for col in Y_test.columns:
        print(classification_report(predictions[col],Y_test[col]))


def save_model(model, model_filepath):
    """save our model to a python pickle file ('pkl') """
    pickle.dump(model, open(model_filepath, 'wb'))


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()