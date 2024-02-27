'''
Created on Feb 24, 2024

@author: immanueltrummer
'''
from llmjoin.real.block_join import block_join


def adaptive_join(client, df1, df2, predicate, model, estimate=0.001):
    """ Perform block join with adaptive selectivity estimates.
    
    Args:
        client: OpenAI client.
        df1: first input table.
        df2: second input table.
        predicate: join predicate as text.
        model: name of OpenAI model.
        estimate: initial selectivity estimate.
    
    Returns:
        performance statistics, result
    """
    overflow = True
    
    all_stats = []
    while overflow:
        stats, result = block_join(
            client, df1, df2, predicate, 
            model, estimate)
        
        all_stats += stats
        overflow = any([s['overflow'] for s in stats])
        estimate *= 4
        print(f'*** New estimate: {estimate} ***')
    
    return all_stats, result