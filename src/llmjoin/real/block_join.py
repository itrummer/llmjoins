'''
Created on Feb 24, 2024

@author: immanueltrummer
'''
import tiktoken
import time

from llmjoin.common.tuning import optimal_block_size


encoder = tiktoken.encoding_for_model('gpt-4')
#t = 4096
t = 2000


def token_size(text):
    """ Returns token size of text.
    
    Args:
        text: measure size of this text.
    
    Returns:
        Number of tokens used by GPT-4 tokenizer.
    """
    return len(encoder.encode(text))


def tuple_size(df):
    """ Calculates average token size of tuples.
    
    Args:
        df: calculate statistics for this data frame.
    
    Returns:
        Average tuple size in tokens.
    """
    return df.apply(lambda r:token_size(r['text']), axis=1).mean()


def create_prompt(block_1, block_2, predicate):
    """ Create prompt to join two blocks using given predicate.
    
    Args:
        block_1: block from first table.
        block_2: block from second table.
        predicate: join predicate as text.
    
    Returns:
        a prompt for joining two blocks.
    """
    parts = []
    parts += [
        ('Find indexes x,y where x is the number of an entry in collection 1 '
         f'and y the number of an entry in collection 2 such that {predicate} '
         '(make sure to catch all pairs!)!')]
    parts += ['Separate index pairs by semicolons.']
    parts += ['Write "Finished" after the last pair!']
    parts += ['Text Collection 1:']
    for idx, text in enumerate(block_1, 1):
        parts += [f'{idx}: {text}']
    parts += ['Text Collection 2:']
    for idx, text in enumerate(block_2, 1):
        parts += [f'{idx}: {text}']
    parts += ['Index pairs:']
    return '\n'.join(parts)


def partition(df, block_size):
    """ Partitions data into equal-sized blocks.
    
    Args:
        df: partition data in "text" column of this data frame.
        block_size: size of blocks (the last block may have fewer elements).
    
    Returns:
        list of blocks (each block is a list of strings).
    """
    data = list(df['text'])
    blocks = []
    for i in range(0, len(data), block_size):
        block = data[i:i+block_size]
        blocks.append(block)
    
    return blocks


def process_answer(answer, block_1, block_2):
    """ Extract join result from LLM answer.
    
    Args:
        answer: raw text answer generated by LLM.
        block_1: list containing text snippets.
        block_2: list containing text snippets.
    
    Returns:
        List of dictionaries representing join result tuples.
    """
    nr_tuples_1 = len(block_1)
    nr_tuples_2 = len(block_2)
    results = []
    for raw_result in answer.split(';'):
        raw_indexes = raw_result.split(',')
        if len(raw_indexes) == 2:
            raw_indexes = [i.strip() for i in raw_indexes]
            x_raw, y_raw = raw_indexes
            if x_raw.isdigit() and y_raw.isdigit():
                index_1 = int(x_raw) - 1
                index_2 = int(y_raw) - 1
                if index_1 >= 0 and index_1 < nr_tuples_1 \
                    and index_2 >= 0 and index_2 < nr_tuples_2:
                    tuple_1 = block_1[index_1]
                    tuple_2 = block_2[index_2]
                    result = {'tuple1':tuple_1, 'tuple2':tuple_2}
                    results.append(result)
    
    return results


def join_two_blocks(client, block_1, block_2, predicate, model):
    """ Joins two blocks using the given predicate.
    
    Args:
        client: OpenAI client.
        block_1: list of entries from first table.
        block_2: list of entries from second table.
        predicate: join predicate as text.
        model: name of OpenAI model to use.
    
    Returns:
        Statistics, join result.
    """
    start_s = time.time()
    prompt = create_prompt(block_1, block_2, predicate)
    print(f'---\n{prompt}\n---')
    messages = [{'role':'user', 'content':prompt}]
    max_tokens = t - token_size(prompt)
    
    if max_tokens >= 1:
        response = client.chat.completions.create(
            messages=messages, model=model, 
            max_tokens=max_tokens, temperature=0,
            stop=['Finished'])
        print(response)
        
        answer = response.choices[0].message.content
        print(f'Answer: {answer}')
        overflow = not (response.choices[0].finish_reason == 'stop')
        print(f'Overflow: {overflow}\n')
        tokens_read = response.usage.prompt_tokens
        tokens_written = response.usage.completion_tokens
        results = process_answer(answer, block_1, block_2)
    else:
        tokens_read = 0
        tokens_written = 0
        overflow = True
        results = []
    
    total_s = time.time() - start_s
    stats = {
        'tokens_read':tokens_read, 
        'tokens_written':tokens_written,
        'seconds':total_s,
        'overflow':overflow}

    return stats, results


def block_join(client, df1, df2, predicate, model, estimate=1):
    """ Performs block join between two tables.
    
    Args:
        client: OpenAI client.
        df1: first input table.
        df2: second input table.
        predicate: compare entries using this predicate.
        model: name of OpenAI model to use.
        estimate: estimate for join predicate selectivity.
    
    Returns:
        A tuple: (performance statistics, join result).
    """
    s1 = tuple_size(df1)
    s2 = tuple_size(df2)
    s3 = 4
    
    static_prompt = create_prompt([], [], predicate)
    p = token_size(static_prompt)
    
    print(p)
    print(t)
    b1, b2 = optimal_block_size(s1, s2, s3, t, p, estimate)
    blocks_1 = partition(df1, b1)
    blocks_2 = partition(df2, b2)
    nr_blocks_1 = len(blocks_1)
    nr_blocks_2 = len(blocks_2)
    
    stats = []
    results = []
    overflow = False
    for idx_1, block_1 in enumerate(blocks_1, 1):
        if overflow:
            break
        for idx_2, block_2 in enumerate(blocks_2, 1):
            print(
                f'Joining block {idx_1}/{nr_blocks_1} from table 1 '
                f'with block {idx_2}/{nr_blocks_2} from table 2 ...')
            stat, result = join_two_blocks(
                client, block_1, block_2, 
                predicate, model)
            overflow = stat['overflow']
            stats.append(stat)
            results += result
            if overflow:
                break
    
    return stats, results