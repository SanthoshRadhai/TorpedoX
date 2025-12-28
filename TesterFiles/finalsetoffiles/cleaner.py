def convert_text_to_lowercase_and_remove_spaces(input_file, output_file):
    """
    This function reads text from an input file, converts it to lowercase,
    removes all whitespace characters (spaces, tabs, newlines), and writes
    the processed text to an output file.

    Args:
    - input_file (str): Path to the input text file.
    - output_file (str): Path to save the processed text.

    Returns:
    None
    """
    try:
        # Open the input file and read its content
        with open(input_file, 'r') as infile:
            text = infile.read()

        # Convert text to lowercase and remove all whitespace
        processed_text = ''.join(text.lower().split())

        # Write the processed text to the output file
        with open(output_file, 'w') as outfile:
            outfile.write(processed_text)

        print(f"Processed text has been saved to '{output_file}'.")
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    input_file = 'FC1.txt'  # Replace with the path to your input file
    output_file = 'FC1_Cleaned.txt'  # Replace with the desired output file name

    convert_text_to_lowercase_and_remove_spaces(input_file, output_file)
