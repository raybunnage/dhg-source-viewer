import sys

sys.path.append("src")
from dbcrud.db import connect_db
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import email
from email.utils import parseaddr
import re
import json
from dbcrud.support_claude import call_claude_basic
from indexing.prompts import EXTRACT_INFORMATION_ABOUT_EMAIL_CONTENTS
from datetime import datetime
from typing import Optional, List, Tuple

# emails.py
"""
INSTRUCTIONS:

This module handles email processing, analysis, and storage in the database.

SITUATION: If you have new emails you consider these functions and call them as needed:
    1) determine if you are going back or going forward?
    2) which persons are you working on and which importance level?
        set_email_importance("davidrogerclawson@gmail.com", 1)
        update_important_email_status(1, 2)
        add_important_email_address("davidrogerclawson@gmail.com", 2)

if __name__ == "__main__":
    find_duplicate_email_ids_in_sources()
    set_email_importance("davidrogerclawson@gmail.com", 1)
    update_important_email_status(1, 2)
    add_important_email_address("davidrogerclawson@gmail.com", 2)

    gmail_address = "bunnage.ray@gmail.com"
    password = "uryj wgsu bbmk fnix"
    begin_date = datetime(2024, 10, 30)
    end_date = datetime(2024, 11, 6)
    importance_level = 1
    extracted_messages = extract_messages_from_important_emails(
        gmail_address, password, begin_date, end_date, importance_level
    )
    analyze_emails_with_importance_level("2024-10-30", 19, importance_level=1)

EXTERNAL FUNCTIONS:
1. support_claude: call_claude_basic: EXTRACT_INFORMATION_ABOUT_EMAIL_CONTENTS


MAIN FUNCTIONS:
1. * extract_messages_from_important_emails(gmail_address, password, begin_date, end_date, importance_level):
   - Extracts emails from Gmail for important addresses within a date range
   - Usage: Call to fetch and store new emails in the database

2. * analyze_emails_with_importance_level(from_date, stop_threshold, importance_level):
   - Analyzes emails not yet in email_contents table and processes their contents
   - Usage: Call after extracting emails to process their contents

3. * set_email_importance(email_address, importance_level):
   - Sets the importance level for a specific email address
   - Usage: Call to update or add important email addresses before extraction

4. * update_important_email_status(old_status, new_status):
   - Updates the status of important emails
   - Usage: Call to change the importance level of multiple emails before extraction

5. * add_important_email_address(email_address, importance_level):
   - Adds a new important email address to the database
   - Usage: Call when a new email address needs to be monitored before extraction

STANDALONE MAINTENANCE FUNCTIONS:
1. * find_duplicate_email_ids_in_sources():
   - Finds duplicate email ids in the sources table

HELPER FUNCTIONS:
1. extract_urls_from_email(email_body):
   - Extracts URLs from an email body
   - Called by: extract_messages_from_important_emails

2. extract_to_recipients(email_body):
   - Extracts recipient email addresses from an email's To header
   - Called by: extract_messages_from_important_emails

3. mark_email_as_in_contents(email_id):
   - Updates the is_in_contents flag for a given email ID
   - Called by: write_email_content_info

4. write_email_content_info(email_id, email_info):
   - Writes extracted email content information to the database
   - Called by: analyze_emails_with_importance_level

5. find_important_emails_not_in_contents(importance_level, from_date):
   - Finds important emails that have not been processed into the email_contents table
   - Called by: analyze_emails_with_importance_level

USAGE:
1. Set up important email addresses and their importance levels using set_email_importance() or add_important_email_address()
2. Extract recent emails using extract_messages_from_important_emails()
3. Analyze extracted emails with analyze_emails_with_importance_level()
4. Use standalone functions as needed for maintenance tasks

STATUS:
The module is functional but complex, handling various aspects of email processing from extraction to analysis. It interacts with multiple database tables and external APIs.

FEEDBACK:
1. Consider splitting into smaller, more focused modules (e.g., email_extraction.py, email_analysis.py, email_importance.py)
2. Implement classes to encapsulate related functionality and state
3. Improve error handling and logging throughout the module
4. Add more comprehensive documentation for each function
5. Implement a configuration file for easily adjustable parameters
6. Standardize function naming conventions (use snake_case consistently)
7. Reduce code duplication, especially in email extraction and processing logic
8. Consider implementing a proper EmailProcessor class to manage the entire workflow

UNUSED/DUPLICATE FUNCTIONS:
No unused or duplicate functions were identified in the provided snippet. However, a full code review of the entire module would be necessary to confirm this for the whole file.
"""


