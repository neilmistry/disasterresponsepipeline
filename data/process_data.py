import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    Loads the messages and categories csv files, from the filepath specified
    Args:
        messages_filepath: Filepath to the messages dataset
        categories_filepath: Filepath to the categories dataset
    Returns:
        (DataFrame) df: Merged dataset returned in a pandas dataframe
    """
    
    messages = pd.read_csv(messages_filepath) #read messages
    categories = pd.read_csv(categories_filepath) #read categories
    df = messages.merge(categories, on='id',how="left") #merge messages with categories
    
    return df

def clean_data(df):
    """ cleans the dataset """
    
    categories_clean = df['categories'].str.split(pat=";",expand=True) #retreive category names
    
    row = categories_clean.iloc[1,:]
    category_colnames = row.apply(lambda x: x[:-2])
    categories_clean.columns = category_colnames
    
    for column in categories_clean:
    # set each value to be the last character of the string
        categories_clean[column] = categories_clean[column].apply(lambda x: x[-1:])
    # convert column from string to numeric
        categories_clean[column] = categories_clean[column].apply(lambda x: pd.to_numeric(x))
        
    df.drop(columns='categories',inplace=True)
    df = pd.concat([df,categories_clean], axis=1) 
    df.drop_duplicates(inplace=True) # remove duplicate rows
    
    return df


def save_data(df, database_filename):
    """ saves the data to a SQL lite database """
    
    engine = create_engine('sqlite:///'+ database_filename)
    df.to_sql('df', engine, index=False)


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()