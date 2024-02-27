'''
Created on Feb 25, 2024

@author: immanueltrummer
'''
import argparse
from llmjoin.real.adaptive_join import adaptive_join
from llmjoin.real.block_join import block_join
from llmjoin.real.tuple_join import tuple_join
import openai
import pandas


def run_benchmark(client, df1, df2, predicate, scenario):
    """ Benchmark join algorithms in given scenario.
    
    Args:
        client: OpenAI client.
        df1: left join input.
        df2: right join input.
        predicate: join predicate.
        scenario: scenario name (used in names of output files).
    """
    for join_op, op_name in [
        # (adaptive_join, 'adaptive_join'),
        # (block_join, 'block_join'),
        (tuple_join, 'tuple_join'),
        ]:
    
        statistics, result = join_op(
            client, df1, df2, 
            predicate, model)
        
        statistics = pandas.DataFrame(statistics)
        result = pandas.DataFrame(result)
        statistics.to_csv(f'testresults/{op_name}_{scenario}_stats.csv')
        result.to_csv(f'testresults/{op_name}_{scenario}_results.csv')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('ai_key', type=str, help='OpenAI access key')
    args = parser.parse_args()
    
    client = openai.OpenAI(api_key=args.ai_key, timeout=20)
    model = 'gpt-4'

    reviews_1 = pandas.read_csv('testdata/reviews_1.csv')
    reviews_2 = pandas.read_csv('testdata/reviews_2.csv')
    #predicate = 'The two reviews express the same sentiment'
    predicate = 'both reviews are positive or both are negative'
    run_benchmark(client, reviews_1, reviews_2, predicate, 'same_review')

    # emails = pandas.read_csv('testdata/emails.csv')
    # statements = pandas.read_csv('testdata/statements.csv')
    # predicate = 'The two texts contradict each other'
    # run_benchmark(client, statements, emails, predicate, 'inconsistency')