# * main email extraction function - called with many parameters
def extract_messages_from_important_emails(gmail_address, password, begin_date, end_date, importance_level):
    """
    Extracts messages from important email addresses within a specified date range.

    Args:
        gmail_address (str): The Gmail address to connect to.
        password (str): The password or app-specific password for the Gmail account.
        begin_date (datetime): The start date for email extraction.
        end_date (datetime): The end date for email extraction.
        importance_level (int): The importance level of email addresses to consider.

    Returns:
        list: A list of dictionaries containing extracted email data (sender, subject, date, message, attachments).

    This function:
    1. Retrieves important email addresses from the database based on the importance level.
    2. Extracts emails from these important addresses within the specified date range.
    3. Processes each email, extracting relevant information and attachments.
    4. Returns a list of processed email data.

    Improvements needed:
    - Implement proper error handling and logging instead of print statements.
    - Use a configuration file for importance levels and excluded URL patterns.
    - Implement retry logic for IMAP connection issues.
    - Consider using async operations for better performance with large email volumes.
    - Add input validation for date ranges and importance levels.
    - Implement a more robust method for parsing email bodies and attachments.
    - Consider using a separate function for processing individual emails to improve readability.
    """
    conn = connect_db()
    cursor = conn.cursor()

    # Get important email addresses
    cursor.execute("SELECT email_address FROM important_email_addresses WHERE is_important = ?", (importance_level,))
    important_addresses = [row[0] for row in cursor.fetchall()]

    conn.close()

    print("Important addresses:", important_addresses)

    if not important_addresses:
        print("No important email addresses found.")
        return []

    extracted_messages = []

    try:
        # Extract emails from important addresses
        important_emails = extract_recent_emails(gmail_address, password, important_addresses, begin_date, end_date)

        if important_emails is None:
            print("No emails extracted.")
            important_emails = []

        for email in important_emails:
            try:
                if email.get("sender") in important_addresses:
                    attachments = []
                    email_body = email.get("email_body")
                    if email_body and isinstance(email_body, email.message.Message) and email_body.is_multipart():
                        for part in email_body.walk():
                            if part.get_content_maintype() == "multipart":
                                continue
                            if part.get("Content-Disposition") is None:
                                continue
                            filename = part.get_filename()
                            payload = part.get_payload(decode=True)
                            if filename:
                                file_size = len(payload) if payload else 0
                                attachments.append({"filename": filename, "size": file_size})

                    extracted_messages.append(
                        {
                            "sender": email.get("sender", ""),
                            "subject": email.get("subject", ""),
                            "date": email.get("date"),
                            "message": email.get("body", ""),
                            "attachments": attachments,
                        }
                    )
            except TypeError as e:
                print(f"Error processing email: {e}")
                continue  # Skip this email and continue with the next one
    except imaplib.IMAP4.abort as e:
        print(f"IMAP connection aborted: {e}")
        # Implement a retry mechanism or handle the error as needed
    except Exception as e:
        print(f"An error occurred while extracting emails: {e}")
    finally:
        # Ensure IMAP connection is closed properly
        pass  # Removed mail.logout() since 'mail' is not defined here.

    return extracted_messages


# no longer used
news_web_sites = [
    "www.news-medical.net",
    "www.healio.com/news",
    "www.medscape.com/viewarticle",
    "www.nih.gov/news-events",
    "www.nature.com/articles",
    "www.sciencealert.com",
    "www.cell.com",
    "www.healthrising.org",
    "www.science.org/content/",
    "multiplesclerosisnewstoday.com",
    "www.scientificamerican.com/article",
    "www.biospace.com",
]


# List of tags in order of appearance:  called by analyze_naviaux_emails
email_tags = [
    "how_many_participants",
    "participant_list",
    "summary_of_the_email",
    "is_science_discussion",
    "is_science_material",
    "is_meeting_focused",
    "good_quotes_list",
]

# called by analyze_naviaux_emails
email_arrays = [
    "participant_list",
    "good_quotes_list",
]


