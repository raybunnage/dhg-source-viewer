# CREATE TABLE "temp_experts" (
# 	"expert_id"	INTEGER,
# 	"expert_name"	TEXT,
# 	"starting_ref_id"	INTEGER, full_name TEXT, is_in_core_group INTEGER DEFAULT 0,
# 	PRIMARY KEY("expert_id")
# )

# CREATE TABLE public.experts (
#   id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
#   expert_name text NOT NULL,
#   full_name text NOT NULL,
#   starting_ref_id integer NULL,
#   is_in_core_group boolean DEFAULT false,
#   created_at timestamp with time zone DEFAULT now(),
#   updated_at timestamp with time zone DEFAULT now(),
#   created_by uuid NOT NULL,
#   updated_by uuid NOT NULL,
#   domain_id uuid NOT NULL,
#   user_id uuid NOT NULL,
#   expertise_area text NULL,
#   bio text NULL,
#   experience_years integer NULL,
#   CONSTRAINT experts_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES public.domains(id),
#   CONSTRAINT experts_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
# );

# -- ALTER TABLE public.experts ENABLE ROW LEVEL SECURITY;

# CREATE INDEX ON public.experts(domain_id);
# CREATE INDEX ON public.experts(user_id);

# CREATE OR REPLACE FUNCTION transfer_temp_experts_to_experts()
# INSERT INTO public.experts (expert_name, full_name, starting_ref_id, is_in_core_group, created_by, updated_by, domain_id, user_id)
#   SELECT
#     expert_name,
#     full_name,
#     starting_ref_id,
#     (is_in_core_group <> 0) AS is_in_core_group,
#     'f5972054-059e-4b1e-915e-268bcdcc94b9',
#     'f5972054-059e-4b1e-915e-268bcdcc94b9',
#     '752f3bf7-a392-4283-bd32-e3f0e530c205',
#     'f5972054-059e-4b1e-915e-268bcdcc94b9'
#   FROM public.temp_experts;
