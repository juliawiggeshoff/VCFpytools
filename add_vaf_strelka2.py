#!/usr/bin/python3

"""
Author: Julia Wiggeshoff
Email: juliawiggeshoff@gmail.com

This script parses a Strelka2 VCF file and calculates VAF for INDELs or SNVs.
"""

import argparse
import gzip
import os
from typing import IO

def calculate_vaf(ref_count: int, alt_count: int) -> float:
    """
    Calculate Variant Allele Frequency (VAF).

    :param ref_count: Count of reference alleles.
    :param alt_count: Count of alternate alleles.
    :return: Calculated VAF.
    """
    return alt_count / (ref_count + alt_count) if (ref_count + alt_count) > 0 else 0.0

def parse_vcf(file_path: str, variant_type: str) -> list[str]:
    """
    Parse a Strelka2 VCF file and calculate VAF for INDELs or SNVs.

    :param file_path: Path to the input VCF file.
    :param variant_type: Type of variant (snv or indel).
    :return: Modified VCF lines as a list of strings.
    """
    header_lines = []
    main_header_line = []
    variant_lines = []
    first_filter = 0
    
    # used just for snv
    allele_map = {'A': 0, 'C': 1, 'G': 2, 'T': 3}

    if file_path.endswith(".gz"):
        open_func = gzip.open
        mode = 'rb'
    else:
        open_func = open
        mode = 'rt'

    with open_func(os.path.abspath(file_path), mode) as f:
        for line in f:
            if file_path.endswith(".gz"):
                line = line.decode('utf-8').rstrip()
            else:
                line = line.rstrip()

            if line.startswith("##"):
                if line.startswith("##FILTER") and first_filter == 0:
                    header_lines.append("##FORMAT=<ID=VAF,Number=A,Type=Float,Description=\"The fraction of reads with alternate allele (nALT/nSumAll)\">")
                    first_filter = 1
                    header_lines.append(line)
                else:
                    header_lines.append(line)
            elif line.startswith("#"):
                main_header_line.append(line)
            else:
                columns = line.split('\t')

                if variant_type.lower() == "snv":
                    ref = columns[3]
                    alt = columns[4]

                    normal_counts = columns[9].split(":")[4:]
                    tumor_counts = columns[10].split(":")[4:]

                    refcount_normal = int(normal_counts[allele_map[ref]].split(',')[0])
                    altcount_normal = int(normal_counts[allele_map[alt]].split(',')[0])

                    refcount_tumor = int(tumor_counts[allele_map[ref]].split(',')[0])
                    altcount_tumor = int(tumor_counts[allele_map[alt]].split(',')[0])

                elif variant_type.lower() == "indel":
                    normal_counts = columns[9].split(":")[2:4]
                    tumor_counts = columns[10].split(":")[2:4]

                    refcount_normal = int(normal_counts[0].split(',')[0])
                    altcount_normal = int(normal_counts[1].split(',')[0])

                    refcount_tumor = int(tumor_counts[0].split(',')[0])
                    altcount_tumor = int(tumor_counts[1].split(',')[0])

                vaf_normal = calculate_vaf(refcount_normal, altcount_normal)
                vaf_tumor = calculate_vaf(refcount_tumor, altcount_tumor)

                columns[8] += ":VAF"
                columns[9] += f":{vaf_normal:.4f}"
                columns[10] += f":{vaf_tumor:.4f}"

                variant_lines.append("\t".join(columns))

    mod_vcf = header_lines + main_header_line + variant_lines
    return mod_vcf

def write_vcf(lines_ls: list[str], output_path: str) -> IO:
    """
    Write modified VCF lines to an output file.

    :param lines_ls: List of VCF lines as strings.
    :param output_path: Path to the output VCF file.
    """
    with open(output_path, 'w') as file:
        for line in lines_ls:
            file.write(line + '\n')

def main():
    parser = argparse.ArgumentParser(description="Parse a Strelka2 VCF file and calculate VAF for INDELs or SNVs")
    parser.add_argument("--input", help="Path to the Strelka2 VCF file", required=True)
    parser.add_argument("--output", help="Path to the modified output VCF file", required=True)
    parser.add_argument("--variant", help="Type of variant (snv or indel)", choices=["snv", "indel"], required=True)
    args = parser.parse_args()

    parsed_vcf = parse_vcf(args.input, args.variant)
    write_vcf(parsed_vcf, args.output)

if __name__ == "__main__":
    main()
