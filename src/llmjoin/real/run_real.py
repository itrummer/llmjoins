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


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('ai_key', type=str, help='OpenAI access key')
    args = parser.parse_args()
    
    client = openai.OpenAI(api_key=args.ai_key, timeout=10)
    model = 'gpt-4'

    emails = pandas.read_csv('testdata/emails.csv')
    statements = pandas.read_csv('testdata/statements.csv')
    predicate = 'The two texts contradict each other'
    
    for join_op, op_name in [
        (adaptive_join, 'adaptive_join'),
        # (block_join, 'block_join'),
        # (tuple_join, 'tuple_join'),
        ]:
    
        statistics, result = join_op(
            client, statements, emails, 
            predicate, model)
        
        statistics = pandas.DataFrame(statistics)
        result = pandas.DataFrame(result)
        statistics.to_csv(f'testresults/{op_name}_inconsistency_stats.csv')
        result.to_csv(f'testresults/{op_name}_inconsistency_results.csv')