# * called to analyze emails with a specified importance level that have not yet been processed and do not have the is_in_contents field set.
def analyze_emails_with_importance_level(from_date, stop_threshold=25, importance_level=2):
    """
    Analyzes emails with a specified importance level that have not yet been processed. A very important field in the emails table is the is_in_contents field.  You can find emails that are not in contents by using the this field.

    Args:
        from_date (str): The date from which to start analyzing emails (format: 'YYYY-MM-DD')
        stop_threshold (int, optional): Maximum number of emails to process. Defaults to 25.
        importance_level (int, optional): The importance level of emails to analyze. Defaults to 2.

    Returns:
        None

    This function:
    1. Connects to the database
    2. Retrieves unprocessed important emails
    3. Cleans and analyzes email content using Claude AI
    4. Processes and stores the analyzed content
    5. Updates the processed status of emails

    Improvements needed:
    - Add error handling for database operations
    - Implement logging instead of print statements
    - Add input validation for function parameters
    - Consider using a context manager for database connections
    - Implement batch processing for better performance
    - Add return value to indicate success/failure or processed count
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Fetch existing email_ids from email_contents table
        cursor.execute("SELECT email_id FROM email_contents")
        existing_email_ids = set(row[0] for row in cursor.fetchall())

        # Fetch all emails with 'naviaux' in sender or to_recipients, excluding those already in email_contents
        rows = find_important_emails_not_in_contents(importance_level, from_date)

        if not rows:
            print("No new emails found with experts in sender or recipients.")
            return

        processed_count = 0
        for row in rows:
            email_id, content = row
            if email_id not in existing_email_ids and content:
                # Remove extraneous newlines
                cleaned_content = " ".join(content.split())
                # Process if the content is between 100 and 10000 characters
                if len(cleaned_content) > 100 and len(cleaned_content) <= 15000:
                    print(f"Content length: {len(cleaned_content)} characters")
                    json_response = call_claude_basic(
                        1028, f"Text from email body:\n{cleaned_content}", EXTRACT_INFORMATION_ABOUT_EMAIL_CONTENTS
                    )
                    process_email_content(email_id, json_response, email_tags, email_arrays)
                    print("\n" + "-" * 50 + "\n")
                    processed_count += 1
                    if processed_count >= stop_threshold:
                        print(f"Reached stop threshold of {stop_threshold} processed emails.")
                        break

        # Update is_in_contents for processed emails
        if processed_count > 0:
            cursor.execute("""
                UPDATE emails
                SET is_in_contents = 1
                WHERE email_id IN (SELECT email_id FROM email_contents)
            """)
            conn.commit()

    except Exception as e:
        print(f"An analyze_emails_with_importance_level error occurred: {e}")

    finally:
        cursor.close()
        conn.close()


# helper function called by process_email_content
def process_array_fields(email_dict: dict, arrays: list) -> dict:
    """
    Processes specific array fields in the email dictionary.

    Args:
        email_dict (dict): The original email dictionary containing array fields.
        arrays (list): List of array field names to process.

    Returns:
        dict: A new dictionary with processed array fields.

    This function handles special processing for 'participant_list' and 'good_quotes_list' fields:
    - For 'participant_list': Strips whitespace and removes quotes and backslashes.
    - For 'good_quotes_list': Cleans and formats individual quotes, joining them with '| '.

    Improvements needed:
    - Add error handling for malformed input.
    - Consider moving print statements to a logging system.
    - Implement more robust parsing for quotes, possibly using regex.
    - Add support for processing other array types.
    - Consider returning both processed and original values for comparison.
    """
    processed_dict = email_dict.copy()

    for array_field in arrays:
        if array_field in processed_dict:
            value = processed_dict[array_field]
            if isinstance(value, str):
                # Remove braces at the beginning and end
                value = value.strip("[]")

                if array_field == "participant_list":
                    # Remove preceding or following white space, except newlines
                    value = "\n".join(line.strip() for line in value.split("\n"))
                    cleaned_string = value.replace('"', "").replace("\\", "")
                    processed_dict[array_field] = cleaned_string
                    print(f"participant_list: {cleaned_string}")

                elif array_field == "good_quotes_list":
                    cleaned_string = value.replace('"', "")
                    # Split the cleaned string into individual quotes
                    quotes = cleaned_string.split("\n")
                    # Process each quote
                    processed_quotes = []
                    for quote in quotes:
                        quote = quote.strip()
                        if "|" in quote:
                            quote = quote.replace("|", " (")
                            if not quote.endswith(")"):
                                quote += ")"
                        quote = quote.replace(" (,)", ")").replace(",)", ")")
                        quote = re.sub(r"(\n|\]|})", "", quote)
                        print(f"quote: {quote}")
                        if len(quote) > 2:
                            processed_quotes.append(quote)
                    # Join the processed quotes back into a single string
                    processed_dict[array_field] = "| ".join(processed_quotes)

    return processed_dict


# called by analyze_emails_with_importance_level
def process_email_content(email_id: int, content: str, tags: list, arrays: list):
    """
    Processes email content by extracting structured data, cleaning array fields, and writing to database.

    Args:
        email_id (int): ID of the email being processed
        content (str): Raw email content/text to process
        tags (list): List of tags to extract from the content
        arrays (list): List of array field names that need special processing

    Returns:
        None: Returns None if there is an error processing the content

    This function:
    1. Extracts structured data from AI output using extract_dict_from_ai_output()
    2. Processes array fields like participant_list and good_quotes_list
    3. Writes the cleaned data to the email_contents table

    Improvements needed:
    - Add proper error handling and return values
    - Replace print statements with logging
    - Add input validation for parameters
    - Return success/failure status and error details
    - Add retry logic for database operations
    - Consider making array field processing configurable
    - Add documentation of expected content format
    """
    email_dict = extract_dict_from_ai_output(tags, content)
    if email_dict is not None:
        processed_dict = process_array_fields(email_dict, arrays)
        if processed_dict is not None:
            new_id = write_email_content_info(email_id, processed_dict)
            print(f"Inserted cleaned email content info for new email_contents id: {new_id}")
        else:
            print(f"Error extracting JSON content for email id: {email_id}")
            return None


# called by process_email_content
def extract_dict_from_ai_output(tags: list, content: str) -> dict:
    """
    Extracts a dictionary of tag-content pairs from AI-generated output.

    Args:
        tags (list): List of tags to extract from the content.
        content (str): The AI-generated output containing JSON-like content.

    Returns:
        dict: A dictionary where keys are tags and values are the corresponding content.
               Returns None if extraction fails.

    This function:
    1. Finds the outermost JSON-like structure in the content.
    2. Locates each tag within the structure.
    3. Extracts the content for each tag.
    4. Constructs a dictionary of tag-content pairs.

    Improvements needed:
    - Add error handling for malformed JSON-like content.
    - Implement more robust JSON parsing (e.g., using json.loads() with error handling).
    - Add input validation for tags and content.
    - Consider using regex for more precise extraction.
    - Add logging instead of print statements.
    - Handle nested structures more effectively.
    - Return both the extracted dict and any error messages.
    """
    # Find the index of the first and last braces
    start_index = content.find("{")
    end_index = content.rfind("}")

    # Check if both braces are found and in the correct order
    if start_index != -1 and end_index != -1 and start_index < end_index:
        # Extract the content between the braces
        json_content = content[start_index : end_index + 1]
        if json_content:
            # Initialize a dictionary to store the start indices of each tag
            tag_indices = {}

            # Go through the list of tags and find the start index of each
            for tag in tags:
                tag_index = json_content.find(f'"{tag}"')
                if tag_index != -1:
                    tag_indices[tag] = tag_index

            # Create a sorted list of (tag, index) tuples
            sorted_tags = sorted(tag_indices.items(), key=lambda x: x[1])

            # Create a list to store the tag ranges
            tag_ranges = []

            # Iterate through the sorted tags to create the ranges
            for i, (tag, start_index) in enumerate(sorted_tags):
                if i < len(sorted_tags) - 1:
                    end_index = sorted_tags[i + 1][1]
                else:
                    end_index = len(json_content)

                tag_ranges.append((tag, start_index, end_index))

            # Iterate through the tag ranges and extract the content for each tag
            tag_content_tuples = []
            for tag, start, end in tag_ranges:
                # Extract the content for the current tag
                tag_content = json_content[start:end].strip()
                # Remove the tag and colon from the beginning of the content
                tag_content = re.sub(f'"{tag}"\s*:', "", tag_content, 1).strip()
                # Remove any trailing comma
                tag_content = tag_content.rstrip(",")
                # Add the new tuple with tag, start, end, and content
                tag_content_tuples.append((tag, start, end, tag_content))

            # Create a dictionary from the tag_content tuples
            extracted_dict = {tag: content for tag, _, _, content in tag_content_tuples}

            return extracted_dict

    return None


# helper function called by write_email_content_info
def mark_email_as_in_contents(email_id: int) -> bool:
    """
    Updates the is_in_contents flag to 1 for a given email ID in the emails table.
    Called by write_email_content_info() after successfully inserting email content.

    Args:
        email_id (int): The ID of the email to mark as processed

    Returns:
        bool: True if update was successful, False if an error occurred

    The function:
    1. Opens a database connection
    2. Updates the is_in_contents field to 1 for the specified email_id
    3. Commits the transaction if successful
    4. Rolls back if an error occurs
    5. Closes the connection

    Improvements needed:
    - Add input validation for email_id
    - Use logging instead of print statements
    - Add retry logic for transient DB errors
    - Consider using context manager for DB connection
    - Add option to batch process multiple email IDs
    - Return more detailed error information
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Update the is_in_contents field for the given email_id
        cursor.execute(
            """
            UPDATE emails
            SET is_in_contents = 1
            WHERE email_id = ?
            """,
            (email_id,),
        )
        conn.commit()
        print(f"Marked email id {email_id} as in contents")
        return True
    except Exception as e:
        print(f"Error marking email as in contents: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


# called by process_email_content
def write_email_content_info(email_id: int, email_info: dict) -> Optional[int]:
    """
    Writes email content information to the email_contents table and marks the email as processed.

    Args:
        email_id (int): The ID of the email to write content for.
        email_info (dict): A dictionary containing the email content information.

    Returns:
        Optional[int]: The ID of the newly inserted email content record if successful, None otherwise.

    This function:
    1. Inserts a new record into the email_contents table with the provided information.
    2. Marks the email as processed in the emails table.
    3. Commits the transaction if successful, rolls back if an error occurs.

    The email_info dictionary should contain the following keys:
    - how_many_participants (int): Number of participants in the email.
    - participant_list (list): List of participant names or email addresses.
    - summary_of_the_email (str): A summary of the email content.
    - is_science_discussion (bool): Whether the email contains scientific discussion.
    - is_science_material (bool): Whether the email contains scientific material.
    - is_meeting_focused (bool): Whether the email is focused on a meeting.
    - good_quotes_list (list): List of notable quotes from the email.

    Improvements needed:
    - Add input validation for email_id and email_info.
    - Use parameterized queries to prevent SQL injection.
    - Implement proper error logging instead of print statements.
    - Consider using a context manager for database connections.
    - Add retry logic for transient database errors.
    - Implement batch processing for multiple emails.
    - Add type hints for the email_info dictionary.
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO email_contents (
                email_id,
                how_many_participants,
                participants,
                summary_of_the_email,
                is_science_discussion,
                is_science_material,
                is_meeting_focused,
                good_quotes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email_id,
                email_info.get("how_many_participants", 0),
                json.dumps(email_info.get("participant_list", [])),
                email_info.get("summary_of_the_email", ""),
                int(email_info.get("is_science_discussion", 0)),
                int(email_info.get("is_science_material", 0)),
                int(email_info.get("is_meeting_focused", 0)),
                json.dumps(email_info.get("good_quotes_list", [])),
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        print(f"Inserted email content info for email id: {email_id}")

        # Mark the email as in contents after successful insertion
        if mark_email_as_in_contents(email_id):
            return new_id
        else:
            return None
    except Exception as e:
        print(f"Error writing email content info: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()


# called by main and by analyze_emails_with_importance_level
def find_important_emails_not_in_contents(importance_level: int, from_date: datetime) -> List[Tuple[int, str]]:
    """
    Finds important emails that have not been processed into the email_contents table.

    Args:
        importance_level (int): The importance level to filter important email addresses.
        from_date (datetime): The starting date to search for emails.

    Returns:
        List[Tuple[int, str]]: A list of tuples containing email_id and content for important emails
        not yet in the email_contents table.

    This function:
    1. Retrieves email addresses marked as important with the specified importance level.
    2. Searches for emails from these important senders that are not yet in the email_contents table.
    3. Returns a list of email IDs and contents for further processing.

    Improvements needed:
    - Add error handling for database connection issues.
    - Implement logging instead of print statements.
    - Use parameterized queries consistently for better security.
    - Consider pagination for large result sets.
    - Add type hints for better code readability.
    - Implement a more efficient query to avoid looping through important emails.
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Find all email addresses marked as important
        cursor.execute(
            """
            SELECT DISTINCT email_address 
            FROM important_email_addresses 
            WHERE is_important = ?
        """,
            (importance_level,),
        )
        important_emails = [row[0] for row in cursor.fetchall()]

        # Print out the list of important emails
        print(f"Important email addresses (importance level {importance_level}):")
        for email in important_emails:
            print(f"- {email}")

        # Find emails from important senders that are not in contents, from the specified date
        not_in_contents_ids = []
        for email in important_emails:
            cursor.execute(
                """
                SELECT email_id, content
                FROM emails 
                WHERE (sender LIKE ? OR to_recipients LIKE ?) 
                AND (is_in_contents is NULL)
                AND date >= ?
            """,
                (f"%{email}%", f"%{email}%", from_date),
            )
            not_in_contents_ids.extend(cursor.fetchall())

        print(
            f"Found {len(not_in_contents_ids)} emails from important senders that are not in contents, from {from_date}."
        )
        return not_in_contents_ids

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        cursor.close()
        conn.close()


# * standalone maintenance helper called by main
def add_important_email_address(email_address: str, is_important: int) -> None:
    """
    Adds a new email address to the important_email_addresses table.

    Args:
        email_address (str): The email address to add
        is_important (int): Importance level flag (typically 0 or 1)

    Returns:
        None

    The function:
    1. Connects to the database
    2. Inserts the email address and importance flag
    3. Commits the transaction
    4. Handles errors and closes connections properly

    Improvements needed:
    - Add input validation for email_address format
    - Add validation for is_important values
    - Return success/failure status
    - Add proper logging instead of print statements
    - Add duplicate checking before insert
    - Support batch inserts
    - Add option to update if exists
    - Add proper error handling with specific exceptions
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
        INSERT INTO important_email_addresses (email_address, is_important)
        VALUES (?, ?)
        """,
            (email_address, is_important),
        )
        conn.commit()
        print(
            f"Email address '{email_address}' added to important_email_addresses with is_important set to {is_important}."
        )
    except Exception as e:
        print(f"An error occurred while adding the email address: {e}")
    finally:
        cursor.close()
        conn.close()


