import os
from pathlib import Path # Convert from docx to strings
import fitz # Import for pdf 
from docx import Document # To convert docx files
import pandas
import re

base_dir=os.getcwd()
if os.name == 'nt':
    path_break='\\'
else:
    path_break='/'

from .statics_deident import *
#from For_GUI_deidentification.statics_deident import *
#from statics_deident import *

### DEFINITIONS FOR CURRENT PY FILE ###
def save_dicts_to_file(array_of_dicts, file_path): 
    new_dataframe=pandas.DataFrame.from_dict(array_of_dicts)
    if os.path.exists(file_path)==True:
        os.remove(file_path)
    new_dataframe.to_excel(file_path)

def remove_docx_trash(string): # Remove trash from docx download method
    docx_trash=["Reply Reply to Comment", "Manage Discussion Entry"]
    for trash_phrase in docx_trash:
        if trash_phrase in string:
            string=string.replace(trash_phrase, "")
    return string

def remove_dash_equal(string): # Remove starting dash or equal sign
    if string[:1]=="-" or string[:1]=="=" or string[:1]=="~":
        new_string=string[1:len(string)]
    else: 
        new_string=string
    return new_string

def detect_trash_date(string): # Detect trash date
    months=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years=["2021", "2022", "2023"]
    for month in months:
        for year in years:
            if month in string and year in string:
                string=""
                break
    return string 

def remove_excess_line_breaks_and_trash(text):
    clean_text=[]
    try:
        for entry in text:
            entry.strip()
            no_break_entry=entry.replace('\n', '')
            remove_extra_space=no_break_entry.replace('.  ', '. ')
            no_date=detect_trash_date(remove_extra_space)
            clean_entry=remove_docx_trash(no_date)
            if len(clean_entry)>0:
                clean_text.append(clean_entry)
    # Catches text=nan
    except TypeError:
        # Converts nan to empty string
        clean_text=''
    return clean_text

def space_after_special_endings(text):
    # Ensure there are spaces after special endings
    special_endings=["?", "!", "]", ",", ")", ":"]
    special_endings_with_space=["? ", "! ", "] ", ", ", ") ", ": "]
    revised_text=[]
    for string in text:
        special_endings_index=0
        while special_endings_index<6:
            if special_endings[special_endings_index] in string and special_endings_with_space[special_endings_index] not in string:
                string.replace(special_endings[special_endings_index], special_endings_with_space[special_endings_index])
            special_endings_index+=1
        revised_text.append(string)
    return revised_text

def remove_special_periods(sentence):
    # Before sentence split by period, remove special uses of period that do not indicate end of sentence. 
    for special_period_case_pair in special_period_set:
        sentence = sentence.replace(str(special_period_case_pair[0]), str(special_period_case_pair[1]))
    # Before spliting by period, protect numbers with decimal expansions and remove emails/urls.
    check_for_numbers_separated=sentence.split()
    removing_decimals=""
    for string in check_for_numbers_separated:
        if '@' in string:
            string='[email]'
        elif '.edu' in string:
            string='[url]'
        elif '.com' in string:
            string='[url]'
        elif '.net' in string: 
            string='[url]'
        elif '.org' in string:
            string='[url]'
        elif '.jpg' in string: 
            string='[image]'
        elif '.png' in string: 
            string='[image]'
        # First checkes that there are numbers to both sides. Otherwise makes a space between the period so the split works.
        elif any(char.isdigit() for char in string):
            check_if_error=string.split('.')
            if len(check_if_error)>1:
                # Second entry is empty if a number is the end of a sentence, like "Module 2." We want to treat these as ends of sentences and leave the period.
                if len(check_if_error[1])==0:
                    string=f"{check_if_error[0]}."
                # Else if there are numbers on either side of the period, we replace the period with DECIMALPOINT.
                elif all(any(char.isdigit() for char in small_string) for small_string in check_if_error):
                    string=string.replace('.', 'DECIMALPOINT')
                # Otherwise this is a number in the sentence that doesn't need to be modified.
                else:
                    fixed_no_space=""
                    for piece in check_if_error:
                        fixed_no_space+=f'{piece} '
                    string=fixed_no_space
        removing_decimals+=f'{string} '
    return removing_decimals 

