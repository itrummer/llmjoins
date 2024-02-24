'''
Created on Feb 24, 2024

@author: immanueltrummer
'''
from llmjoin.simulated.simulator import run_benchmark


if __name__ == '__main__':
    
    run_benchmark(
        '500:10500:500', 5000, '30:31:1', 30, 
        2, '1:2:1', 2, 8192 , 50, 50, 'scale_table_1.csv')
    run_benchmark(
        '5000:5001:1', 5000, '50:1050:50', 30, 
        2, '1:2:1', 2, 8192 , 50, 50, 'scale_tuple_1.csv')
    run_benchmark(
        '5000:5001:1', 5000, '30:31:1', 30, 
        2, '0:1001:50', 2, 8192 , 50, 50, 'scale_output_1.csv')