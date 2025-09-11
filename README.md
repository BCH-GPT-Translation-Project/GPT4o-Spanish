# GPT4o-Spanish

_Evaluating a Large Language Model in Translating Patient Instructions to Spanish Using a Standardized Framework_
[doi:10.1001/jamapediatrics.2025.1729](http://doi.org/10.1001/jamapediatrics.2025.1729)

Authors:  
Mondira Ray, MD, MBI*; Daniel J. Kats, MD, MBI*; Joss Moorkens, PhD; Dinesh Rai, MD; Nate Shaar; Diane Quinones, MS, RN, CPNP; Alejandro Vermeulen, BFA, CMI; Camila M. Mateo, MD, MPH; Ryan C. L. Brewster, MD; Alisa Khan, MD, MPH; Benjamin Rader, PhD; John S. Brownstein, PhD; Jonathan D. Hron, MD  
*Contributed equally as first-authors

Corresponding authors:  
Mondira Ray, MD: mondira.ray@childrens.harvard.edu  
Daniel J. Kats, MD: daniel.kats@childrens.harvard.edu


## Prerequisites
### Python
* Python 3.11.5
* Python package versions are listed in [requirements.txt](requirements.txt)
* Store OpenAI API Key as environmental variable `AZURE_OPENAI_API_KEY`
* Store OpenAI API endpoint as environmental variable `AZURE_OPENAI_ENDPOINT`

### R
R package versions are as follows: 
- R 4.3.1
- RStudio 2023.06.0+421
- dplyr 1.1.3
- fmsb 0.7.6
- ggplot2 3.5.1
- lme4 1.1-35.5
- MASS 7.3-60
- Matrix 1.6-5
- psych 2.4.6.26
- readxl 1.4.3
- tidyr 1.3.1

## Technical Implementation
### [Translation.py](Translation.py)
1. Place all source texts within the active directory (ok to place in nested folders, as long as the parent directory is within the active directory)
    1. English source text files should be `.txt`, `.doc`, or `.docx`
1. Run the script to generate GPT-4o translations of the source texts
    1. Translations will be stored in the same directory/ies as the source texts
1. Create a `Translation Units.xlsx` document in the active directory with the following format:

    | LL ID | Target Language | Word Count | Whole or Partial | HT | GPT | GPT Date | HT EWC | GPT EWC |
    | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
    | *Translation ID* | *Target Language* | *Source Document Word Count* | *Whole or Partial* | *Human Translation ID* | *GPT Translation ID* | *GPT Date* | *Human Translation Word Count* | *GPT Translation Word Count* |
    | translation001 | Spanish | 343 | Whole | T1 | T2 | 20240802 | 365 | 348 |
    | translation002 | Spanish | 366 | Partial | T2 | T1 | 20240802 | 389 | 376 |
    | translation003 | Spanish | 752 | Whole | T1 | T2 | 20240802 | 781 | 749 |
  
### MQM Evaluations
* Perform MQM evaluations and fill out a scorecard (provided in the publication's Supplementary Materials) for each evaluated translation
* Create separate directories within the active directory for each linguist's evaluations
    * Name the directories with evaluations beginning with "Linguist" (e.g., "Linguist 1_DK")
* Create a `preferences.xlsx` document in the active directory with the following format:

    | linguist | unit | Strongly Prefer Translation 1 | Prefer Translation 1 | No preference | Prefer Translation 2 | Strongly Prefer Translation 2 | why |
    | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
    | *Linguist ID* | *Translation ID* | | *Mark response* | | | | *Optional explanation* |
    | Linguist 1_DK | translation001 | | x | | | | Fewer errors |
    | Linguist 1_DK | translation002 | | | | x | | More conversational style |
    | Linguist 2_MR | translation001 | x | | | | | |

* Store the scorecards (as `.xlsx` files) within each linguist's directory
    * Can be nested within folders or flat

### [Analysis.Rmd](Analysis.Rmd)
1. Set MQM parameters as desired in lines 90, 92, 94, 98, 101
1. Script should run if correct libraries are installed and file structure is as specified above
1. Output: data via `translation_scores.csv` and several `png` images of figures

## License
This repository is licensed under [CC BY-NC 4.0](./LICENSE.md). Please cite the article (doi:10.1001/jamapediatrics.2025.1729) if you use this work.
