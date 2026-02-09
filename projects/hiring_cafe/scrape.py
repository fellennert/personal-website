import requests 
import pandas as pd 
import time

jobs_endpoint = "https://hiring.cafe/api/search-jobs"

payload = {
    "locations": [
        {
            "types": ["country"],
            "formatted_address": "United States",
            "address_components": [
                {
                    "long_name":"United States",
                    "short_name":"US",
                    "types": ["country"]
                }
            ],
            "workplace_types": ["Remote","Hybrid","Onsite"],
            "options":{},
            "id":"United Statescountry"
        }
    ],
    "searchQuery": "data scientist",
    "dateFetchedPastNDays":-1,
    "roleYoeRange":[0,4]
} 

headers = headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }

response = requests.post(
    jobs_endpoint,
    json=payload,
    headers=headers,
    timeout=30
    )
        
response.raise_for_status()
data = response.json()


#### SANDBOX


jobs_endpoint = "https://hiring.cafe/api/search-jobs"

# The exact encoded search state from the working URL
s_param = "JTdCJTIybG9jYXRpb25zJTIyJTNBJTVCJTdCJTIydHlwZXMlMjIlM0ElNUIlMjJjb3VudHJ5JTIyJTVEJTJDJTIyZm9ybWF0dGVkX2FkZHJlc3MlMjIlM0ElMjJVbml0ZWQlMjBTdGF0ZXMlMjIlMkMlMjJhZGRyZXNzX2NvbXBvbmVudHMlMjIlM0ElNUIlN0IlMjJsb25nX25hbWUlMjIlM0ElMjJVbml0ZWQlMjBTdGF0ZXMlMjIlMkMlMjJzaG9ydF9uYW1lJTIyJTNBJTIyVVMlMjIlMkMlMjJ0eXBlcyUyMiUzQSU1QiUyMmNvdW50cnklMjIlNUQlN0QlNUQlMkMlMjJ3b3JrcGxhY2VfdHlwZXMlMjIlM0ElNUIlMjJSZW1vdGUlMjIlMkMlMjJIeWJyaWQlMjIlMkMlMjJPbnNpdGUlMjIlNUQlMkMlMjJvcHRpb25zJTIyJTNBJTdCJTdEJTJDJTIyaWQlMjIlM0ElMjJVbml0ZWQlMjBTdGF0ZXNjb3VudHJ5JTIyJTdEJTVEJTJDJTIyd29ya3BsYWNlVHlwZXMlMjIlM0ElNUIlMjJSZW1vdGUlMjIlMkMlMjJIeWJyaWQlMjIlMkMlMjJPbnNpdGUlMjIlNUQlMkMlMjJkZWZhdWx0VG9Vc2VyTG9jYXRpb24lMjIlM0F0cnVlJTJDJTIydXNlckxvY2F0aW9uJTIyJTNBbnVsbCUyQyUyMnBoeXNpY2FsRW52aXJvbm1lbnRzJTIyJTNBJTVCJTIyT2ZmaWNlJTIyJTJDJTIyT3V0ZG9vciUyMiUyQyUyMlZlaGljbGUlMjIlMkMlMjJJbmR1c3RyaWFsJTIyJTJDJTIyQ3VzdG9tZXItRmFjaW5nJTIyJTVEJTJDJTIycGh5c2ljYWxMYWJvckludGVuc2l0eSUyMiUzQSU1QiUyMkxvdyUyMiUyQyUyMk1lZGl1bSUyMiUyQyUyMkhpZ2glMjIlNUQlMkMlMjJwaHlzaWNhbFBvc2l0aW9ucyUyMiUzQSU1QiUyMlNpdHRpbmclMjIlMkMlMjJTdGFuZGluZyUyMiU1RCUyQyUyMm9yYWxDb21tdW5pY2F0aW9uTGV2ZWxzJTIyJTNBJTVCJTIyTG93JTIyJTJDJTIyTWVkaXVtJTIyJTJDJTIySGlnaCUyMiU1RCUyQyUyMmNvbXB1dGVyVXNhZ2VMZXZlbHMlMjIlM0ElNUIlMjJMb3clMjIlMkMlMjJNZWRpdW0lMjIlMkMlMjJIaWdoJTIyJTVEJTJDJTIyY29nbml0aXZlRGVtYW5kTGV2ZWxzJTIyJTNBJTVCJTIyTG93JTIyJTJDJTIyTWVkaXVtJTIyJTJDJTIySGlnaCUyMiU1RCUyQyUyMmN1cnJlbmN5JTIyJTNBJTdCJTIybGFiZWwlMjIlM0ElMjJBbnklMjIlMkMlMjJ2YWx1ZSUyMiUzQW51bGwlN0QlMkMlMjJmcmVxdWVuY3klMjIlM0ElN0IlMjJsYWJlbCUyMiUzQSUyMkFueSUyMiUyQyUyMnZhbHVlJTIyJTNBbnVsbCU3RCUyQyUyMm1pbkNvbXBlbnNhdGlvbkxvd0VuZCUyMiUzQW51bGwlMkMlMjJtaW5Db21wZW5zYXRpb25IaWdoRW5kJTIyJTNBbnVsbCUyQyUyMm1heENvbXBlbnNhdGlvbkxvd0VuZCUyMiUzQW51bGwlMkMlMjJtYXhDb21wZW5zYXRpb25IaWdoRW5kJTIyJTNBbnVsbCUyQyUyMnJlc3RyaWN0Sm9ic1RvVHJhbnNwYXJlbnRTYWxhcmllcyUyMiUzQWZhbHNlJTJDJTIyY2FsY0ZyZXF1ZW5jeSUyMiUzQSUyMlllYXJseSUyMiUyQyUyMmNvbW1pdG1lbnRUeXBlcyUyMiUzQSU1QiUyMkZ1bGwlMjBUaW1lJTIyJTJDJTIyUGFydCUyMFRpbWUlMjIlMkMlMjJDb250cmFjdCUyMiUyQyUyMkludGVybnNoaXAlMjIlMkMlMjJUZW1wb3JhcnklMjIlMkMlMjJTZWFzb25hbCUyMiUyQyUyMlZvbHVudGVlciUyMiU1RCUyQyUyMmpvYlRpdGxlUXVlcnklMjIlM0ElMjIlMjIlMkMlMjJqb2JEZXNjcmlwdGlvblF1ZXJ5JTIyJTNBJTIyJTIyJTJDJTIyYXNzb2NpYXRlc0RlZ3JlZUZpZWxkc09mU3R1ZHklMjIlM0ElNUIlNUQlMkMlMjJleGNsdWRlZEFzc29jaWF0ZXNEZWdyZWVGaWVsZHNPZlN0dWR5JTIyJTNBJTVCJTVEJTJDJTIyYmFjaGVsb3JzRGVncmVlRmllbGRzT2ZTdHVkeSUyMiUzQSU1QiU1RCUyQyUyMmV4Y2x1ZGVkQmFjaGVsb3JzRGVncmVlRmllbGRzT2ZTdHVkeSUyMiUzQSU1QiU1RCUyQyUyMm1hc3RlcnNEZWdyZWVGaWVsZHNPZlN0dWR5JTIyJTNBJTVCJTVEJTJDJTIyZXhjbHVkZWRNYXN0ZXJzRGVncmVlRmllbGRzT2ZTdHVkeSUyMiUzQSU1QiU1RCUyQyUyMmRvY3RvcmF0ZURlZ3JlZUZpZWxkc09mU3R1ZHklMjIlM0ElNUIlNUQlMkMlMjJleGNsdWRlZERvY3RvcmF0ZURlZ3JlZUZpZWxkc09mU3R1ZHklMjIlM0ElNUIlNUQlMkMlMjJhc3NvY2lhdGVzRGVncmVlUmVxdWlyZW1lbnRzJTIyJTNBJTVCJTVEJTJDJTIyYmFjaGVsb3JzRGVncmVlUmVxdWlyZW1lbnRzJTIyJTNBJTVCJTVEJTJDJTIybWFzdGVyc0RlZ3JlZVJlcXVpcmVtZW50cyUyMiUzQSU1QiU1RCUyQyUyMmRvY3RvcmF0ZURlZ3JlZVJlcXVpcmVtZW50cyUyMiUzQSU1QiU1RCUyQyUyMmxpY2Vuc2VzQW5kQ2VydGlmaWNhdGlvbnMlMjIlM0ElNUIlNUQlMkMlMjJleGNsdWRlZExpY2Vuc2VzQW5kQ2VydGlmaWNhdGlvbnMlMjIlM0ElNUIlNUQlMkMlMjJleGNsdWRlQWxsTGljZW5zZXNBbmRDZXJ0aWZpY2F0aW9ucyUyMiUzQWZhbHNlJTJDJTIyc2VuaW9yaXR5TGV2ZWwlMjIlM0ElNUIlMjJObyUyMFByaW9yJTIwRXhwZXJpZW5jZSUyMFJlcXVpcmVkJTIyJTJDJTIyRW50cnklMjBMZXZlbCUyMiUyQyUyMk1pZCUyMExldmVsJTIyJTJDJTIyU2VuaW9yJTIwTGV2ZWwlMjIlNUQlMkMlMjJyb2xlVHlwZXMlMjIlM0ElNUIlMjJJbmRpdmlkdWFsJTIwQ29udHJpYnV0b3IlMjIlMkMlMjJQZW9wbGUlMjBNYW5hZ2VyJTIyJTVEJTJDJTIycm9sZVlvZVJhbmdlJTIyJTNBJTVCMCUyQzIwJTVEJTJDJTIyZXhjbHVkZUlmUm9sZVlvZUlzTm90U3BlY2lmaWVkJTIyJTNBZmFsc2UlMkMlMjJtYW5hZ2VtZW50WW9lUmFuZ2UlMjIlM0ElNUIwJTJDMjAlNUQlMkMlMjJleGNsdWRlSWZNYW5hZ2VtZW50WW9lSXNOb3RTcGVjaWZpZWQlMjIlM0FmYWxzZSUyQyUyMnNlY3VyaXR5Q2xlYXJhbmNlcyUyMiUzQSU1QiUyMk5vbmUlMjIlMkMlMjJDb25maWRlbnRpYWwlMjIlMkMlMjJTZWNyZXQlMjIlMkMlMjJUb3AlMjBTZWNyZXQlMjIlMkMlMjJUb3AlMjBTZWNyZXQlMkZTQ0klMjIlMkMlMjJQdWJsaWMlMjBUcnVzdCUyMiUyQyUyMkludGVyaW0lMjBDbGVhcmFuY2VzJTIyJTJDJTIyT3RoZXIlMjIlNUQlMkMlMjJsYW5ndWFnZVJlcXVpcmVtZW50cyUyMiUzQSU1QiU1RCUyQyUyMmV4Y2x1ZGVkTGFuZ3VhZ2VSZXF1aXJlbWVudHMlMjIlM0ElNUIlNUQlMkMlMjJsYW5ndWFnZVJlcXVpcmVtZW50c09wZXJhdG9yJTIyJTNBJTIyT1IlMjIlMkMlMjJleGNsdWRlSm9ic1dpdGhBZGRpdGlvbmFsTGFuZ3VhZ2VSZXF1aXJlbWVudHMlMjIlM0FmYWxzZSUyQyUyMmFpclRyYXZlbFJlcXVpcmVtZW50JTIyJTNBJTVCJTIyTm9uZSUyMiUyQyUyMk1pbmltYWwlMjIlMkMlMjJNb2RlcmF0ZSUyMiUyQyUyMkV4dGVuc2l2ZSUyMiU1RCUyQyUyMmxhbmRUcmF2ZWxSZXF1aXJlbWVudCUyMiUzQSU1QiUyMk5vbmUlMjIlMkMlMjJNaW5pbWFsJTIyJTJDJTIyTW9kZXJhdGUlMjIlMkMlMjJFeHRlbnNpdmUlMjIlNUQlMkMlMjJtb3JuaW5nU2hpZnRXb3JrJTIyJTNBJTVCJTVEJTJDJTIyZXZlbmluZ1NoaWZ0V29yayUyMiUzQSU1QiU1RCUyQyUyMm92ZXJuaWdodFNoaWZ0V29yayUyMiUzQSU1QiU1RCUyQyUyMndlZWtlbmRBdmFpbGFiaWxpdHlSZXF1aXJlZCUyMiUzQSUyMkRvZXNuJ3QlMjBNYXR0ZXIlMjIlMkMlMjJob2xpZGF5QXZhaWxhYmlsaXR5UmVxdWlyZWQlMjIlM0ElMjJEb2Vzbid0JTIwTWF0dGVyJTIyJTJDJTIyb3ZlcnRpbWVSZXF1aXJlZCUyMiUzQSUyMkRvZXNuJ3QlMjBNYXR0ZXIlMjIlMkMlMjJvbkNhbGxSZXF1aXJlbWVudHMlMjIlM0ElNUIlMjJOb25lJTIyJTJDJTIyT2NjYXNpb25hbCUyMChvbmNlJTIwYSUyMG1vbnRoJTIwb3IlMjBsZXNzKSUyMiUyQyUyMlJlZ3VsYXIlMjAob25jZSUyMGElMjB3ZWVrJTIwb3IlMjBtb3JlKSUyMiU1RCUyQyUyMmJlbmVmaXRzQW5kUGVya3MlMjIlM0ElNUIlNUQlMkMlMjJhcHBsaWNhdGlvbkZvcm1FYXNlJTIyJTNBJTVCJTVEJTJDJTIyY29tcGFueU5hbWVzJTIyJTNBJTVCJTVEJTJDJTIyZXhjbHVkZWRDb21wYW55TmFtZXMlMjIlM0ElNUIlNUQlMkMlMjJ1c2FHb3ZQcmVmJTIyJTNBbnVsbCUyQyUyMmluZHVzdHJpZXMlMjIlM0ElNUIlNUQlMkMlMjJleGNsdWRlZEluZHVzdHJpZXMlMjIlM0ElNUIlNUQlMkMlMjJjb21wYW55S2V5d29yZHMlMjIlM0ElNUIlNUQlMkMlMjJjb21wYW55S2V5d29yZHNCb29sZWFuT3BlcmF0b3IlMjIlM0ElMjJPUiUyMiUyQyUyMmV4Y2x1ZGVkQ29tcGFueUtleXdvcmRzJTIyJTNBJTVCJTVEJTJDJTIyaGlkZUpvYlR5cGVzJTIyJTNBJTVCJTVEJTJDJTIyZW5jb3VyYWdlZFRvQXBwbHklMjIlM0ElNUIlNUQlMkMlMjJzZWFyY2hRdWVyeSUyMiUzQSUyMmRhdGElMjBzY2llbnRpc3QlMjIlMkMlMjJkYXRlRmV0Y2hlZFBhc3RORGF5cyUyMiUzQS0xJTJDJTIyaGlkZGVuQ29tcGFuaWVzJTIyJTNBJTVCJTVEJTJDJTIydXNlciUyMiUzQW51bGwlMkMlMjJzZWFyY2hNb2RlU2VsZWN0ZWRDb21wYW55JTIyJTNBbnVsbCUyQyUyMmRlcGFydG1lbnRzJTIyJTNBJTVCJTVEJTJDJTIycmVzdHJpY3RlZFNlYXJjaEF0dHJpYnV0ZXMlMjIlM0ElNUIlNUQlMkMlMjJzb3J0QnklMjIlM0ElMjJkZWZhdWx0JTIyJTJDJTIydGVjaG5vbG9neUtleXdvcmRzUXVlcnklMjIlM0ElMjIlMjIlMkMlMjJyZXF1aXJlbWVudHNLZXl3b3Jkc1F1ZXJ5JTIyJTNBJTIyJTIyJTJDJTIyY29tcGFueVB1YmxpY09yUHJpdmF0ZSUyMiUzQSUyMmFsbCUyMiUyQyUyMmxhdGVzdEludmVzdG1lbnRZZWFyUmFuZ2UlMjIlM0ElNUJudWxsJTJDbnVsbCU1RCUyQyUyMmxhdGVzdEludmVzdG1lbnRTZXJpZXMlMjIlM0ElNUIlNUQlMkMlMjJsYXRlc3RJbnZlc3RtZW50QW1vdW50JTIyJTNBbnVsbCUyQyUyMmxhdGVzdEludmVzdG1lbnRDdXJyZW5jeSUyMiUzQSU1QiU1RCUyQyUyMmludmVzdG9ycyUyMiUzQSU1QiU1RCUyQyUyMmV4Y2x1ZGVkSW52ZXN0b3JzJTIyJTNBJTVCJTVEJTJDJTIyaXNOb25Qcm9maXQlMjIlM0ElMjJhbGwlMjIlMkMlMjJjb21wYW55U2l6ZVJhbmdlcyUyMiUzQSU1QiU1RCUyQyUyMm1pblllYXJGb3VuZGVkJTIyJTNBbnVsbCUyQyUyMm1heFllYXJGb3VuZGVkJTIyJTNBbnVsbCUyQyUyMmV4Y2x1ZGVkTGF0ZXN0SW52ZXN0bWVudFNlcmllcyUyMiUzQSU1QiU1RCU3RA"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}

