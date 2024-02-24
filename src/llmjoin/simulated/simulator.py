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


def simulate_block_join(
        r1, r2, s1, s2, s3, sigma, estimate, g, p, t, log_prefix):
    """ Simulate block-nested loops join.
    
    Args:
        r1: number of tuples in first table.
        r2: number of tuples in second table.
        s1: size of each tuple in first table.
        s2: size of each tuple in second table.
        s3: size of each output tuple.
        sigma: selectivity of join predicate.
        estimate: selectivity estimate used to calculate block sizes.
        g: relative cost of writing tuples.
        p: size of static part of prompt.
        t: maximal number of tuples processed per model invocation.
        log_prefix: prefix all logged attributes by this.
    
    Returns:
        A dictionary with simulation results.
    """
    estimate = max(estimate, 0.0000001)
    b1 = math.floor(
        (math.sqrt(s1*s1*s2*s2+s1*s2*s3*estimate*(t-p))-s1*s2)/
        (s1*s3*estimate))
    b2 = math.floor(((t-p)-b1*s1)/(s2+b1*s3*estimate))
    prompt_size = p+b1*s1+b2*s2
    output_size = b1*b2*sigma*s3
    
    # Check for prompt overflow
    total_tokens = prompt_size + output_size
    if total_tokens > t:
        total_read = prompt_size
        overflow_tokens = total_tokens - t
        total_written = output_size - overflow_tokens
        total_cost = total_read + total_written * g
        return {
            f'{log_prefix}_block_invocations':1, 
            f'{log_prefix}_block_cost':total_cost,
            f'{log_prefix}_block_read':total_read, 
            f'{log_prefix}_block_written':total_written,
            f'{log_prefix}_block_overflow':True}
    
    nr_invocations = math.ceil(r1/b1) * math.ceil(r2/b2)
    total_read = prompt_size * nr_invocations
    total_written = output_size * nr_invocations
    total_cost = total_read + total_written * g
    return {
        f'{log_prefix}_block_invocations':nr_invocations, 
        f'{log_prefix}_block_cost':total_cost,
        f'{log_prefix}_block_read':total_read, 
        f'{log_prefix}_block_written':total_written,
        f'{log_prefix}_block_overflow':False}


def simulate_adaptive_join(r1, r2, s1, s2, s3, sigma, estimate, g, p, t):
    """ Simulate adaptive join algorithm.
    
    Args:
        r1: number of rows in first table.
        r2: number of rows in second table.
        s1: size of tuples in first table.
        s2: size of tuples in second table.
        s3: size of output entries.
        sigma: actual selectivity of join predicate.
        estimate: initial estimate for join selectivity (may be too low).
        g: relative cost of written tokens.
        p: size of static part of prompt template.
        t: maximal number of tokens read and generated per LLM invocation.
    """
    nr_invocations = 0
    total_read = 0
    total_written = 0    
    total_cost = 0
    overflow = True
    
    while overflow:
        result = simulate_block_join(
            r1, r2, s1, s2, s3, sigma, 
            estimate, g, p, t, '')
        nr_invocations += result['_block_invocations']
        total_read += result['_block_read']
        total_written += result['_block_written']
        total_cost += result['_block_cost']
        overflow = result['_block_overflow']
        estimate *= 4
    
    return {
        f'adaptive_invocations':nr_invocations, 
        f'adaptive_cost':total_cost,
        f'adaptive_read':total_read, 
        f'adaptive_written':total_written}


def run_benchmark(
        r1, r2, s1, s2, s3, sigma_pm, 
        g, t, p_tuple, p_block, out_file):
    """ Runs benchmark and writes result to .csv file.
    
    Args:
        r1: range of sizes for first table (format: "start:end:step").
        r2: size of second table.
        s1: range of tuple sizes for first table.
        s2: size of tuple in second table.
        s3: size of join result tuple.
        sigma_pm: pro mille selectivity range.
        g: relative cost per output token.
        t: maximal number of tokens per LLM invocation.
        p_tuple: size of static prompt part for tuple join.
        p_block: size of static prompt part for block join.
        out_file: name of result output file. 
    """
    r1_range = extract_range(r1)
    s1_range = extract_range(s1)
    sigma_pm_range = extract_range(sigma_pm)
    
    results = []
    for r1 in r1_range:
        for s1 in s1_range:
            for sigma_pm in sigma_pm_range:
                sigma = 0.001 * sigma_pm
                result = {
                    'r1':r1, 'r2':r2, 
                    's1':s1, 's2':s2, 's3':s3, 
                    'sigma':sigma, 'g':g, 't':t,
                    'p_tuple':p_tuple, 'p_block':p_block}
                result = result | simulate_tuple_join(
                    r1, r2, s1, s2, s3, 
                    g, p_tuple)
                result = result | simulate_block_join(
                    r1, r2, s1, s2, s3, 
                    sigma, sigma, 
                    g, p_block, t, 'informed')
                result = result | simulate_block_join(
                    r1, r2, s1, s2, s3, 
                    sigma, 1, 
                    g, p_block, t, 'conservative')
                result = result | simulate_adaptive_join(
                    r1, r2, s1, s2, s3, 
                    sigma, sigma/100.0, 
                    g, p_block, t)
                
                results += [result]
    
    df = pandas.DataFrame(results)
    df.to_csv(out_file, index=False)


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
    
    run_benchmark(
        args.r1, args.r2, args.s1, args.s2, args.s3, 
        args.sigma_pm, args.g, args.t, 
        args.p_tuple, args.p_block, args.out_file)