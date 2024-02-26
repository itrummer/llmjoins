'''
Created on Feb 24, 2024

@author: immanueltrummer
'''
import argparse
import pandas


def analyze_results(reference, results):
    """ Print result statistics after comparison to reference.
    
    Args:
        reference: data frame with reference results.
        results: results to evaluate.
    """
    ref_rows = reference[reference['joins']].copy()
    ref_rows['resultpair'] = ref_rows.apply(
        lambda r:(r['text1'], r['text2']), axis=1)
    ref_tuples = set(ref_rows['resultpair'])
    nr_refs = len(ref_tuples)
    
    nr_correct = 0
    nr_incorrect = 0
    for _, row in results.iterrows():
        result_tuple = (row['tuple1'], row['tuple2'])
        if result_tuple in ref_tuples:
            nr_correct += 1
        else:
            nr_incorrect += 1
    
    nr_results = len(results)
    recall = nr_correct/nr_refs
    precision = nr_correct/nr_results
    f1_score = 2 * precision * recall / (precision+recall)
    
    print(f'Recall:   \t{recall}')
    print(f'Precision:\t{precision}')
    print(f'F1 Score: \t{f1_score}')


def analyze_stats(stats):
    """ Print aggregate performance statistics.
    
    Args:
        stats: performance statistics.
    """
    seconds = stats['seconds'].sum()
    tokens_read = stats['tokens_read'].sum()
    tokens_written = stats['tokens_written'].sum()
    dollars = tokens_read * 0.03/1000 + tokens_written * 0.06/1000
    
    print(f'Tokens read:   \t{tokens_read}')
    print(f'Tokens written:\t{tokens_written}')
    print(f'Seconds:       \t{seconds}')
    print(f'Dollars:       \t{dollars}')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('refpath', type=str, help='Path to reference result')
    parser.add_argument('resultpath', type=str, help='Path to join results')
    parser.add_argument('statspath', type=str, help='Path to input statistics')
    args = parser.parse_args()
    
    reference = pandas.read_csv(args.refpath)
    results = pandas.read_csv(args.resultpath)
    stats = pandas.read_csv(args.statspath)
    
    analyze_results(reference, results)
    analyze_stats(stats)