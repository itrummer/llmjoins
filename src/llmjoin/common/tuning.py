'''
Created on Feb 26, 2024

@author: immanueltrummer
'''
import math


def optimal_block_size(s1, s2, s3, t, p, estimate):
    """ Calculates optimal block sizes for block join.
    
    Args:
        s1: size of tuples in first table.
        s2: size of tuples in second table.
        s3: size of join result tuples.
        t: threshold on number of tokens per LLM invocation.
        p: size of static prompt parts.
        estimate: estimate for join predicate selectivity.
    
    Returns:
        (optimal block size for first table, optimal size for second table) 
    """
    estimate = max(estimate, 0.0000001)
    b1 = math.floor(
        (math.sqrt(s1*s1*s2*s2+s1*s2*s3*estimate*(t-p))-s1*s2)/
        (s1*s3*estimate))
    b2 = math.floor(((t-p)-b1*s1)/(s2+b1*s3*estimate))
    return b1, b2