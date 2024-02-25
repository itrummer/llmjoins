'''
Created on Feb 24, 2024

@author: immanueltrummer
'''
import pandas


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


if __name__ == '__main__':
    
    inconsistency_benchmark()