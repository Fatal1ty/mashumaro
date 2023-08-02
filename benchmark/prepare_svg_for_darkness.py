import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file name")
    parser.add_argument("output", help="output file name")
    args = parser.parse_args()

    if not args.input or not args.output:
        print("Please provide both input and output file names.")
        exit(1)

    # Replace all occurrences of "#333333" with "#C9D1D9" for dark theme
    with open(args.input) as infile, open(args.output, 'w') as outfile:
        for line in infile:
            outfile.write(line.replace('#333333', '#C9D1D9'))
