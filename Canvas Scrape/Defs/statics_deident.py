def define_acceptable_statics():
    acceptable_class_IDs=['MATH', 'PHY']
    acceptable_terms=['AUG', 'SEP']
    acceptable_years=['2021', '2022']
    acceptable_cohorts=['1', '2', '3', '4', '5', '6', '7']
    acceptable_module_numbers=['1', '2', '3', '4', '5', '6', '7', '8', '9']
    return [acceptable_class_IDs, acceptable_terms, acceptable_years, acceptable_cohorts, acceptable_module_numbers]

def column_names():
    headers_without_modify=['Speaker ID', 'Speaker Type', 'Class ID', 'Term', 'Year', 'Cohort', 'Module Number', 'Analysis Unit', 'Analysis Unit Index']
    static_headers=headers_without_modify+['Modify']
    researcher_names=['Emily', 'Syaza', 'Abigail', 'Patrick', 'Amina', 'Qaisara', 'Andrea', 'Emma', 'Elizabeth'] # Update when adding researchers
    database_header_array=static_headers+researcher_names
    return [headers_without_modify, static_headers, researcher_names, database_header_array]


acceptable_class_IDs, acceptable_terms, acceptable_years, acceptable_cohorts, acceptable_module_numbers=define_acceptable_statics()
headers_without_modify, static_headers, researcher_names, database_header_array=column_names()
special_period_set = [ [" p.", " p"], [" pg.", " pg"], [" PG.", " PG"], [" Pg.", " Pg"], ["p.s.", "ps"], ["P.S.", "PS"], [" lbs.", " lbs"], [" n.d.", " nd"], [" oz.", " oz"], [" AHA!", " AHA"], ["i.e.", " ie"], ["e.g.", " eg"], ["Mr.", "Mr"], ["Mrs.", "Mrs"], ["Ms.", "Ms"], ["Dr.", "Dr"], ["Prof.", "Prof"], ["Ph.D.", "PhD"], ["U.S.", "US"], [" al.", " al"], [" vs.", " vs"], [" hr.", " hr"], [" hrs.", " hrs"], [" et.", " et"], [" etc.", " etc"], [" a.k.a.", " aka"], [" .pdf", " pdf"], [" .jpg", " jpg"], [" .png", " png"], [" :)", " [smile-emoji]."], [" .s.g.", " sg"], ["...", "[dot dot dot]"]]