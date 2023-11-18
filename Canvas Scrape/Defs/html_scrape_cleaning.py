import re
import numpy

from .deidentify import *

before_breaks_replacement_array=[
    {'Html': '\n', 'Replace with': ''},
    {'Html': '<strong>', 'Replace with': ''},
    {'Html': '</strong>', 'Replace with': ''}, 
    {'Html': '<em>', 'Replace with': ''},
    {'Html': '</em>', 'Replace with': ''}
]
after_breaks_replacement_array=[
    {'Html': '&nbsp;', 'Replace with': ' '}, 
    {'Html': '<div>', 'Replace with': ''},
    {'Html': '<div\sclass=.+>', 'Replace with': ''},
    {'Html': '<span\sclass=.+><span\sdata-offset-key.+>', 'Replace with': ''},
    {'Html': '<span\sdata-offset-key.+>', 'Replace with': ''},
    {'Html': '<span\sstyle=.+>', 'Replace with': ''},
    {'Html': '</div>', 'Replace with': ''},
    {'Html': '<img.+>', 'Replace with': '[image]'},
    {'Html': 'https://.+\s', 'Replace with': '[url]'},
    {'Html': '&amp;', 'Replace with': '&'},
    {'Html': '<script.+</script>', 'Replace with': ''},
    {'Html': '<ol>', 'Replace with': ''},
    {'Html': '</ol>', 'Replace with': ''},
    {'Html': '<ul>', 'Replace with': ''},
    {'Html': '</ul>', 'Replace with': ''},
    {'Html': '<p>', 'Replace with': ''}, # Special case when </p> is caught in a final script or image call.
    {'Html': '<li>', 'Replace with': ''}, # Special case 
    {'Html': '<sup>', 'Replace with': '^'}, 
    {'Html': '</sup>', 'Replace with': ''}
]
special_character_removal_array=[
    {'Replace': '\\n', 'With': ''},
    {'Replace': '\\\\:', 'With': ''},
]

def extract_equation(array):
    extract_equation_array=[]
    equation_regex='<img\sclass="equation_image".+?">'
    for sentence in array:
        if re.findall(equation_regex, sentence)!=[]:
            split_without_equation=re.split(equation_regex, sentence)
            raw_equation_array=re.findall(equation_regex, sentence)
            clean_equation_array=[]
            for raw_equation in raw_equation_array:
                # First try to extact the exact equation display
                try:
                    math_to_display=re.search('data-equation-content=".*?"', raw_equation).group()
                    cleaned_math=re.sub('data-equation-content="', '', math_to_display)
                    cleaned_math=re.sub('"', '', cleaned_math)
                    clean_equation_array.append(cleaned_math)
                # If an error occurs (such as not finding data-equation-content) substitute for a generic statement
                except:
                    clean_equation_array.append('[equation_image]')
            clean_sentence=split_without_equation.pop(0)
            while len(clean_equation_array)!=0:
                clean_sentence+=clean_equation_array.pop(0)
                clean_sentence+=split_without_equation.pop(0)
            extract_equation_array.append(clean_sentence)
        else:
            extract_equation_array.append(sentence)
    return extract_equation_array

def split_by_environment(array, env_html_sub, env_new_val, env_html_end):
    split_array=[]
    for entry in array:
        if re.findall(env_html_end, entry)!=[]:
            sentence_breaks=re.split(env_html_end, entry)
            for sentence in sentence_breaks:
                sentence=re.sub(env_html_sub, env_new_val, sentence)
                split_array.append(sentence)
        else:
            split_array.append(entry)
    return split_array

def split_sentences(old_entry):
    revised_entry=old_entry
    # Removes nan entries from splitting, returns an empty string
    if type(revised_entry) != type(''):
        return ['']
    try:
        for replacement_dict in before_breaks_replacement_array:
            revised_entry=re.sub(replacement_dict['Html'], replacement_dict['Replace with'], revised_entry)
    except:
        input(revised_entry)
    # Comb through arrays, splitting as necessary
    temp_array=extract_equation([revised_entry])
    temp_array=split_by_environment(temp_array, '<br>', '', '<br>')
    temp_array=split_by_environment(temp_array, '<a\sclass="instructure_file_link.*?>.*', '[file]', '</a>')
    temp_array=split_by_environment(temp_array, 'href=.*?>.*', '[url]', '<a')
    temp_array=split_by_environment(temp_array, '<span>', '', '</span>')
    #temp_array=split_by_environment(temp_array, '<div>', '', '</div>')
    temp_array=split_by_environment(temp_array, '<p.*?>', '', '</p>')
    temp_array=split_by_environment(temp_array, '<li>', '', '</li>')
    
    final_array=[]
    
    for entry in temp_array:
        # Skip nan entries
        if type(entry) != type(''):
            continue
        elif len(entry)>0:
            if entry[0]=='>' or entry[0]=='-':
                entry=entry[1:]
            final_entry=entry
            for replacement_dict in after_breaks_replacement_array:
                final_entry=re.sub(replacement_dict['Html'], replacement_dict['Replace with'], final_entry)
            # After cleaning, append to final array
            if type(final_entry) == type(''):
                final_entry=final_entry.strip()
            for special_character in special_character_removal_array:
                if special_character['Replace'] in final_entry:
                    final_entry=final_entry.replace(special_character['Replace'], special_character['With'])
            if len(final_entry)>0:
                final_array.append(final_entry)
    return final_array

def save_html_scrape_df_as_xlsx(encode_relations_dict, dict_file_properties, raw_df):
    # Workflow
        # Apply cleaning function to raw html row
        # Apply splitting function to raw html row, as single array of sentences
        # Rename columns with compatible column names
        # Explode single array of sentence column
    html_scrape_df=raw_df
    html_scrape_df['Analysis Unit']=html_scrape_df['Message'].apply(split_sentences)
    html_scrape_df=html_scrape_df.explode('Analysis Unit')
    html_scrape_df['Analysis Unit']=html_scrape_df['Analysis Unit'].apply(clean_array_of_sentences, args=(encode_relations_dict['Unitized Student Names'], encode_relations_dict['Unitized Instructor Names']))
    html_scrape_df=html_scrape_df.explode('Analysis Unit')
    html_scrape_df_file_path=f'{base_dir}{path_break}Cleaned_Files{path_break}{dict_file_properties["File Name"]}.xlsx'
    if os.path.exists(html_scrape_df_file_path):
        os.remove(html_scrape_df_file_path)
    html_scrape_df.to_excel(html_scrape_df_file_path)