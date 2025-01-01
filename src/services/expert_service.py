from typing import Dict, Any
from services.base_service import BaseService
from services.exceptions import ValidationError, DuplicateError, ServiceError


class ExpertService(BaseService):
    def __init__(self, supabase_client):
        super().__init__(
            supabase_client=supabase_client,
            table_name="experts",
            logger_name="ExpertService",
        )

    @BaseService.log_operation
    async def create_expert_with_validation(
        self, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create expert with additional validation"""
        try:
            # Custom validation
            if not data.get("email"):
                raise ValidationError("Email is required")

            # Check for duplicate email
            existing = (
                await self.async_query()
                .select("id")
                .eq("email", data["email"])
                .single()
            )
            if existing:
                raise DuplicateError(
                    f"Expert with email {data['email']} already exists"
                )

            return await self.async_create(data)

        except ServiceError:
            raise
        except Exception as e:
            raise self.handle_error(e, "create_expert_with_validation")
