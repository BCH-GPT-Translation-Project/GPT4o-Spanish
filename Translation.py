import os
import re
import datetime
import json
import win32com.client
from docx import Document
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from openai import AzureOpenAI

# Azure OpenAI settings
api_key = os.environ.get("AZURE_OPENAI_API_KEY")
azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

# Initialize the AzureOpenAI client
client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-05-13",
    azure_endpoint=azure_endpoint
)

def list_files_starting_with_number(directory):
    # List all files and directories in the given directory
    all_files = os.listdir(directory)
    
    # Filter the list to include only those that start with a number
    files_starting_with_number = [f for f in all_files if re.match(r'^\d', f)]
    
    return files_starting_with_number

def find_folders_ending_with(filenames, search_directory):
    # List all directories in the search directory
    all_dirs = [d for d in os.listdir(search_directory) if os.path.isdir(os.path.join(search_directory, d))]
    
    # Filter the list to include only those that end with one of the filenames
    matching_dirs = [d for d in all_dirs if any(d.endswith(filename) for filename in filenames)]
    
    return matching_dirs

def collect_source_files_in_subfolder(directory):
    files = []
    if os.path.exists(directory) and os.path.isdir(directory):
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.lower().startswith("source"):
                    files.append(os.path.join(root, filename))
    return files

def read_docx(file_path):
    # Read a .docx file and return its text content.
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def read_doc(file_path):
    # Read a .doc file and return its text content using pywin32.
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    doc = word.Documents.Open(file_path)
    content = doc.Content.Text
    doc.Close()
    word.Quit()
    return content

def read_txt(file_path):
    # Read a .txt file and return its text content.
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_translation(source_file, translation):
    # Write content to results.txt in the same directory as source_file.
    print("\n" + "="*80 + "\n")
    print(f"Translation of {source_file}\nEndpoint: {translation.object}\nModel: {translation.model}\nFingerprint: {translation.system_fingerprint}\nTokens: Prompt {translation.usage.prompt_tokens}; Completion {translation.usage.completion_tokens}; Total {translation.usage.total_tokens}\nTime: {translation.created}\nFinish reason: {translation.choices[0].finish_reason}\n\n{translation.choices[0].message.content}")

    # Write the translation
    translation_path = os.path.join(os.path.dirname(source_file), f"gpt_translation-{translation.created}.txt")
    with open(translation_path, 'a', encoding='utf-8') as translation_file:
        translation_file.write(translation.choices[0].message.content)

    # Log the entire output of the GPT Chat Completion object
    log_path = os.path.join(os.path.dirname(source_file), f"gpt_translation-{translation.created}.log")
    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"Translation of {source_file}\n")
        log_file.write(f"Endpoint: {translation.object}\n")
        log_file.write(f"Model: {translation.model}\n")
        log_file.write(f"Fingerprint: {translation.system_fingerprint}\n")
        log_file.write(f"Tokens: Prompt {translation.usage.prompt_tokens}; Completion {translation.usage.completion_tokens}; Total {translation.usage.total_tokens}\n")
        log_file.write(f"Time: {translation.created}\n")
        log_file.write(f"Finish reason: {translation.choices[0].finish_reason}\n\n")

        # Write the whole Chat Completion object in readable JSON format
        log_file.write(f"Translation object: {json.dumps(translation.to_dict(), indent=4)}")

def translate(text):
    delimeter = '"""'
    system_message = f"""
    You are a skilled translator with expertise in medical terminology and patient care at Boston Children's Hospital in Boston, MA. Your task is to translate medical documents from English to Spanish. These documents include crucial details about diagnoses, treatment options, medication guidelines, preventative health tips, and general medical information, targeting patients and their families with varying levels of medical knowledge. Aim for translations that are precise, culturally attuned, and simple, steering clear of complex medical jargon and acronyms that could confuse non-expert readers.
    Follow these rules:
    1. Determine the core message of the original text and the most effective way to convey it in the target language.
    2. Take into account cultural differences and varying health literacy levels to make your translation as accessible as possible.
    3. Ensure the content is understandable to a person with a sixth-grade level of education. 
    4. Use the formal register.
    5. Expand unambiguous acronyms (e.g., "ABA" = "Applied Behavior Analysis", "IEP" = "Individualized Education Program", "OB" = "Obstetrician", "GJT" = "gastrojejunostomy tube") and translate them.
    6. Do not translate or edit proper nouns. 
    7. Translate medication names. If translated medication names are not exactly the same as how they appear in the source text, include the source/English name of the medication in parentheses (e.g., "hydrocortisone" should be translated as "hidrocortisona (hydrocortisone)").
    8. Ensure consistent use of gender-specific language (nouns, adjectives) when mentioning the patient. 
    9. Take target language conventions into account.
    Your objective is to render the medical content thoroughly comprehensible, enabling patients and their families to be well-informed about their health. Please translate the text below the triple quotes ({delimeter}):
    {delimeter}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": text}
            ],
            max_tokens=2000
        )
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    # Get the current working directory
    current_directory = os.getcwd()

    # Get the list of translation IDs that start with a number in the current directory
    translation_directories = list_files_starting_with_number(current_directory)

    source_files = []
    for directory in translation_directories:
        source_files_in_directory = collect_source_files_in_subfolder(directory)
        source_files.extend(source_files_in_directory)

    print("\n" + "="*160 + "\n" + "="*160 + "\n")

    # Read and print the contents of each file
    for index, file in enumerate(source_files, start=1):
        # Print the progress and timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"{timestamp}: {index} of {len(source_files)}")
        
        try:
            if file.endswith('.docx'):
                content = read_docx(file)
            elif file.endswith('.doc'):
                content = read_doc(file)
            elif file.endswith('.txt'):
                content = read_txt(file)
            else:
                continue

            translation = translate(content)
            write_translation(file, translation)
        except Exception as e:
            print("\n" + "*"*160 + "\n")
            print(f"Could not read file {file} due to {e}")
            print("\n" + "*"*160 + "\n")

if __name__ == "__main__":
    main()