# * helper called before extract_messages_from_important_emails to update the is_important field
def update_important_email_status(new_status: int, current_status: int) -> None:
    """
    Updates the is_important field in the important_email_addresses table from current_status to new_status.

    Args:
        new_status (int): The new is_important value to set.
        current_status (int): The current is_important value to match.

    Returns:
        None

    This function:
    1. Connects to the database.
    2. Updates all rows in important_email_addresses where is_important matches current_status.
    3. Sets is_important to new_status for these rows.
    4. Commits the transaction if successful, rolls back if an error occurs.
    5. Prints the number of affected rows.

    Improvements needed:
    - Add input validation for new_status and current_status (e.g., ensure they are 0 or 1).
    - Implement proper logging instead of print statements.
    - Return the number of affected rows instead of printing it.
    - Add more specific error handling (e.g., database connection errors).
    - Consider using a context manager for database connection.
    - Add option for dry run to preview changes without committing.
    - Implement batch processing for large updates to improve performance.
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE important_email_addresses 
            SET is_important = ?
            WHERE is_important = ?
        """,
            (new_status, current_status),
        )

        affected_rows = cursor.rowcount
        conn.commit()
        print(
            f"Updated {affected_rows} email addresses from is_important={current_status} to is_important={new_status}"
        )

    except Exception as e:
        print(f"An error occurred while updating important email status: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# * helper called by main before extract_messages_from_important_emails to update the is_important field
def set_email_importance(email_address, importance_level):
    """
    Updates the importance level for a specific email address in the important_email_addresses table.

    Args:
        email_address (str): The email address to update
        importance_level (int): The new importance level to set (typically 0 or 1)

    Returns:
        None

    This function:
    1. Connects to the database
    2. Updates the is_important field for the specified email address
    3. Commits the transaction if successful, rolls back if error occurs
    4. Prints confirmation message or error

    Improvements needed:
    - Add input validation for email_address format
    - Validate importance_level is valid (e.g., 0 or 1)
    - Return success/failure status instead of printing
    - Implement proper logging instead of print statements
    - Add error handling for specific database errors
    - Use context manager for database connection
    - Add option to create record if email doesn't exist
    - Return number of affected rows
    - Add docstring examples
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE important_email_addresses 
            SET is_important = ?
            WHERE email_address = ?
            """,
            (importance_level, email_address),
        )
        conn.commit()
        print(f"Email address '{email_address}' importance level set to {importance_level}.")
    except Exception as e:
        print(f"An error occurred while setting email importance: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# * standalone helper maintenance function to find any duplicates
def find_duplicate_email_ids_in_sources():
    """
    Finds and prints details of duplicate email_ids in the sources table.

    This function queries the database to identify email_ids that appear multiple times
    in the sources table, then prints detailed information about each duplicate.

    Args:
        None

    Returns:
        None

    Prints:
        - A message if no duplicates are found
        - For each duplicate:
            - The email_id and how many times it appears
            - Details of each duplicate entry (source_id, title, date, creation time)

    Improvements needed:
    - Return the duplicate data instead of printing it
    - Add option to write results to a file
    - Implement logging instead of print statements
    - Add error handling for specific database errors
    - Use a context manager for database connection
    - Add option to delete or merge duplicate entries
    - Parameterize the query to allow searching for specific email_ids
    - Add pagination for large result sets
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT email_id, COUNT(*) as count
            FROM sources 
            WHERE email_id IS NOT NULL
            GROUP BY email_id
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)

        duplicates = cursor.fetchall()

        if not duplicates:
            print("No duplicate email_ids found in sources table")
            return

        print("\nDuplicate email_ids in sources table:")
        print("=====================================")
        for email_id, count in duplicates:
            print(f"email_id: {email_id} appears {count} times")

            # Get details for each duplicate
            cursor.execute(
                """
                SELECT source_id, title, date_text, created_at 
                FROM sources
                WHERE email_id = ?
                ORDER BY created_at
            """,
                (email_id,),
            )

            details = cursor.fetchall()
            for source_id, title, date_text, created_at in details:
                print(f"  source_id: {source_id}")
                print(f"  title: {title}")
                print(f"  date: {date_text}")
                print(f"  created: {created_at}")
                print("  ---")
            print()

    except Exception as e:
        print(f"Error finding duplicate email_ids: {e}")

    finally:
        cursor.close()
        conn.close()


# helper called by extract_recent_emails
def extract_urls_from_email(email_body):
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
    # Regular expression pattern to match URLs
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    # Find all matches of the URL pattern in the email body
    urls = re.findall(url_pattern, email_body)

    if not urls:
        return None

    # Return a dictionary with the "urls" key and the list of URLs as the value
    return {"urls": urls}


# helper called by extract_recent_emails
def extract_to_recipients(email_body):
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
    recipients = [parseaddr(addr.strip())[1] for addr in addresses if addr.strip()]

    # Create a dictionary with the "recipients" key and the list of recipients as the value
    result = {"recipients": recipients}

    # Convert the dictionary to a JSON-formatted string
    return result


#  high level call called by extract_messages_from_important_emails
def extract_recent_emails(gmail_address, password, important_addresses, begin_date, end_date):
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
    imap_server = "imap.gmail.com"
    imap_port = 993

    # Create an IMAP4 client encrypted with SSL
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)

    try:
        # Login to the account
        mail.login(gmail_address, password)

        # Select the inbox
        mail.select("inbox")

        end_date_str = end_date.strftime("%d-%b-%Y")
        begin_date_str = begin_date.strftime("%d-%b-%Y")

        print(f"Searching for emails from {begin_date_str} to {end_date_str}")

        # Search for emails within the specified date range
        _, message_numbers = mail.search(None, f'(SINCE "{begin_date_str}" BEFORE "{end_date_str}")')

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
                        print(f"Warning: No date found for email. Skipping...")
                        continue

                    # Get the sender
                    from_header = email_body.get("From", "")
                    sender = email.utils.parseaddr(from_header)[1]

                    # Continue if sender is not in important_addresses
                    if sender not in important_addresses:
                        continue

                    print(f"Processing email from {sender}")
                    # Decode the subject
                    subject_header = email_body.get("Subject", "")
                    subject, encoding = decode_header(subject_header)[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")

                    to_recipients = extract_to_recipients(email_body)
                    # Convert to_recipients dictionary to a string
                    to_recipients_str = ""
                    if isinstance(to_recipients, dict) and "recipients" in to_recipients:
                        to_recipients_str = ", ".join(to_recipients["recipients"])

                    # Extract and store the email text
                    content = ""
                    if email_body.is_multipart():
                        for part in email_body.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    content = part.get_payload(decode=True).decode(encoding or "utf-8")
                                except UnicodeDecodeError:
                                    try:
                                        content = part.get_payload(decode=True).decode("latin-1")
                                    except UnicodeDecodeError:
                                        print(f"Failed to decode email content for {subject}")
                                        content = "Unable to decode email content"
                                break
                    else:
                        try:
                            content = email_body.get_payload(decode=True).decode(encoding or "utf-8")
                        except UnicodeDecodeError:
                            try:
                                content = email_body.get_payload(decode=True).decode("latin-1")
                            except UnicodeDecodeError:
                                print(f"Failed to decode email content for {subject}")
                                content = "Unable to decode email content"

                    urls = extract_urls_from_email(content)

                    # Extract attachment information
                    attachments = []
                    if email_body.is_multipart():
                        for part in email_body.walk():
                            if part.get_content_maintype() == "multipart":
                                continue
                            if part.get("Content-Disposition") is None:
                                continue
                            filename = part.get_filename()
                            if filename and isinstance(filename, str) and len(filename.strip()) > 0:
                                payload = part.get_payload(decode=True)
                                if payload is not None:
                                    file_size = len(payload)
                                    attachments.append({"filename": filename, "size": file_size})

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
                    conn = connect_db()
                    cursor = conn.cursor()

                    # Check if email already exists with same sender, date and content
                    try:
                        cursor.execute(
                            """
                            SELECT email_id FROM emails 
                            WHERE sender = ? 
                            AND date = ?
                            AND content = ?
                            """,
                            (email_data["sender"], email_data["date"], email_data["content"]),
                        )
                        existing_email = cursor.fetchone()

                        if existing_email:
                            print(f"Skipping duplicate email from {email_data['sender']} on {email_data['date']}")
                            cursor.close()
                            conn.close()
                            continue

                    except Exception as e:
                        print(f"Error checking for existing email: {e}")

                    try:
                        cursor.execute(
                            """
                            INSERT INTO emails (date, sender, subject, to_recipients, content, attachment_cnt, url_cnt, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                email_data["date"],
                                email_data["sender"],
                                email_data["subject"],
                                to_recipients_str,
                                email_data["content"],
                                len(email_data["attachments"]),
                                len(email_data["urls"]["urls"]),
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            ),
                        )
                        conn.commit()
                        email_id = cursor.lastrowid

                        if email_id:
                            # Write attachments to the attachments table
                            for attachment in email_data["attachments"]:
                                # Strip leading "-" or " " from the filename
                                cleaned_filename = attachment["filename"].lstrip("- ")
                                cursor.execute(
                                    """
                                INSERT INTO attachments (email_id, filename, size, created_at)
                                VALUES (?, ?, ?, ?)
                                """,
                                    (
                                        email_id,
                                        cleaned_filename,
                                        attachment["size"],
                                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    ),
                                )

                            # Write URLs to the urls table
                            for url in email_data["urls"]["urls"]:
                                cursor.execute(
                                    """
                                INSERT INTO all_email_urls (email_id, url, created_at)
                                VALUES (?, ?, ?)
                                """,
                                    (email_id, url, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                )

                        conn.commit()
                    except Exception as e:
                        print(f"Error inserting email into database: {e}")
                        conn.rollback()
                    finally:
                        cursor.close()
                        conn.close()

        return emails

    except Exception as e:
        print(f"An error occurred while extracting emails: {e}")
        return []

    finally:
        # Close the connection
        mail.logout()


if __name__ == "__main__":
    # find_duplicate_email_ids_in_sources()
    # set_email_importance("davidrogerclawson@gmail.com", 1)
    # update_important_email_status(1, 2)
    # add_important_email_address("davidrogerclawson@gmail.com", 2)

    # gmail_address = "bunnage.ray@gmail.com"
    # password = "uryj wgsu bbmk fnix"
    # begin_date = datetime(2024, 10, 30)
    # end_date = datetime(2024, 11, 6)
    # importance_level = 1
    # extracted_messages = extract_messages_from_important_emails(
    #     gmail_address, password, begin_date, end_date, importance_level
    # )

    analyze_emails_with_importance_level("2024-10-30", 19, importance_level=1)


# 11/20 commented out because it isn't called
# def show_non_get_concepts_urls():
#     """
#     Displays URLs from the 'urls' table that meet specific criteria.

#     This function queries the database for URLs where:
#     - 'is_get_concepts' is NULL or not 0
#     - 'count' is 1
#     - 'senders' includes 'dnhanscom@gmail.com'

#     It then prints the results, sorted by the most recent date.

#     Args:
#         None

#     Returns:
#         None

#     Raises:
#         Exception: If there's an error during the database operation.

#     Improvements:
#     - Add parameters for customizable search criteria (e.g., sender email, count threshold).
#     - Implement logging instead of print statements for better error tracking.
#     - Add option to export results to a file.
#     - Use parameterized queries to prevent SQL injection.
#     - Add pagination for large result sets.
#     - Consider returning the results instead of printing them for more flexibility.
#     """
#     conn = connect_db()
#     cursor = conn.cursor()

#     try:
#         cursor.execute("""
#             SELECT url, count, first_date, last_date, senders, subjects
#             FROM urls
#             WHERE (is_get_concepts IS NULL OR is_get_concepts != 0)
#             AND count = 1
#             AND senders LIKE '%dnhanscom@gmail.com%'
#             ORDER BY last_date DESC
#         """)

#         results = cursor.fetchall()

#         if not results:
#             print("No URLs found matching the criteria.")
#         else:
#             print("URLs matching the criteria (sorted by most recent date):")
#             for row in results:
#                 url, count, first_date, last_date, senders, subjects = row
#                 print(f"URL: {url}")
#                 print(f"Count: {count}")
#                 print(f"First Date: {first_date}")
#                 print(f"Last Date: {last_date}")
#                 print(f"Senders: {senders}")
#                 print(f"Subjects: {subjects}")
#                 print("-" * 50)

#     except Exception as e:
#         print(f"An error occurred: {e}")

#     finally:
#         cursor.close()
#         conn.close()

# 11/20 commented out because it isn't called
# # called by main
# def tag_emails_for_ai_processing(subjects):
#     """
#     Tags emails for AI concept processing based on their subject lines.

#     Args:
#         subjects (list): List of subject line substrings to match against email subjects

#     Returns:
#         None

#     This function:
#     1. Connects to the database
#     2. For each subject substring:
#        - Updates emails table to set is_ai_process_for_concepts=1
#        - Matches subject lines containing the substring
#     3. Prints number of emails tagged
#     4. Commits changes and closes connection

#     Improvements needed:
#     - Add input validation for subjects list
#     - Add error handling for database operations
#     - Return number of updated rows instead of printing
#     - Support batch updates for better performance
#     - Add logging instead of print statements
#     - Add option to untag emails
#     - Add transaction handling
#     - Consider using parameterized subjects list
#     """
#     conn = connect_db()
#     cursor = conn.cursor()

#     # Update emails where subject contains any of the given subjects
#     for subject in subjects:
#         cursor.execute(
#             """
#             UPDATE emails
#             SET is_ai_process_for_concepts = 1
#             WHERE subject LIKE ?
#         """,
#             ("%" + subject + "%",),
#         )

#     updated_rows = cursor.rowcount
#     print(f"Tagged {updated_rows} emails for AI processing.")

#     conn.commit()
#     conn.close()


# 11/20 commented out because not used - but it is in concepts_emails.py
# called by process_scientific_emails
# def get_processed_email_contents_ids():
#     """
#     Retrieves IDs of email contents that have already been processed for concepts.

#     Returns:
#         set: A set of email_contents_ids that have corresponding entries in the email_concepts table.
#              Returns an empty set if an error occurs.

#     This function:
#     1. Queries the email_concepts table to get distinct email_contents_ids
#     2. Returns these IDs as a set for efficient lookups
#     3. Prints the number of processed IDs found
#     4. Handles database errors gracefully

#     Improvements needed:
#     - Add optional date range filtering
#     - Support batch retrieval for large result sets
#     - Add proper logging instead of print statements
#     - Consider caching results for performance
#     - Add option to return results as list instead of set
#     - Support filtering by specific concept types
#     - Add transaction handling
#     - Consider returning success/error status along with results
#     """
#     conn = connect_db()
#     cursor = conn.cursor()

#     try:
#         cursor.execute("""
#             SELECT DISTINCT email_contents_id
#             FROM email_concepts
#         """)
#         processed_ids = set(row[0] for row in cursor.fetchall())
#         print(f"Found {len(processed_ids)} already processed email_contents_ids.")
#         return processed_ids
#     except Exception as e:
#         print(f"Error fetching processed email_contents_ids: {e}")
#         return set()
#     finally:
#         cursor.close()
#         conn.close()
