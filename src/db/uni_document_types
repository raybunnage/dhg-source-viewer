
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService
from dotenv import load_dotenv
from typing import Optional

class DocumentTypes:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_document_type_id_with_alias(self, document_type: str) -> Optional[str]:
        try:
            # First try direct lookup in document_types
            result = self.supabase.select_from_table(
                "document_types",
                [id"],
                [("LOWER(document_type)", "eq", document_type.lower())]
            )

            if result:
                return result[0]['id']

            # If not found, try looking up in aliases
            result = self.supabase.select_from_table(
                "document_type_aliases",
                ["document_type_uuid"],
                [("LOWER(alias_name)", "eq", document_type.lower())]
            )

            return result[0]['document_type_uuid'] if result else None

        except Exception as e:
            print(f"Error looking up document type: {str(e)}")
            return None





-- CREATE TABLE public.uni_document_types (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     domain_id UUID REFERENCES public.domains(id) ON DELETE SET NULL,
--     document_type TEXT NOT NULL,
--     current_num_of_type INTEGER,
--     description TEXT,
--     is_ai_generated INTEGER,
--     mime_type TEXT NULL,
--     file_extension TEXT NULL,
--     document_type_counts INTEGER DEFAULT 0,
--     category TEXT,
--     is_active BOOLEAN DEFAULT TRUE,
--     created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
--     updated_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
--     updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
--     version INTEGER DEFAULT 1,
--     required_fields JSONB
-- );



-- INSERT INTO public.uni_document_types (document_type, current_num_of_type, description, is_ai_generated, mime_type, file_extension, document_type_counts, category, version)
-- SELECT document_type, current_num_of_type, description, is_ai_generated, mime_type, file_extension, document_type_counts, category, 1 from temp_document_types

-- update uni_document_types
-- set domain_id = '752f3bf7-a392-4283-bd32-e3f0e530c205',
--     created_at = now(),
--     updated_at = now(),
--     created_by = 'f5972054-059e-4b1e-915e-268bcdcc94b9',
--     updated_by = 'f5972054-059e-4b1e-915e-268bcdcc94b9'