'''
Created on Feb 27, 2024

@author: immanueltrummer
'''
from argparse import ArgumentParser
from llmjoin.real.analyze import analyze_stats
from llmjoin.real.analyze import analyze_results
from pandas import read_csv
from pathlib import Path


if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument('dir', type=str, help='Path to result directory')
    args = parser.parse_args()

    for op_name in [
        'tuple_join', 'block_join', 
        'adaptive_join', 'embedding_join']:
        for scenario, ref_name in [
            ('inconsistency', 'inconsistencies.csv'),
            ('inconsistency50names', 'inconsistencies50names.csv'),
            ('inconsistency100names', 'inconsistencies100names.csv'),
            ('inconsistency150names', 'inconsistencies150names.csv'),
            ('inconsistency200names', 'inconsistencies200names.csv'),
            ('inconsistency250names', 'inconsistencies250names.csv'),
            ('same_review', 'same_reviews.csv'),
            ('ad_matches', 'ad_matches_search.csv')]:

            print(f'*** {scenario} - {op_name} ***')
            
            prefix = f'{op_name}_{scenario}_'
            ref_path = Path('testdata') / ref_name
            results_dir = Path(args.dir)
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