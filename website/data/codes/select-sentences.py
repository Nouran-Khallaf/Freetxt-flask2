def filter_sentences(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            words = line.strip().split()  # split the sentence into words
            if 20 <= len(words) <= 50 and line.strip().endswith('.'):  
                # write to the output file if sentence length is between 10 and 50 words and ends with '.'
                f_out.write(line)

# usage
filter_sentences('/Users/katiana/Documents/Thesawrws-welsh/website/data/corcencc_clean_sentences.txt', '/Users/katiana/Documents/Thesawrws-welsh/website/data/filtered_sentences.txt')
