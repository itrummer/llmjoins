'''
Created on Feb 23, 2024

@author: immanueltrummer
'''
import argparse
import math
import pandas


def extract_range(range_str):
    """ Extracts range from string representation.
    
    Args:
        range_str: string representation of range.
    
    Returns:
        corresponding range object.
    """
    strings = range_str.split(':')
    integers = [int(s) for s in strings]
    return range(*integers)


def simulate_tuple_join(r1, r2, s1, s2, s3, g, p):
    """ Simulates a tuple join.
    
    Args:
        r1: number of rows in first table.
        r2: number of rows in second table.
        s1: size of tuples in first table.
        s2: size of tuples in second table.
        s3: size of result tuples.
        g: relative cost of token generation.
        p: token size of static prompt part.
    
    Returns:
        A dictionary with simulation results.
    """
    prompt_size = p + s1 + s2 + s3
    output_size = 1
    nr_invocations = r1 * r2
    total_read = prompt_size * nr_invocations
    total_written = output_size * nr_invocations
    total_cost = total_read + total_written * g
    return {
        'tuple_invocations':nr_invocations, 'tuple_cost':total_cost, 
        'tuple_read':total_read, 'tuple_written':total_written}


def simulate_block_join(r1, r2, s1, s2, s3, sigma, estimate, g, p, t):
    """ Simulate block-nested loops join.
    
    Args:
        r1: number of tuples in first table.
        r2: number of tuples in second table.
        s1: size of each tuple in first table.
        s2: size of each tuple in second table.
        s3: size of each output tuple.
        sigma: selectivity of join predicate.
        estimate: either "precise" or "conservative" selectivity estimate.
        g: relative cost of writing tuples.
        p: size of static part of prompt.
        t: maximal number of tuples processed per model invocation.
    
    Returns:
        A dictionary with simulation results.
    """
    b1 = math.floor((math.sqrt(s1*s1*s2*s2+s1*s2*s3*sigma*t)-s1*s2)/(s1*s3*sigma))
    b2 = math.floor((t-b1*s1)/(s2+b1*s3*sigma))
    nr_invocations = math.ceil(r1/b1) * math.ceil(r2/b2)
    prompt_size = p+b1*s1+b2*s2
    output_size = b1*b2*sigma*s3
    total_read = prompt_size * nr_invocations
    total_written = output_size * nr_invocations
    total_cost = total_read + total_written * g
    return {
        f'block_{estimate}_invocations':nr_invocations, 
        f'block_{estimate}_cost':total_cost,
        f'block_{estimate}_read':total_read, 
        f'block_{estimate}_written':total_written}


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('r1', type=str, help='Size range of the first table')
    parser.add_argument('r2', type=int, help='Size of second table')
    parser.add_argument('s1', type=str, help='Size range for first tuple size')
    parser.add_argument('s2', type=int, help='Size of tuples in second table')
    parser.add_argument('s3', type=int, help='Size of output tuples')
    parser.add_argument('sigma_pm', type=str, help='Selectivity range pro mille')
    parser.add_argument('g', type=float, help='Relative cost of output tokens')
    parser.add_argument('t', type=int, help='Maximal #tokens per invocation')
    parser.add_argument('p_tuple', type=int, help='Static size for tuple join')
    parser.add_argument('p_block', type=int, help='Static size for block join')
    parser.add_argument('out_file', type=str, help='Name of result file')
    args = parser.parse_args()
    
    r1_range = extract_range(args.r1)
    s1_range = extract_range(args.s1)
    sigma_pm_range = extract_range(args.sigma_pm)
    
    results = []
    for r1 in r1_range:
        for s1 in s1_range:
            for sigma_pm in sigma_pm_range:
                sigma = 0.001 * sigma_pm
                result = {
                    'r1':r1, 'r2':args.r2, 
                    's1':s1, 's2':args.s2, 's3':args.s3, 
                    'sigma':sigma, 'g':args.g, 't':args.t,
                    'p_tuple':args.p_tuple, 'p_block':args.p_block}
                result = result | simulate_tuple_join(
                    r1, args.r2, s1, args.s2, args.s3, 
                    args.g, args.p_tuple)
                result = result | simulate_block_join(
                    r1, args.r2, s1, args.s2, args.s3, 
                    sigma, 'precise', 
                    args.g, args.p_block, args.t)
                result = result | simulate_block_join(
                    r1, args.r2, s1, args.s2, args.s3, 
                    1, 'conservative', 
                    args.g, args.p_block, args.t)
                results += [result]
    
    df = pandas.DataFrame(results)
    df.to_csv(args.out_file, index=False)