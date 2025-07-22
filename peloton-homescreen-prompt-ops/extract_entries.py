#!/usr/bin/env python3
import json
import os
import sys
import argparse

def extract_entries(input_path, num_entries):
    """
    Extract the first n entries from a JSON file and write them to a new file.

    Args:
        input_path (str): Path to the input JSON file
        num_entries (int): Number of entries to extract

    Returns:
        str: Path to the output file
    """
    # Parse the input path to get the directory, filename, and extension
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)

    # Split the filename to get the name without extension
    name_parts = os.path.splitext(filename)
    base_name = name_parts[0]
    extension = name_parts[1]

    # Create the output filename
    output_filename = f"{base_name}_{num_entries}{extension}"
    output_path = os.path.join(directory, output_filename)

    try:
        # Read the input JSON file
        with open(input_path, 'r') as f:
            data = json.load(f)

        # Check if the data is a list
        if not isinstance(data, list):
            print(f"Error: The JSON file does not contain a list of entries.")
            return None

        # Check if there are enough entries
        if len(data) < num_entries:
            print(f"Warning: The JSON file only contains {len(data)} entries, but {num_entries} were requested.")
            num_entries = len(data)

        # Extract the first n entries
        extracted_data = data[:num_entries]

        # Write the extracted entries to the output file
        with open(output_path, 'w') as f:
            json.dump(extracted_data, f, indent=2)

        print(f"Successfully extracted {num_entries} entries to {output_path}")
        return output_path

    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {input_path} is not a valid JSON file.")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        return None

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract entries from a JSON file.')
    parser.add_argument('input_path', help='Path to the input JSON file')
    parser.add_argument('num_entries', type=int, help='Number of entries to extract')

    # Parse arguments
    args = parser.parse_args()

    # Extract entries
    extract_entries(args.input_path, args.num_entries)

if __name__ == '__main__':
    main()
