'''
Created on Feb 27, 2024

@author: immanueltrummer
'''
from llmjoin.real.analyze import analyze_stats
from llmjoin.real.analyze import analyze_results
from pandas import read_csv
from pathlib import Path


if __name__ == '__main__':

    for scenario, ref_name in [
        ('inconsistency', 'inconsistencies.csv'), 
        ('same_review', 'same_reviews.csv'),]:
        for op_name in ['adaptive_join', 'block_join', 'tuple_join']:
            print(f'*** {scenario} - {op_name} ***')
            
            prefix = f'{op_name}_{scenario}_'
            ref_path = Path('testdata') / ref_name
            results_dir = Path('testresults')
            result_path = results_dir / f'{prefix}results.csv'
            stats_path = results_dir / f'{prefix}stats.csv'
            
            if not result_path.exists() or not stats_path.exists():
                print('At least one file does not exist:')
                print(result_path)
                print(stats_path)
                continue
            
            reference = read_csv(str(ref_path))
            results = read_csv(str(result_path))
            stats = read_csv(str(stats_path))
            
            analyze_results(reference, results)
            analyze_stats(stats)