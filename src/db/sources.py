# CREATE TABLE public.sources (
#     source_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),  -- UUID for the source_id
#     domain_id uuid DEFAULT '752f3bf7-a392-4283-bd32-e3f0e530c205',  -- Default domain_id
#     user_id uuid DEFAULT 'f5972054-059e-4b1e-915e-268bcdcc94b9',    -- Default user_id
#     reference_tag TEXT,
#     source_type TEXT,
#     uni_document_type_id uuid DEFAULT '9dbe32ff-5e82-4586-be63-1445e5bcc548',
#     expert_id uuid DEFAULT 'f5972054-059e-4b1e-915e-268bcdcc94b9', 
#     title TEXT,
#     year INTEGER,
#     month INTEGER,
#     day INTEGER,
#     date_text TEXT,
#     trust_level INTEGER,
#     subject_classifications TEXT,
#     authors TEXT,
#     keywords TEXT,
#     source_identifier TEXT,
#     created_at timestamp with time zone DEFAULT now(),  -- Timestamp for creation
#     updated_at timestamp with time zone DEFAULT now(),  -- Timestamp for creation
#     parent_id uuid,  -- Changed to uuid for consistency
#     summary TEXT,
#     abstract TEXT,
#     cleaned_authors TEXT,
#     primary_authors TEXT,
#     ref_id INTEGER,
#     notes TEXT,
#     article_type TEXT,
#     reference_info TEXT,
#     aggregate_subject_classifications TEXT,
#     has_title_and_reference_info BOOLEAN DEFAULT false,  -- Changed to BOOLEAN
#     has_processing_errors BOOLEAN DEFAULT false,          -- Changed to BOOLEAN
#     processing_error TEXT,
#     all_references_cnt INTEGER,
#     concept_count INTEGER,
#     file_hash TEXT,
#     file_size BIGINT,
#     email_id uuid,
#     email_content_id uuid,
#     url_id uuid,
#     folder_level INTEGER,
#     relationship_action_id INTEGER,
#     google_id TEXT,
#     created_by uuid DEFAULT 'f5972054-059e-4b1e-915e-268bcdcc94b9',
#     updated_by uuid DEFAULT 'f5972054-059e-4b1e-915e-268bcdcc94b9'
# )

# CREATE INDEX idx_sources_domain_id ON public.sources(domain_id);

# CREATE INDEX idx_sources_user_id ON public.sources(user_id);

# CREATE INDEX idx_sources_expert_id ON public.sources(expert_id);

# CREATE INDEX idx_sources_google_id ON public.sources(google_id);