def split_by_period(removing_decimals):
    # Split by period
    period_parsed=removing_decimals.split('.')
    # Add decimals back after spliting out periods.
    adding_back_decimals=[]
    for string in period_parsed:
        if any(char.isdigit() for char in string):
            string=string.replace('DECIMALPOINT', '.')
        adding_back_decimals.append(string)
    return adding_back_decimals

def replace_utfs(stripped_entry):
    # Uncomment when trying to determine special characters to decode
    ###
    #encoding=stripped_entry.encode("utf-8")
    #print(encoding)
    ###
    stripped_entry=stripped_entry.replace(b'\xce\xbc'.decode('utf-8'), 'mu')
    stripped_entry=stripped_entry.replace(b'\xe2\x80\x9c'.decode('utf-8'), '\"')
    stripped_entry=stripped_entry.replace(b'\xe2\x80\x9d'.decode('utf-8'), '\"')
    stripped_entry=stripped_entry.replace(b'\xe2\x88\x92'.decode('utf-8'), '-')
    stripped_entry=stripped_entry.replace(b'\xe2\x80\x93'.decode('utf-8'), '--')
    stripped_entry=stripped_entry.replace(b'\xe2\x80\x94'.decode('utf-8'), '---')
    stripped_entry=stripped_entry.replace(b'\xe2\x80\x98'.decode('utf-8'), '\'')
    stripped_entry=stripped_entry.replace(b'\xe2\x80\x99'.decode('utf-8'), '\'')
    stripped_entry=stripped_entry.replace(b'\xe2\x96\xb3'.decode('utf-8'), ' [delta] ')
    stripped_entry=stripped_entry.replace(b'\xce\x94'.decode('utf-8'), ' [delta] ')
    stripped_entry=stripped_entry.replace(b'\xe2\x89\x88'.decode('utf-8'), ' [approximately] ')
    stripped_entry=stripped_entry.replace(b'\xe2\x80\xa6'.decode('utf-8'), '')
    stripped_entry=stripped_entry.replace(b'\xc3\x97'.decode('utf-8'), ' x ')
    stripped_entry=stripped_entry.replace(b'\xc2\xb2'.decode('utf-8'), '^2')
    
    return stripped_entry

def deidentify_names(stripped_entry, deidentify_student_names, deidentify_instructor_names):
    for student_name in deidentify_student_names:
        stripped_entry = stripped_entry.replace(str(student_name), "[name]")
    for instructor_name in deidentify_instructor_names:
        stripped_entry = stripped_entry.replace(str(instructor_name[0]), "[instructor]")
    stripped_entry = stripped_entry.replace("[name] [name]", "[name]") # Since replacing by first name and last name separately, a student/instructor who signs off with their full name will look like [name] [name]
    return stripped_entry

def strip_by_special_character(special_character, array_of_text): 
    revised_text=[]
    for semi_cleaned_sentence in array_of_text:
        semi_parsed = semi_cleaned_sentence.split(special_character)
        for sentence in semi_parsed:
            revised_sentence=""
            stripped_sentence=sentence.strip()
            if len(stripped_sentence)>0:
                if stripped_sentence[-1] not in ["?", ".", "]", ",", ")", ":"]:
                    # Add ! back to end of sentence
                    stripped_sentence+=special_character
                revised_sentence+=f"{stripped_sentence} "
            revised_text.append(revised_sentence)
    return revised_text

