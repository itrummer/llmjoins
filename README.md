# Theta-Joins with Language Models

This repository implements joins with predicates described as free text (e.g., ``ads matching searches'' or ``statements contradicting each other''). The implementation uses large language models such as GPT-4 to determine matches between text inputs. The repository features a simulator, comparing simulated processing fees for different join operators and scenarios, and implementations of real join operators. 

## Simulation

The simulator is located in the `src/llmjoin/simulated` package. Run the simulator in all standard scenarios with the following command:
```
python src/llmjoin/simulated/run_simulator.py
```
The simulator generates three .csv files containing benchmark results.

## Real Joins

The implementations of the actual join operators are located in the `src/llmjoin/real` package. To generate benchmark data for the joins, execute the following command (make sure that all relevant source data files can be found in the `data` sub-directory):
```
python src/llmjoin/real/generate.py
```
After generating benchmark data, create the `testresults` sub-directory and run benchmarks with all join operators using the following command (replace `[OpenAI Key]` with your OpenAI key):
```
python src/llmjoin/real/run_real [OpenAI Key]
```
Results will be stored in the `testresults` sub-directory after the benchmark completes.
