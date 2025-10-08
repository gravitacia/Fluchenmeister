from components.token import get_valid_token_results  # or whatever the function name is
results = get_valid_token_results()  # call the function to get the data

for token in results:
    print(token)