#def clean_array_of_sentences(full_text, encode_relations_dict): 
def clean_array_of_sentences(full_text, deidentify_student_names, deidentify_instructor_names): 
#    deidentify_student_names=encode_relations_dict['Unitized Student Names']
#    deidentify_instructor_names=encode_relations_dict['Unitized Instructor Names']
    # If a single string is input, converts to list of the string for compatibility
    if type(full_text)==type(''):
        full_text=[full_text]
    clean_text=remove_excess_line_breaks_and_trash(full_text)
    clean_text=space_after_special_endings(clean_text) # WHAT DOES THIS DO?

    # Convert paragraphs in clean_text into individual sentences by period. Also deidentifies names. 
    first_parse=[]
    for sentence in clean_text:
        removing_decimals=remove_special_periods(sentence)
        parsed_by_period=split_by_period(removing_decimals)
        for entry in parsed_by_period:
            stripped_entry=entry.strip()
            if len(stripped_entry)>0: # Continues cleaning process on nonempty lines. 
                if stripped_entry[-1] not in ["?", "!", "]", ",", ")", ":"]: # Checks if the last entry is a special ending. If not, it adds a period that is not there.
                    stripped_entry+="." # Add period back to end of sentence
                stripped_entry=replace_utfs(stripped_entry)

                # Checks for the new comment phrase "SPEAKER [name]". Removes it for just the name of the speaker if it appears.
                if "SPEAKER " not in stripped_entry:
                    stripped_entry=deidentify_names(stripped_entry, deidentify_student_names, deidentify_instructor_names)
                # Split special case where punctuation occures within quotations - STILL NEEDS TO BE ADDED
                # Add entry to list of fully_parsed sentences
                first_parse.append(stripped_entry) # Only added to first_parse if nonempty and cleaned.

    second_parse=strip_by_special_character('!', first_parse)
    third_parse=strip_by_special_character('?', second_parse)

    clean_text_again=[]
    # Strips away additional spaces and breaks, just in case. Also removes empty sentences from array.
    for entry in third_parse:
        entry.strip()
        cleaned_for_excel=remove_dash_equal(entry)
        no_break_entry=cleaned_for_excel.replace('\n', '')
        clean_entry=no_break_entry.replace('. ', '.')
        encode_to_clean=clean_entry.encode("ascii", "ignore")
        clean_entry=encode_to_clean.decode()
        # Special cases to combine string with previous line
        if len(clean_entry)>0 and len(clean_text_again)>0:
            previous_line=clean_text_again[len(clean_text_again)-1]
            removed_period_previous_line=previous_line[:len(previous_line)-1]
            space=" "
            if clean_entry[0].islower() is True: # Attach to previous string if first letter is lower case
                clean_text_again[len(clean_text_again)-1]=removed_period_previous_line+space+clean_entry
            elif '(' in previous_line and ')' not in previous_line: # Attach this string to the previous string to avoid orphan parentheses
                clean_text_again[len(clean_text_again)-1]=removed_period_previous_line+space+clean_entry
            elif removed_period_previous_line.isdigit() is True: # This was the student numbering their argument
                clean_text_again[len(clean_text_again)-1]=f'{removed_period_previous_line}. {clean_entry}'
            elif "Step" in previous_line and removed_period_previous_line[-1].isdigit() is True and len(previous_line)<8:
                clean_text_again[len(clean_text_again)-1]=f'{previous_line} {clean_entry}'
            elif clean_entry != " ":
                clean_text_again.append(clean_entry)
        elif len(clean_entry)>0 and len(clean_text_again)==0:
            clean_text_again.append(clean_entry)
    return clean_text_again

### END OF DEFINITIONS FOR CURRENT PY FILE ###


