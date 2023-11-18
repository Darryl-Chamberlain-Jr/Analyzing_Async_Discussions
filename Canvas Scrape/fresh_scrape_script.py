from canvasapi import Canvas
import pandas
import os
import re

from Defs.html_scrape_cleaning import *

API_url='https://canvas.instructure.com'
# Change to your API key
#darryl_API_key='2386~frxW4VyE1DhfLNNguGSikQqChn4EXPEnwTVdBOMXCMohKs8SiECJa8BtnF44EIyV'
zack_API_key='2386~AOsQlkZwKRnY5Gxle1ocPDRLlvx9hKulvELBLFhEg1qGjv6WgTts4XOz0o9eIK4o'

canvas = Canvas(API_url, zack_API_key)

# Base number 
base_number=23860000000
course=canvas.get_course(23860000000154913)
discussion_2=course.get_discussion_topic(23860000003042656)
dict_file_properties={
    'File Name': 'discussion_2_test'
}

### 

post_id_re_search=f'\({base_number}.+\)$'

def check_for_replies(discussion_entry):
    try:
        list_of_entry_replies=[]
        for reply in discussion_entry.get_replies():
            list_of_entry_replies.append(reply)
    except:
        list_of_entry_replies=[]
    finally:
        return list_of_entry_replies

def dict_for_discussion_entry(entry, entry_number):
    post_dict={
        'Entry': entry_number, 
        'Post or Reply': 'Post',
        'Replied to': '',
        'Reply Level': '',
        'Course ID': str(entry.course_id)[-6:],
        'Message': entry.message,
        'Discussion Title': entry.get_discussion().title,
        'Created At': entry.created_at,
        'User ID': str(entry.user_id)[-6:],
    }
    return post_dict

def dict_for_discussion_reply(reply_dict):
    reply_dict_for_db={
        'Entry': reply_dict['Entry'],
        'Post or Reply': 'Reply',
        'Replied to': reply_dict['Replied to'],
        'Reply Level': reply_dict['Reply Level'],
        'Course ID': str(reply_dict['Subreply Entry'].course_id)[-6:],
        'Message': reply_dict['Subreply Entry'].message,
        'Discussion Title': reply_dict['Discussion Title'],
        'Created At': reply_dict['Subreply Entry'].created_at,
        'User ID': str(reply_dict['Subreply Entry'].user_id)[-6:],
    }
    return reply_dict_for_db


entry_number=0
singular_entry_array=[]
array_for_reversal=[]
for grab_entry in discussion_2.get_topic_entries():
    array_for_reversal.append(grab_entry)

for entry in array_for_reversal[::-1]:
    entry_number+=1
    post_dict=dict_for_discussion_entry(entry, entry_number)
    singular_entry_array.append(post_dict)

    for reply in entry.get_replies():
        # Reply may have many subreplies
        reply_level=1
        try:
            subreply_array=reply.get_replies()
            for subreply in subreply_array:
                subreply_dict={
                    'Replied to': reply.message,
                    'Subreply Entry': subreply, 
                    'Reply Level': 2, 
                    'Entry': entry_number,
                    'Discussion Title': entry.get_discussion().title
                }

            for subreply_dict in subreply_array:
                # Could have been achieved with while loop popping single responses out and splitting non-single slices. End loop when evaluation array (queue) is empty
                try:
                    for another_reply in subreply['Subreply Entry'].get_replies():
                        # Cycle it back to get reworked
                        another_reply_dict={
                            'Replied to': subreply['Subreply Entry'].message,
                            'Subreply Entry': another_reply['Subreply Entry'].message,
                            'Reply Level': another_reply['Reply Level']+1, 
                            'Entry': entry_number, 
                            'Discussion Title': entry.get_discussion().title
                        }
                        subreply_array.append(another_reply)
                except:
                    # subreply has no subreplies
                    singular_entry_array.append(subreply_dict)
                
        # If subreply_array errors, there were no replies
        except:
            reply_dict_for_db={
                'Entry': entry_number,
                'Post or Reply': 'Reply',
                'Replied to': entry.message,
                'Reply Level': reply_level,
                'Course ID': str(entry.course_id)[-6:],
                'Message': reply.message,
                'Discussion Title': entry.get_discussion().title,
                'Created At': reply.created_at,
                'User ID': str(reply.user_id)[-6:],
            }
            singular_entry_array.append(reply_dict_for_db)

new_dataframe=pandas.DataFrame.from_dict(singular_entry_array)
encode_relations_dict={
    'Full Student Names': [], 
    'Unitized Student Names': [], 
    'Full Instructor Names': [],
    'Unitized Instructor Names': [], 
    'Instructor IDs': [],
    'Speaker Array': []
}

save_html_scrape_df_as_xlsx(encode_relations_dict, dict_file_properties, new_dataframe)