all_jobs = []
page = 0

while True:
    print(f"Fetching page {page}...")

    
    # Build URL with parameters
    params = {
        's': s_param,
        'size': 40,
        'page': page
    }
    
    try:
        response = requests.get(jobs_endpoint, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract jobs from response
        jobs = data.get('results') or data.get('jobs') or data.get('data') or (data if isinstance(data, list) else [])
        
        if not jobs:
            print("No more jobs")
            break
        
        all_jobs.extend(jobs)
        print(f"  Got {len(jobs)} jobs (Total: {len(all_jobs)})")
        
        # Stop if last page
        if len(jobs) < 1:
            print("Last page reached")
            break
        
        page += 1
        
        # Safety limit
        if page >= 100:
            print("Max pages reached")
            break
        
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Error: {e}")
        break

print(f"\nTotal jobs collected: {len(all_jobs)}")

def flatten_job(job):
    """Flatten a single job into a flat dictionary"""
    flat = {}
    
    # Flatten v5_processed_job_data
    job_data = job.get('v5_processed_job_data', {})
    for key, val in job_data.items():
        flat[f'job_data.{key}'] = val
    
    # Flatten v5_processed_company_data
    company_data = job.get('v5_processed_company_data', {})
    for key, val in company_data.items():
        flat[f'company_data.{key}'] = val
    
    # Flatten job_information
    job_info = job.get('job_information', {})
    for key, val in job_info.items():
        flat[f'job_info.{key}'] = val
    
    # Flatten _geoloc (handle dict properly)
    geoloc = job.get('_geoloc', {})
    if isinstance(geoloc, dict):
        flat['geoloc.lat'] = geoloc.get('lat')
        flat['geoloc.lng'] = geoloc.get('lng')
    else:
        flat['geoloc'] = str(geoloc)
    
    # Add top-level fields
    for key in ['id', 'apply_url', 'source', 'objectID']:
        flat[key] = job.get(key)
    
    return flat

# Flatten all jobs
flattened = [flatten_job(job) for job in all_jobs]

# Single DataFrame creation
output_df = pd.DataFrame(flattened)

print(f"Shape: {output_df.shape}")
print(f"NAs per column:\n{output_df.isnull().sum()}")

## only select columns of interest
selected_df = output_df.loc[:, ['job_data.masters_degree_requirement', 
                                'job_data.workplace_type',
                                'job_data.relocation_assistance',
                                'job_data.workplace_counties',
                                'job_data.company_activities',
                                'job_data.company_sector_and_industry',
                                'job_data.commitment',
                                'job_data.requirements_summary',
                                'job_data.requirements_summary',
                                'job_data.is_compensation_transparent',
                                'job_data.bachelors_degree_fields_of_study',
                                'job_data.masters_degree_fields_of_study',
                                'job_data.doctorate_degree_fields_of_study',
                                'job_data.company_name',
                                'job_data.workplace_cities',
                                'job_data.technical_tools',
                                'job_data.workplace_states',
                                'job_data.core_job_title',
                                'job_data.seniority_level',
                                'job_data.min_industry_and_role_yoe',
                                'job_data.visa_sponsorship',
                                'job_data.role_activities',
                                'job_data.yearly_min_compensation',
                                'job_data.yearly_max_compensation',
                                'job_data.four_day_work_week',
                                'job_data.estimated_publish_date',
                                'company_data.num_employees',
                                'company_data.website',
                                'company_data.activities',
                                'company_data.industries',
                                'job_info.savedFromUsers',
                                'job_info.viewedByUsers',
                                'job_info.appliedFromUsers',
                                'job_info.title',
                                'job_info.description',
                                'geoloc'
                                ]]

output_df.to_csv("projects/hiring_cafe/job_listings_big.csv")
selected_df.to_csv("projects/hiring_cafe/job_listings_selected_big.csv")
