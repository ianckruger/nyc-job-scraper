# nyc-job-scraper

src/job hunter/sources provides adapters for each job source, which keeps them isolated from one another
pipeline/ turns raw postings into comparable job objects after cleaning up the data. 
    flow: discover ==> fetch ==> parse ==> normalize ==> dedupe ==> enrich ==> rank
filters is self explanatory, swap the files out for what you want if you use this
taxonomy is just normalization of similar job positions
storage is database layer for SQlite to postgres
services is outputs for exports or alerts for new postings 

3 focused source handlers 
- structured ATS sources
- public city/company career pages
- a fallback to html scrapers

core scraped object should look like the following
JobPosting
- id
- source
- source_job_id
- title
- company
- location
- remote_policy
- job_url
- apply_url
- description 
- posted_at
- scraped_at
- salary_min
- salary_max
- currency
- tags
- score
- is_swe_relevant
- is_nyc_relevant

For canonic job models look to [Models Page](src/job_hunter/core/models.py)
    - this helps normalize an internal object across multiple different sources, so a lever and workday object look the same.
    - metadata helps find source specific junk without forcing it into main schema

Every source should answer some basic questions:
    - where do i discover the jobs
    - how do i fetchyour job page or job api responses
    - how do i parse it into the above mentioned object
[The Base Page](src/job_hunter/sources/base.py) answers this

filtering modules can be found in the filtering folder, seperate from source. give ways to add to score instead of completely remove in a binary
[SWE Filters](src/job_hunter/filters/swe.py)
[NYC Filters](src/job_hunter/filters/nyc.py)


The DB works by getting the source adapter, taking the created job posting object, creating a connection and store it in the database  
    source adapter --> job object --> repository --> database

prevents scraping code from building sql strings directly, rather it creates instances of the job object and passes it to repo

