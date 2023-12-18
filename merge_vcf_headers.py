#!/usr/bin/python3

"""
Author: Julia Wiggeshoff
Email: juliawiggeshoff@gmail.com

This script merges the headers of multiple VCF files.
"""

import argparse
import gzip
from typing import IO

def parse_vcf_header(file_path: str) -> list[str]:
    """
    Parse the header of a VCF file and return a list of header lines.

    :param file_path: Path to the VCF file.
    :return: List of header lines.
    """
    header = []
    if file_path.endswith(".gz"):
        with gzip.open(file_path, 'rb') as vcf_file:
            for line_bytes in vcf_file:
                line = line_bytes.decode('utf-8')
                if line.startswith("##"):
                    header.append(line.strip())
                else:
                    break
    else:
        with open(file_path, 'r') as vcf_file:
            for line in vcf_file:
                line = line.rstrip()
                if line.startswith("##"):
                    header.append(line.strip())
                else:
                    break
    return header

def merge_vcf_headers(vcf_files: list[str], output_file: str, include_others = None) -> IO:
    """
    Merge headers of multiple VCF files and write to an output file.

    :param vcf_files: List of paths to the VCF files.
    :param output_file: Path to the output merged header file.
    :param include_others: Include other headers (commands and extra info) in the merged output.
    """
    merged_header = []
    fileformat_line_added = False
    header_collections = {
        "##contig=": [],
        "##FILTER=": [],
        "##INFO=": [],
        "##FORMAT=": [],
    }
    other_headers = []

    for vcf_file_path in vcf_files:
        header = parse_vcf_header(vcf_file_path)

        # Collect header lines by type
        for line in header:
            if line.startswith("##fileformat="):
                if not fileformat_line_added:
                    merged_header.append(line)
                    fileformat_line_added = True
            elif line.startswith("##contig="):
                if line not in header_collections["##contig="]:
                    header_collections["##contig="].append(line)
            elif line.startswith("##FILTER="):
                if line not in header_collections["##FILTER="]:
                    header_collections["##FILTER="].append(line)
            elif line.startswith("##INFO="):
                if line not in header_collections["##INFO="]:
                    header_collections["##INFO="].append(line)
            elif line.startswith("##FORMAT="):
                if line not in header_collections["##FORMAT="]:
                    header_collections["##FORMAT="].append(line)
            else:
                other_headers.append(line)

    # Add the collected headers in the specified order
    for key in header_collections.keys():
        merged_header.extend(header_collections[key])

    # Add other headers that start with ##
    if include_others is True:
        merged_header.extend(other_headers)

    # Write the merged header to the output file
    with open(output_file, 'w') as output:
        for line in merged_header:
            output.write(line + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge headers of multiple VCF files")
    parser.add_argument("-vcfs", nargs="+", help="Paths to the VCF files", required=True)
    parser.add_argument("-o", "--output", help="Path to the output merged VCF header file (including directory and filename)")
    parser.add_argument("-fullheader", action="store_true", help="Include other headers (commands and extra info) in the merged output")

    args = parser.parse_args()

    output_file = args.output if args.output else "merged_headers.txt"

    if args.fullheader:        
        merge_vcf_headers(args.vcfs, output_file, True)
    else:
        merge_vcf_headers(args.vcfs, output_file)