def speaker_init(chunk):
    # Identifiers that are wrapped around speaker in pdf
    identifier_1="(http"
    identifier_2="erau.instructure.com"
    check_raw_split=chunk.split()
    new_lines=[chunk]
    all_split_lines=[]
    if len(check_raw_split) > 2:
        # Checks if something (a name) is inbetween declaration of a link and another link to the discussion
        if identifier_1 in check_raw_split[0] and identifier_2 in check_raw_split[len(check_raw_split)-1]: 
            # Split appropriately and return just speaker name
            split_identified_speaker_chunk_by_space=chunk.split()
            split_len=len(split_identified_speaker_chunk_by_space)
            speaker_name=f'{split_identified_speaker_chunk_by_space[1]}'
            for index in range(2, split_len-1):
                speaker_name=f'{speaker_name} {split_identified_speaker_chunk_by_space[index]}'
            new_lines=[f'SPEAKER {speaker_name}']
    for speaker_split_line in new_lines: 
        split_by_special_char=speaker_split_line.split(b'\xee\xa9\x9b'.decode('utf-8')) # Split lines by special characters that appear before speakers.
        for char_split_line in split_by_special_char:
            all_split_lines.append(char_split_line)
    return all_split_lines
### EXTRACT DEFINITIONS ###
def extract_text_from_pdf(file_path):
    pdf_file=fitz.open(file_path)
    raw_document=[]
    semi_cleaned_document=[]
    number_of_pages=pdf_file.page_count
    for page in pdf_file:
        blocks_in_page=[]
        blocks=page.get_text("blocks")
        for block in blocks:
            text=block[4]
            blocks_in_page.append(text)
        raw_document.append(blocks_in_page)
    for index in range(0, number_of_pages):
        blocks_in_page=raw_document[index]
        array_of_lines=[]
        for block in blocks_in_page:
            temp_array=speaker_init(block)
            for line in temp_array:
                joined_line=' '.join(line.splitlines())
                array_of_lines.append(joined_line)
        for line in array_of_lines:
            encode_to_check=line.encode("ascii", "ignore")
            decode_to_check=encode_to_check.decode()
            stripped_decode=decode_to_check.strip()
            if "Topic:" in line and "Discussion:" in line and "Module" in line: 
                continue
            elif "Topic: Module" in line and "Discussion" in line: # Post PDFS PHYS
                continue
            elif "http" in line and f'{index+1}/{number_of_pages}' in line:
                continue
            elif "s://" in line or "s : / /" in line: 
                continue
            elif stripped_decode=="Reply":
                continue
            elif "Reply" in stripped_decode and "like" in stripped_decode:
                continue
            elif "<image:" in line: 
                line='[image]'
                semi_cleaned_document.append(line)
            else:
                semi_cleaned_document.append(line)
    return semi_cleaned_document

def extract_text_from_docx(document_opened):
    # Extract text from document into array of paragraphs
    full_text=[] 
    for para in document_opened.paragraphs:
        if "Collapse Subdiscussion" in para.text:
            new_para=para.text
            replaced_by_speaker=new_para.replace("Collapse Subdiscussion ", "SPEAKER ")
            full_text.append(replaced_by_speaker)
        else:
            full_text.append(para.text)
    return full_text

def extract_text_from_html(file_path):
    # TO DO Still needs to be implemented
    text_from_html=[]
    return text_from_html

### END EXTRACT DEFINITIONS ###

