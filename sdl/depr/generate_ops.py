# TODO: Some better way to generate operation_pool
with open('simple_operation_names.txt', 'w') as f:
    for i in range(1, 101):
        f.write(f'OP_{i}\n')
