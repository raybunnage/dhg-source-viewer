from exceptions import SupabaseConnectionError, SupabaseQueryError

class SupabaseService:
    def connect(self):
        try:
            # Supabase connection code
            pass
        except Exception as e:
            raise SupabaseConnectionError("Failed to connect to Supabase", original_error=e)

    def execute_query(self, query):
        try:
            # Query execution code
            pass
        except Exception as e:
            raise SupabaseQueryError(f"Query failed: {query}", original_error=e)