### DEFS FOR IDENTIFIED DATA ###
def arrays_for_deidentification(dict_file_properties): # Dynamically define deidentified sets to use 
    # Structure: 
    # Take input from user to determine Class ID, Term, Cohort
    # Define 5 arrays based on the inputs: 
        #1   encode_student_names          Used to replace full name at start of post with speaker code
        #2   deidentify_student_names      Used to replace all other mentions of student name within the document with [name]
        #3   encode_instructor_names       Used to replace full name at start of post with speaker code
        #4   deidentify_instructor_names   Used to replace all other mentions of instructor name with their speaker code
        #5   list_of_instructor_IDs        Used when sorting dictonaries 
    class_ID=dict_file_properties['Class ID']
    term=dict_file_properties['Term']
    year=dict_file_properties['Year']
    cohort=dict_file_properties['Cohort']
    
    #Inititalize target arrays
    encode_student_names=[]
    deidentify_student_names=[]
    encode_instructor_names=[]
    deidentify_instructor_names=[]
    list_of_instructor_IDs=[]

    # Extract identified data
    path_to_identifiable_database=f'{base_dir}{path_break}Identifiable_Data{path_break}Deident_Key.xlsx'
    identifiable_data=pandas.read_excel(path_to_identifiable_database) # We need the first column, so it does not ignore the first column as other pandas.read_excel calls.
    identifiable_array=identifiable_data.to_dict('records')

    # Search through all identified data for relevant data
    for ident_dict in identifiable_array: 
        if ident_dict["Class ID"]==class_ID and ident_dict["Term"]==term and str(ident_dict["Year"])==year and str(ident_dict["Cohort"])==cohort: # Relevant identified data. Add to target arrays.
            if ident_dict["Speaker Type"]=="Student": # Add student info to student target arrays
                encode_student_names.append([ident_dict["Speaker Name"], ident_dict["Speaker ID"]])
                for part_of_name in ident_dict["Speaker Name"].split():
                    deidentify_student_names.append(part_of_name)
            else: # Add instructor info to instructor arrays
                encode_instructor_names.append([ident_dict["Speaker Name"], ident_dict["Speaker ID"]])
                deidentify_instructor_names.append([ident_dict["Speaker Name"].split()[1], ident_dict["Speaker ID"]])
                list_of_instructor_IDs.append(ident_dict["Speaker ID"])

    return [encode_student_names, deidentify_student_names, encode_instructor_names, deidentify_instructor_names, list_of_instructor_IDs]

### END DEFS FOR IDENTIFIED DATA ###
def check_file_naming_convention(file_name): # Checks file name for all necessary variables to deidentify file
    # Basic search through file name for acceptable values
    value_and_acceptable_values_pairing_array=[ ['Unknown', acceptable_class_IDs], ['Unknown', acceptable_terms], ['Unknown', acceptable_years] ]
    for variable_pair in value_and_acceptable_values_pairing_array: # For each pair of variable and acceptable values array
        for acceptable_value in variable_pair[1]: # For each acceptable value within the array of acceptable values
            if acceptable_value in file_name: # If the acceptable value is in the file name
                variable_pair[0]=acceptable_value # We reassign the variable
    class_ID=value_and_acceptable_values_pairing_array[0][0]
    term=value_and_acceptable_values_pairing_array[1][0]
    year=value_and_acceptable_values_pairing_array[2][0]

    # Dealing with special cases for cohort and module number
    cohort='Unknown'
    for cohort_index in acceptable_cohorts:
        if f'SECTION {cohort_index}' in file_name:
            cohort=cohort_index

    module_number='Unknown'
    for module_number_index in acceptable_module_numbers:
        if f'M{module_number_index}' in file_name:
            module_number=module_number_index

    return [class_ID, term, year, cohort, module_number]

def input_acceptable_string_loop(array_of_acceptable_inputs, initial_message, error_message): # while loop until the user gives a pre-defined accepted input in proper format
    initial=0
    user_input=''
    while user_input not in array_of_acceptable_inputs:
        if initial==0:
            initial=1
            user_input=input(initial_message)
        else:
            print(error_message)
            user_input=input(initial_message)
    return user_input

