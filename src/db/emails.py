import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import imaplib
import email
from email.header import decode_header
import pandas as pd
import time

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.db.base_db import BaseDB
from src.services.supabase_service import SupabaseService


class Emails(BaseDB):
    def __init__(
        self,
        supabase_client: SupabaseService = None,
        gmail_address: str = None,
        password: str = None,
    ) -> None:
        super().__init__()
        if not supabase_client:
            raise ValueError("Supabase client cannot be None")
        self.supabase = supabase_client
        self.table_name = "emails"
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.gmail_address = gmail_address
        self.password = password

    def set_begin_and_end_date(self, begin_date: datetime, end_date: datetime) -> None:
        """
        Formats begin and end dates into IMAP-compatible date strings.

        Args:
            begin_date (datetime): Start date
            end_date (datetime): End date

        Returns:
            tuple[str, str]: Formatted begin and end date strings
        """
        self.end_date_str = end_date.strftime("%d-%b-%Y")
        self.begin_date_str = begin_date.strftime("%d-%b-%Y")

    def get_email_addresses(self) -> list:
        """
        Gets a list of email addresses from the database.

        Returns:
            list: List of email addresses
        """
        result = self.supabase.select_from_table("emails", ["sender"], [])

        # Extract unique email addresses from results
        email_addresses = []
        if result:
            email_addresses = list(set([record["sender"] for record in result]))

        return email_addresses

    #  high level call called by extract_messages_from_important_emails
    def extract_recent_emails(self, important_addresses: list) -> list:
        """
        Extracts recent emails from a Gmail account within a specified date range.

        Args:
            gmail_address (str): The Gmail address to connect to
            password (str): The password or app-specific password for the Gmail account
            important_addresses (list): List of email addresses considered important
            begin_date (datetime): Start date for email extraction
            end_date (datetime): End date for email extraction

        Returns:
            list: A list of dictionaries containing extracted email data

        This function:
        1. Connects to Gmail's IMAP server
        2. Searches for emails within the specified date range
        3. Extracts relevant information from each email (subject, sender, date, content, attachments, URLs)
        4. Stores extracted data in the database
        5. Returns a list of extracted email data

        Improvements needed:
        - Implement error handling for network issues
        - Add support for OAuth 2.0 authentication
        - Optimize database operations (use batch inserts)
        - Implement rate limiting to avoid API restrictions
        - Add logging for better debugging
        - Separate database operations into a different function
        - Handle different email encodings more robustly
        - Implement parallel processing for faster extraction of large email volumes
        """
        # Connect to Gmail's IMAP server
        mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)

        try:
            # Login to the account
            mail.login(self.gmail_address, self.password)

            # Select the inbox
            mail.select("inbox")

            self.logger.info(
                f"Searching for emails from {self.begin_date_str} to {self.end_date_str}"
            )

            # Search for emails within the specified date range
            _, message_numbers = mail.search(
                None, f'(SINCE "{self.begin_date_str}" BEFORE "{self.  end_date_str}")'
            )

            emails = []

            for num in message_numbers[0].split():
                # Fetch the email message by ID
                _, msg = mail.fetch(num, "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        # Parse the email content
                        email_body = email.message_from_bytes(response[1])

                        # Get the date
                        date_str = email_body.get("Date")
                        if date_str:
                            date = email.utils.parsedate_to_datetime(date_str)
                        else:
                            self.logger.warning("No date found for email. Skipping...")
                            continue

                        # Get the sender
                        from_header = email_body.get("From", "")
                        sender = email.utils.parseaddr(from_header)[1]

                        # Continue if sender is not in important_addresses
                        if sender not in important_addresses:
                            continue

                        self.logger.info(f"Processing email from {sender}")
                        # Decode the subject
                        subject_header = email_body.get("Subject", "")
                        subject, encoding = decode_header(subject_header)[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8")

                        to_recipients = self._extract_to_recipients(email_body)
                        # Convert to_recipients dictionary to a string
                        to_recipients_str = ""
                        if (
                            isinstance(to_recipients, dict)
                            and "recipients" in to_recipients
                        ):
                            to_recipients_str = ", ".join(to_recipients["recipients"])

                        # Extract and store the email text
                        content = ""
                        if email_body.is_multipart():
                            for part in email_body.walk():
                                if part.get_content_type() == "text/plain":
                                    try:
                                        content = part.get_payload(decode=True).decode(
                                            encoding or "utf-8"
                                        )
                                    except UnicodeDecodeError:
                                        try:
                                            content = part.get_payload(
                                                decode=True
                                            ).decode("latin-1")
                                        except UnicodeDecodeError:
                                            self.logger.error(
                                                f"Failed to decode email content for {subject}"
                                            )
                                            content = "Unable to decode email content"
                                    break
                        else:
                            try:
                                content = email_body.get_payload(decode=True).decode(
                                    encoding or "utf-8"
                                )
                            except UnicodeDecodeError:
                                try:
                                    content = email_body.get_payload(
                                        decode=True
                                    ).decode("latin-1")
                                except UnicodeDecodeError:
                                    self.logger.error(
                                        f"Failed to decode email content for {subject}"
                                    )
                                    content = "Unable to decode email content"

                        urls = self._extract_urls_from_email(content)

                        # Extract attachment information
                        attachments = []
                        if email_body.is_multipart():
                            for part in email_body.walk():
                                if part.get_content_maintype() == "multipart":
                                    continue
                                if part.get("Content-Disposition") is None:
                                    continue
                                filename = part.get_filename()
                                if (
                                    filename
                                    and isinstance(filename, str)
                                    and len(filename.strip()) > 0
                                ):
                                    payload = part.get_payload(decode=True)
                                    if payload is not None:
                                        file_size = len(payload)
                                        attachments.append(
                                            {"filename": filename, "size": file_size}
                                        )

                        email_data = {
                            "subject": subject,
                            "sender": sender,
                            "date": date,
                            "attachments": attachments,
                            "to_recipients": to_recipients,
                            "content": content,
                            "urls": urls if urls else {"urls": []},
                        }

                        emails.append(email_data)

                        # Write the email to the database
                        # conn = connect_db()
                        # cursor = conn.cursor()

                        # Check if email already exists with same sender, date and content
                        try:
                            # cursor.execute(
                            #     """
                            #     SELECT email_id FROM emails
                            #     WHERE sender = ?
                            #     AND date = ?
                            #     AND content = ?
                            #     """,
                            #     (email_data["sender"], email_data["date"], email_data["content"]),
                            # )
                            # existing_email = cursor.fetchone()
                            existing_email_id = self._check_existing_email(email_data)

                            if existing_email_id:
                                self.logger.info(
                                    f"Skipping duplicate email from {email_data['sender']} on {email_data['date']}"
                                )
                                # cursor.close()
                                # conn.close()
                                continue

                        except Exception as e:
                            self.logger.error(f"Error checking for existing email: {e}")

                        try:
                            # cursor.execute(
                            #     """
                            #     INSERT INTO emails (date, sender, subject, to_recipients, content, attachment_cnt, url_cnt, created_at)
                            #     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            #     """,
                            #     (
                            #         email_data["date"],
                            #         email_data["sender"],
                            #         email_data["subject"],
                            #         to_recipients_str,
                            #         email_data["content"],
                            #         len(email_data["attachments"]),
                            #         len(email_data["urls"]["urls"]),
                            #         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            #     ),
                            # )
                            # conn.commit()
                            # email_id = cursor.lastrowid
                            email_id = self._insert_email(email_data, to_recipients_str)

                            if email_id:
                                # Write attachments to the attachments table
                                for attachment in email_data["attachments"]:
                                    # Strip leading "-" or " " from the filename
                                    cleaned_filename = attachment["filename"].lstrip(
                                        "- "
                                    )
                                    # cursor.execute(
                                    #     """
                                    # INSERT INTO attachments (email_id, filename, size, created_at)
                                    # VALUES (?, ?, ?, ?)
                                    # """,
                                    #     (
                                    #         email_id,
                                    #         cleaned_filename,
                                    #         attachment["size"],
                                    #         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    #     ),
                                    # )
                                    self._insert_attachment(
                                        email_id, cleaned_filename, attachment["size"]
                                    )
                                # Write URLs to the urls table
                                for url in email_data["urls"]["urls"]:
                                    # cursor.execute(
                                    #     """
                                    # INSERT INTO all_email_urls (email_id, url, created_at)
                                    # VALUES (?, ?, ?)
                                    # """,
                                    #     (email_id, url, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                    # )
                                    self._insert_url(email_id, url)
                        except Exception as e:
                            self.logger.error(
                                f"Error inserting email into database: {e}"
                            )
            return emails

        except Exception as e:
            self.logger.error(f"An error occurred while extracting emails: {e}")
            return []

        finally:
            # Close the connection
            mail.logout()

        # helper called by extract_recent_emails

    def _extract_to_recipients(self, email_body):
        """
        Extracts recipient email addresses from an email's To header.

        Args:
            email_body (email.message.Message): Email message object containing headers

        Returns:
            dict: Dictionary with key "recipients" containing list of extracted email addresses

        The function:
        1. Gets the To header from the email message
        2. Splits addresses on commas
        3. Parses each address using email.utils.parseaddr
        4. Returns dictionary with list of clean email addresses

        Improvements needed:
        - Add input validation for email_body
        - Handle malformed email addresses
        - Support CC and BCC recipients
        - Handle encoded headers (RFC 2047)
        - Add option to preserve display names
        - Return empty list instead of empty dict when no recipients
        - Add logging for parsing errors
        - Support group addresses (RFC 2822)
        """
        to_header = email_body.get("To", "")

        # Split the header into individual addresses
        addresses = to_header.split(",")

        # Extract email addresses using parseaddr and strip whitespace
        recipients = [
            email.utils.parseaddr(addr.strip())[1] for addr in addresses if addr.strip()
        ]

        # Create a dictionary with the "recipients" key and the list of recipients as the value
        result = {"recipients": recipients}

        # Convert the dictionary to a JSON-formatted string
        return result

    # helper called by extract_recent_emails
    def _extract_urls_from_email(self, email_body: str) -> dict | None:
        """
        Extracts URLs from an email body using regex pattern matching.

        Args:
            email_body (str): The body text of an email to search for URLs

        Returns:
            dict: Dictionary with key "urls" containing list of found URLs, or None if no URLs found

        The function:
        1. Uses regex to find URLs matching http/https pattern
        2. Returns dictionary format for consistency with other extraction functions
        3. Returns None if no URLs found

        Improvements needed:
        - Add input validation for email_body
        - Handle malformed URLs
        - Support additional URL patterns (ftp, etc)
        - Add URL validation/sanitization
        - Consider returning empty list instead of None for consistency
        - Add option to deduplicate URLs
        - Support extracting URL metadata (title, domain, etc)
        """
        import re

        # Regular expression pattern to match URLs
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

        # Find all matches of the URL pattern in the email body
        urls = re.findall(url_pattern, email_body)

        if not urls:
            return None

        # Return a dictionary with the "urls" key and the list of URLs as the value
        return {"urls": urls}

    def _check_existing_email(self, email_data: dict) -> dict | None:
        """
        Checks if an email already exists in the database with the same sender, date and content.

        Args:
            email_data (dict): Dictionary containing email data with sender, date and content

        Returns:
            dict | None: The existing email record if found, None otherwise
        """
        return self.supabase.select_from_table(
            "emails",
            ["email_id"],
            [
                ("sender", "eq", email_data["sender"]),
                ("date", "eq", email_data["date"]),
                ("content", "eq", email_data["content"]),
            ],
        )

    def _insert_email(
        self, email_data: dict | list, to_recipients_str: str = None
    ) -> int | list:
        """
        Inserts one or more email records into the database using Supabase.

        Args:
            email_data (dict | list): Single dictionary or list of dictionaries containing email data
            to_recipients_str (str, optional): Comma-separated string of recipient emails, only used for single records

        Returns:
            int | list: ID of the inserted email record(s)
        """
        if isinstance(email_data, dict):
            # Handle single record
            data = {
                "date": email_data["date"],
                "sender": email_data["sender"],
                "subject": email_data["subject"],
                "to_recipients": to_recipients_str,
                "content": email_data["content"],
                "attachment_cnt": len(email_data["attachments"]),
                "url_cnt": len(email_data["urls"]["urls"]),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        else:
            # Handle multiple records
            data = email_data

        result = self.supabase.insert_into_table("emails", data)
        if isinstance(email_data, dict):
            return result[0]["id"] if result else None
        return [record["id"] for record in result] if result else []

    def _insert_attachment(
        self, email_id: int | list, cleaned_filename: str | list, size: int | list
    ) -> int | list:
        """
        Inserts one or more attachment records into the database using Supabase.

        Args:
            email_id (int | list): ID(s) of the associated email record(s)
            cleaned_filename (str | list): Sanitized filename(s) of the attachment(s)
            size (int | list): Size(s) of the attachment(s) in bytes

        Returns:
            int | list: ID(s) of the inserted attachment record(s)
        """
        if isinstance(email_id, int):
            # Handle single record
            data = {
                "email_id": email_id,
                "filename": cleaned_filename,
                "size": size,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        else:
            # Handle multiple records
            data = [
                {
                    "email_id": eid,
                    "filename": fname,
                    "size": s,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                for eid, fname, s in zip(email_id, cleaned_filename, size)
            ]

        result = self.supabase.insert_into_table("attachments", data)
        if isinstance(email_id, int):
            return result[0]["id"] if result else None
        return [record["id"] for record in result] if result else []

    def _insert_url(self, email_id: int | list, url: str | list) -> int | list:
        """
        Inserts one or more URL records into the database using Supabase.

        Args:
            email_id (int | list): ID(s) of the associated email record(s)
            url (str | list): URL(s) found in the email(s)

        Returns:
            int | list: ID(s) of the inserted URL record(s)
        """
        if isinstance(email_id, int):
            # Handle single record
            data = {
                "email_id": email_id,
                "url": url,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        else:
            # Handle multiple records
            data = [
                {
                    "email_id": eid,
                    "url": u,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                for eid, u in zip(email_id, url)
            ]

        result = self.supabase.insert_into_table("all_email_urls", data)
        if isinstance(email_id, int):
            return result[0]["id"] if result else None
        return [record["id"] for record in result] if result else []

    def import_csv_in_batches(self, csv_file_path: str, batch_size: int = 2) -> None:
        """
        Imports a CSV file into Supabase in smaller batches to avoid timeout issues.

        Args:
            csv_file_path (str): Path to the CSV file
            batch_size (int): Number of records to process in each batch
        """
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        total_records = len(df)

        # Calculate number of batches
        num_batches = (total_records + batch_size - 1) // batch_size

        self.logger.info(f"Processing {total_records} records in {num_batches} batches")

        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_records)

            batch_df = df.iloc[start_idx:end_idx]

            self.logger.info(
                f"Processing batch {i+1}/{num_batches} (records {start_idx+1} to {end_idx})"
            )

            try:
                # Convert DataFrame batch to list of dictionaries
                records = batch_df.to_dict("records")

                # Insert batch into Supabase
                result = self.supabase.insert_into_table(self.table_name, records)

                if result:
                    self.logger.info(f"Successfully inserted batch {i+1}")
                else:
                    self.logger.error(f"Failed to insert batch {i+1}")

            except Exception as e:
                self.logger.error(f"Error processing batch {i+1}: {e}")

            # Optional: Add a small delay between batches to prevent rate limiting
            time.sleep(1)


if __name__ == "__main__":
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)
    emails = Emails(supabase)
    emails.import_csv_in_batches("file_types/csvs/emails.csv")
