# VCFpytools
Assortment of VCF processing scripts 

# Requirements

- Ensure you have Python3 installed on your system
- Clone or download the script from this repository

  `git clone https://github.com/juliawiggeshoff/VCFpytools.git`

# Merge VCF Headers

This [script](https://github.com/juliawiggeshoff/VCFpytools/blob/main/merge_vcf_headers.py) allows you to merge headers from multiple VCF (Variant Call Format) files into a single output header file. It's useful when you have VCF files with similar headers and you want to consolidate them. This can then be used after or before running `bcftools concat --naive[-force]`, where `--naive-force` ignores the differences in headers, for example, to modify the concatenated VCF files with all header information from both files, if you opt to include the merged headers only after concatenating your VCF files with bcftools (other concatenation tools).

Input can be gzipped or not. Output filename is optional, but recommended. If not given, will create `merged_headers.txt` in the working directory. 

`python merge_vcf_headers.py -vcfs file1.vcf.gz file2.vcf.gz [...] -o output_merged_header.txt`

Optionally, you can include headers other than the mandatory ##fileformat, ##contig, ##FILTER, ##INFO, and ##FORMAT. These are usually commands used to process the VCF files (e.g. bcftools, vcflib, etc), dates of file creation, version of tool, etc.

`python merge_vcf_headers.py -vcfs file1.vcf.gz file2.vcf.gz -o output_merged_header.txt -fullheader`

### Example usage with bcftools concat

- Re-head VCF files before concatenation:
```
python merge_vcf_headers.py -vcfs file1.vcf.gz file2.vcf.gz -o output_merged_header.txt
(cat output_merged_header.txt; zcat file1.vcf.gz | grep -v '##') | bgzip -f -c > reheaded_file1.vcf.gz
(cat output_merged_header.txt; zcat file2.vcf.gz | grep -v '##') | bgzip -f -c > reheaded_file2.vcf.gz
tabix -f -p vcf file1.vcf.gz 
tabix -f -p vcf file2.vcf.gz 
bcftools concat --naive file1.vcf.gz file2.vcf.gz  > reheaded_concatenated.bcf
```

- Re-head VCF file after concatenation
```
bcftools concat --naive-force file1.vcf.gz  file2.vcf.gz > concatenated.bcf
bcftools view concatenated.bcf -Oz -o concatenated.vcf.gz
python merge_vcf_headers.py -vcfs file1.vcf.gz file2.vcf.gz -o output_merged_header.txt -fullheader
(cat output_merged_header.txt; zcat concatenated.vcf.gz | grep -v "##") | bgzip -f -c > reheaded_concatenated.vcf.gz
tabix -f -p vcf reheaded_concatenated.vcf.gz
```

# Parse and Calculate VAF from Strelka2 somatic VCF files

This [script](https://github.com/juliawiggeshoff/VCFpytools/blob/main/add_vaf_strelka2.py) parses Strelka2 Variant Call Format (VCF) files and calculates Variant Allele Frequency (VAF) for INDELs or SNVs. It follows the recommendations from the [developers](https://github.com/Illumina/strelka/blob/v2.9.x/docs/userGuide/README.md#somatic-variant-allele-frequencies).

Input can be gzipped or not. Output will be a VCF (not gzipped) and setting the filename is mandatory, as well as setting the type of variant based on the somatic output files from Strelka2. Information found [here](https://github.com/Illumina/strelka/blob/v2.9.x/docs/userGuide/README.md#somatic)
```
python add_vaf_strelka2.py --input somatic.snvs.vcf.gz --output somatic.snvs.VAF.vcf --variant snv
python add_vaf_strelka2.py --input somatic.indels.vcf.gz --output somatic.indels.VAF.vcf --variant indel
```