def user_defined_variables_for_deidentification(file_name): # Walks user through defining variables needed for deidentification, complete with while loops to protect against inproper inputs.
    html_scrape=input(f"Is {file_name} an html scrape? We don't need to define anything if it is. [y/n]: ")
    if html_scrape=='y' or html_scrape=='Y' or html_scrape=='Yes' or html_scrape=='yes':
        class_ID=''; term=''; year=''; cohort=''; module_number=''
    else:
        # Class IDs
        initial_message_class_IDs='Class ID\nAcceptable inputs: MATH, PHY\n'
        error_message_class_IDs='Be sure class ID is all caps and matches one of the acceptable IDs.\n'
        class_ID=input_acceptable_string_loop(acceptable_class_IDs, initial_message_class_IDs, error_message_class_IDs)

        # Term
        initial_message_terms='Term\nAcceptable inputs: AUG, SEP\n'
        error_message_terms='Be sure term is 3 letters long and is all-caps.\n'
        term=input_acceptable_string_loop(acceptable_terms, initial_message_terms, error_message_terms)

        # Year
        initial_message_years='Year\nAcceptable inputs: 2021, 2022\n'
        error_message_years='Be sure the year is 4 digits long.\n'
        year=input_acceptable_string_loop(acceptable_years, initial_message_years, error_message_years)

        # Cohort
        initial_message_cohorts='Cohort/Section\n Acceptable inputs: 1, 2, 3, 4, 5, 6, 7\n'
        error_message_cohorts='Be sure the cohort is a single number between 1 and 7 (inclusive).\n'
        cohort=input_acceptable_string_loop(acceptable_cohorts, initial_message_cohorts, error_message_cohorts)

        # Module Number
        initial_message_module_numbers='Module Number\n Acceptable inputs: 1, 2, 3, 4, 5, 6, 7, 8, 9\n'
        error_message_module_numbers='Be sure the module number is a single number between 1 and 9 (inclusive).\n'
        module_number=input_acceptable_string_loop(acceptable_module_numbers, initial_message_module_numbers, error_message_module_numbers)
    return [class_ID, term, year, cohort, module_number]

def define_dict_file_properties(file):
    dict_file_properties={}
    file_path=re.sub(f'{base_dir}{path_break}Documents_To_Deidentify{path_break}', '', file)
    clean_file_name, file_extension=re.split('\.', file_path, 1) # Splits as before period (clean_file_name) and after period (file_extension)
    dict_file_properties['File Name']=clean_file_name
    dict_file_properties['Extension']=file_extension
    dict_file_properties['File Path']=file_path

    class_ID, term, year, cohort, module_number = check_file_naming_convention(clean_file_name) # Checks if variables can be asertained based on file naming

    print(f'\nWelcome! Beginning to deidentify file \n\n{clean_file_name}\n\n')
    for string in [class_ID, term, year, cohort, module_number]:
        if string=='Unknown':
            print(f'Some values are unknown based on the file naming convention. Please input the following:\n')
            class_ID, term, year, cohort, module_number=user_defined_variables_for_deidentification(clean_file_name)
            break # As soon as one variable is unknown, we ask the user to define all variables, then break from the loop checking that all variables are defined. 

    # Now that properties were either extracted or manually defined, add to dict
    dict_file_properties['Class ID']=class_ID
    dict_file_properties['Term']=term
    dict_file_properties['Year']=year
    dict_file_properties['Cohort']=cohort
    dict_file_properties['Module Number']=module_number
    
    return dict_file_properties

def extract_preset_encoding(dict_file_properties):
    encode_student_names, deidentify_student_names, encode_instructor_names, deidentify_instructor_names, list_of_instructor_IDs=arrays_for_deidentification(dict_file_properties)
    speaker_array=[*encode_student_names, *encode_instructor_names] # Concates student and instructor names into speaker array for initializing speakers 
    encoding_dict={
        'Full Student Names': encode_student_names, 
        'Unitized Student Names': deidentify_student_names, 
        'Full Instructor Names': encode_instructor_names,
        'Unitized Instructor Names': deidentify_instructor_names, 
        'Instructor IDs': list_of_instructor_IDs,
        'Speaker Array': speaker_array
    }
    return encoding_dict

