'''
Created on Feb 24, 2024

@author: immanueltrummer
'''
import pandas
import tiktoken

encoder = tiktoken.encoding_for_model('gpt-4')


def inconsistency_benchmark():
    """ Generates join input and output files for inconsistency scenario. 
    
    The goal of the join is to find statements that are inconsistencies
    with information discussed in a collection of emails.
    """
    names = [
        'Joe', 'Martin', 'Jane', 'Julia', 'Jeff', 
        'Victor', 'Bob', 'Alice', 'Rosy', 'Bella']
    
    statements = []
    for name in names:
        statement = f'{name}: "I first heard about the losses in February 2022."'
        statements += [statement]
    
    emails = []
    for name in names:
        emails.append(f'I told {name} about the losses in February 2022.')
        emails.append(f'I told {name} about the losses on 2/5/2022.')
        emails.append(f'I told {name} about the losses on 2/7/2022.')
        emails.append(f'I told {name} about the losses after January 2022.')
        emails.append(f'I told {name} about the losses in the first half of February 2022.')
        emails.append(f'I told {name} about the losses some time in 2022.')
        emails.append(f'I told {name} about the losses not before the year 2022.')
        emails.append(f'I told {name} about the losses in 2022 or 2021.')
        emails.append(f'I told {name} about the losses before 2023.')
        emails.append(f'I told {name} about the losses in October 2021.')

    results = []
    for statement in statements:
        for email in emails:
            inconsistent = False
            if 'October' in email:
                for name in names:
                    if name in statement and name in email:
                        inconsistent = True
            results += [{'text1':statement, 'text2':email, 'joins':inconsistent}]
    
    pandas.DataFrame({'text':statements}).to_csv('testdata/statements.csv')
    pandas.DataFrame({'text':emails}).to_csv('testdata/emails.csv')
    pandas.DataFrame(results).to_csv('testdata/inconsistencies.csv')


def movie_benchmarks():
    """ Generates benchmarks matching reviews, based on sentiment. """
    
    def shorten_review(review):
        """ Shortens review if above 100 tokens.
        
        Args:
            review: shortens this review.
        
        Returns:
            Shortened review.
        """
        tokens = encoder.encode(review)
        nr_tokens = len(tokens)
        if nr_tokens > 100:
            return encoder.decode(tokens[:100]) + ' ...'
        else:
            return review
    
    all_reviews = pandas.read_csv('testdata/all_reviews.csv')
    all_reviews['text'] = all_reviews.apply(
        lambda r:shorten_review(r['text']), axis=1)
    reviews_1 = all_reviews.iloc[:50]
    reviews_2 = all_reviews.iloc[50:]
    
    reviews_1.to_csv('testdata/reviews_1.csv')
    reviews_2.to_csv('testdata/reviews_2.csv')
    
    same_results = []
    different_results = []
    for _, row_1 in reviews_1.iterrows():
        for _, row_2 in reviews_2.iterrows():
            review_1 = row_1['text']
            review_2 = row_2['text']
            sentiment_1 = row_1['sentiment']
            sentiment_2 = row_2['sentiment']
            
            result = {'text1':review_1, 'text2':review_2}
            is_same = (sentiment_1 == sentiment_2)
            same_result = result.copy() | {'joins':is_same}
            same_results.append(same_result)
            different_result = result.copy() | {'joins':not is_same}
            different_results.append(different_result)
    
    pandas.DataFrame(same_results).to_csv('testdata/same_reviews.csv')
    pandas.DataFrame(different_results).to_csv('testdata/different_reviews.csv')


if __name__ == '__main__':
    
    inconsistency_benchmark()
    movie_benchmarks()