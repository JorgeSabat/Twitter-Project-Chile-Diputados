def get_partition_count(line_count, partition_size):
    partition_count = line_count // partition_size
    has_remainder = line_count % partition_size
    if has_remainder:
        partition_count += 1
    return partition_count


def create_files(base_filename, partition_size):
    id_ranges = [
        (31013, 37015),
        (31498, 31802),
        (32387, 32649),
    ]

    lines = []
    for id_range in id_ranges:
        range_start = id_range[0]
        range_end = id_range[1]
        for id in range(range_start, range_end + 1):
            line = f'{id}\n'
            lines.append(line)

    
    partition_count = get_partition_count(len(lines), partition_size)
    for i in range(partition_count):
        filename = f'{base_filename}{i + 1}.txt'
        with open(filename, 'w') as file:
            range_start = i * partition_size
            range_end = range_start + partition_size 
            file.writelines(lines[range_start: range_end])
   

if __name__ == '__main__':
    BASE_FILENAME = 'input'
    PARTITION_SIZE = 1000
    create_files(BASE_FILENAME, PARTITION_SIZE)