def extract_from_file(dict_file_properties):
    extension_type=dict_file_properties['Extension']
    if extension_type=='pdf':
        pdf_file_path=f'{base_dir}{path_break}Documents_To_Deidentify{path_break}{dict_file_properties["File Name"]}.pdf'
        text_from_file=extract_text_from_pdf(pdf_file_path)
    elif extension_type=='html':
        text_from_file=extract_text_from_html(f'{dict_file_properties["File Name"]}.html')
    elif extension_type=='xlsx': # Assumes html_scrape
        xlsx_file_path=f'{base_dir}{path_break}Documents_To_Deidentify{path_break}{dict_file_properties["File Name"]}.xlsx'
        text_from_file=pandas.read_excel(xlsx_file_path, index_col=[0])
    elif extension_type=='docx':
        word_document=Document(f'{dict_file_properties["File Name"]}.docx')
        text_from_file=extract_text_from_docx(word_document)
    else:
        print('\nNot implemented yet. No text was extracted, sorry.')
        text_from_file=[]
    return text_from_file


# Save data as array of dicts and write dicts to xlsx 
def save_pdf_or_docs_sentences_as_xlsx(encode_relations_dict, dict_file_properties, cleaned_sentences): 
    # Define arrays for organizing and saving results
    final_cleaning=[]
    initial_list_of_IDs=[]
    speaker_real_name=''
    word_delete_dead_line_after_speaker=0

    # Find SPEAKER and create blanks
    for sentence in cleaned_sentences:
        if "SPEAKER" in sentence: # If "SPEAKER" is in the sentence, define this as the new speaker's name.
            speaker_real_name=sentence.replace("SPEAKER ", "")
            if dict_file_properties['Extension']=="docx":
                word_delete_dead_line_after_speaker=1
        
        else: # Add the speaker name to the list of IDs and the sentence to the final cleaning
            if word_delete_dead_line_after_speaker==1:
                if "SPEAKER" not in sentence:
                    word_delete_dead_line_after_speaker=0
            elif sentence != '\".' and sentence != '\"?' and sentence != '\"!' and sentence != "" and sentence != ".":
                final_cleaning.append(sentence)
                initial_list_of_IDs.append(speaker_real_name)
    
    # Deidentify speakers
    list_of_IDs=[]
    for name_in_list in initial_list_of_IDs: 
        found_name=0
        # Encode instructor names
        for instructor_name in encode_relations_dict['Full Instructor Names']:
            if instructor_name[0] in name_in_list:
                list_of_IDs.append(instructor_name[1])
                found_name=1
        for student_name_encode in encode_relations_dict['Full Student Names']:
            if student_name_encode[0] in name_in_list:
                list_of_IDs.append(student_name_encode[1])
                found_name=1
        if found_name==0:
            list_of_IDs.append(name_in_list)

    # Create a dictonary for each sentence that can later be used to tag with code.
    list_of_dicts=[]
    for index in range(0, len(final_cleaning)):
        if list_of_IDs[index]!='': # Add to list_of_dicts as long as a Speaker ID appears
            temp_dict={}

            temp_dict["Analysis Unit"]=final_cleaning[index]
            temp_dict['Analysis Unit Index']=index

            if final_cleaning[index]=="":
                temp_dict["Speaker ID"]=""
            else:
                temp_dict["Speaker ID"]=list_of_IDs[index]

            if list_of_IDs[index] in encode_relations_dict['Instructor IDs']:
                temp_dict["Speaker Type"]="Instructor"
            else:
                temp_dict["Speaker Type"]="Student"
            
            temp_dict["Class ID"]=dict_file_properties['Class ID']
            temp_dict["Term"]=dict_file_properties['Term']
            temp_dict["Year"]=dict_file_properties['Year']
            temp_dict["Cohort"]=dict_file_properties['Cohort']
            temp_dict["Module Number"]=dict_file_properties['Module Number']
            temp_dict["Modify"]=""

            for researcher in researcher_names:
                temp_dict[researcher]='' # Initial empty code for each researcher

            list_of_dicts.append(temp_dict)

    # Create xlsx file
    xlsx_file_path=f'{base_dir}{path_break}Deidentified_xlsx_Files{path_break}{dict_file_properties["File Name"]}.xlsx'
    if os.path.exists(xlsx_file_path):
        os.remove(xlsx_file_path)
    Path(xlsx_file_path).touch()
    save_dicts_to_file(list_of_dicts, xlsx_file_path)
