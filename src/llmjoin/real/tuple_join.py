'''
Created on Feb 24, 2024

@author: immanueltrummer
'''
import argparse
import openai
import pandas


def create_prompt(tuple1, tuple2, predicate):
    """ Create prompt to compare two tuples.
    
    Args:
        tuple1: first tuple.
        tuple2: second tuple.
        predicate: compare using join predicate.
    
    Returns:
        Prompt for tuple comparison.
    """
    parts = []
    parts += ['Does the following condition hold for the two text snippets ("Yes"/"No")?']
    parts += [f'Condition: {predicate}']
    parts += [f'Snippet 1: {tuple1}']
    parts += [f'Snippet 2: {tuple2}']
    parts += ['Answer:']
    return '\n'.join(parts)


def tuple_join(df1, df2, predicate, model):
    """ Perform tuple join.
    
    Args:
        df1: first input table.
        df2: second input table.
        predicate: join predicate.
        model: name of OpenAI model.
    
    Returns:
        Tuple: statistics, join result.
    """
    results = []
    stats = []
    client = openai.OpenAI()
    for row1 in df1.rows():
        for row2 in df2.rows():
            tuple1 = row1['text']
            tuple2 = row2['text']
            prompt = create_prompt(tuple1, tuple2, predicate)
            messages = [{'role':'user', 'content':prompt}]
            response = client.chat.completions().create(
                messages=messages, model=model, max_tokens=1)
            
            answer = response['choices'][0]['content']
            if answer == 'Yes':
                results += [{'tuple1':tuple1, 'tuple2':tuple2}]
            
            tokens_read = response['usage']['prompt_tokens']
            tokens_written = response['usage']['completion_tokens']
            stats += [
                {'tokens_read':tokens_read, 
                 'tokens_written':tokens_written}]
    
    return pandas.DataFrame(stats), pandas.DataFrame(results)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('ai_key', type=str, help='Key for OpenAI access')
    parser.add_argument('model', type=str, help='Name of OpenAI model')
    parser.add_argument('input1', type=str, help='Path to .csv file')
    parser.add_argument('input2', type=str, help='Path to .csv file')
    parser.add_argument('predicate', type=str, help='Join predicate')
    parser.add_argument('stats_out', type=str, help='Path for statistics')
    parser.add_argument('result_out', type=str, help='Path for result')
    args = parser.parse_args()
    
    openai.api_key = args.ai_key
    df1 = pandas.read_csv(args.input1)
    df2 = pandas.read_csv(args.input2)
    
    statistics, result = tuple_join(df1, df2, args.predicate)
    statistics.to_csv(args.stats_out)
    result.to_csv(args.result_out)