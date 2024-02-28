'''
Created on Feb 24, 2024

@author: immanueltrummer
'''
import dataclasses
import pandas
import tiktoken
import typing

encoder = tiktoken.encoding_for_model('gpt-4')


def inconsistency_benchmark(names, variant):
    """ Generates join input and output files for inconsistency scenario.
    
    The goal of the join is to find statements that are inconsistencies
    with information discussed in a collection of emails.
    
    Args:
        names: first names of people.
        variant: name of benchmark variant.
    """
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
    
    statements_path = f'testdata/statements{variant}.csv'
    emails_path = f'testdata/emails{variant}.csv'
    results_path = f'testdata/inconsistencies{variant}.csv'
    pandas.DataFrame({'text':statements}).to_csv(statements_path)
    pandas.DataFrame({'text':emails}).to_csv(emails_path)
    pandas.DataFrame(results).to_csv(results_path)


def inconsistency_benchmarks():
    """ Generates benchmarks on spotting inconsistent statements. """
    few_names = [
        'Joe', 'Martin', 'Jane', 'Julia', 'Jeff', 
        'Victor', 'Bob', 'Alice', 'Rosy', 'Bella']
    inconsistency_benchmark(few_names, '')
    many_names = list(pandas.read_csv('testdata/names.csv')['name'][:100])
    inconsistency_benchmark(many_names, 'XXL')


def movie_benchmarks():
    """ Generates benchmarks focused on matching reviews. """
    
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


def ads_benchmark():
    """ Generates benchmark about matching ads to searches. """
    
    @dataclasses.dataclass
    class Ad():
        """ Represents an add. """
        properties: typing.List[str]
        """ Material, color. """
        
        def __str__(self):
            """ Generates text representation of ad.
            
            Returns:
                ad representation in natural language.
            """
            material, color = self.properties
            return f'Offering table that is {material} and {color}.'

    @dataclasses.dataclass
    class Search():
        """ Represents a search. """
        properties: typing.List[str]
        """ Material color. """
        negations: typing.List[bool]
        """ Whether a property is negated. """
        
        def matches(self, ad):
            """ Returns true iff an ad matches this search.
            
            Args:
                ad: evaluate match with this ad.
            
            Returns:
                True iff the ad matches this search.
            """
            for i in range(2):
                ad_property = ad.properties[i]
                search_property = self.properties[i]
                search_negation = self.negations[i]
                
                properties_equal = (ad_property == search_property)
                if search_negation and properties_equal or \
                    not search_negation and not properties_equal:
                    return False
            
            return True
        
        def __str__(self):
            """ Generates text representation of search.
            
            Returns:
                search represented in natural language.
            """
            material, color = self.properties
            mn, cn = ['not ' if n else '' for n in self.negations]
            return (f'Searching table that is ' 
                    f'{mn}{material} and {cn}{color}.')
    
    materials = [
        'made of wood', 'made of metal', 
        'made of glass', 'made of stone']
    colors = ['blue', 'red', 'white', 'black']
    
    ads = []
    for material in materials:
        for color in colors:
            ad = Ad([material, color])
            ads.append(ad)
    
    searches = []
    for material in materials:
        for color in colors:
            for negations in [[False, False]]:
                properties = [material, color]
                search = Search(properties, negations)
                searches.append(search)

    results = []
    for ad in ads:
        for search in searches:
            matches = search.matches(ad)
            result = {'text1':str(ad), 'text2':str(search), 'joins':matches}
            results.append(result)

    ads_text = [str(a) for a in ads]
    search_text = [str(s) for s in searches]
    pandas.DataFrame({'text':ads_text}).to_csv('testdata/ads.csv')
    pandas.DataFrame({'text':search_text}).to_csv('testdata/searches.csv')
    pandas.DataFrame(results).to_csv('testdata/ad_matches_search.csv')


if __name__ == '__main__':
    
    inconsistency_benchmarks()
    movie_benchmarks()
    ads_benchmark()