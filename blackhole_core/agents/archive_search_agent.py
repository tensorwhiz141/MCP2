# blackhole_core.agents.archive_search_agent.py

import pandas as pd  # For CSV reading and data manipulation
from datetime import datetime, timezone  # For timestamping
from bson import ObjectId  # For MongoDB document ID support
from blackhole_core.data_source.mongodb import get_mongo_client  # Mongo client connection
import os  # For file system handling
from rapidfuzz import fuzz  # For fuzzy string matching


class ArchiveSearchAgent:
    """
    Agent that searches an archived CSV file using approximate string matching (fuzzy logic).
    Can optionally interface with MongoDB for future expansion.
    """

    def __init__(self, memory=None, source=None):
        """
        Initialize the ArchiveSearchAgent.

        Args:
            memory (optional): Not currently used but may hold past context.
            source (optional): Defaults to "csv", could support other sources later.
        """
        self.memory = memory
        self.source = source or "csv"

        # Connect to MongoDB (used optionally, not critical in CSV mode)
        self.client = get_mongo_client()
        self.db = self.client["blackhole_db"]

        # Dynamically resolve CSV path for archived documents
        self.archive_path = os.path.join(
            os.path.dirname(__file__), '..', 'data_source', 'sample_archive.csv'
        )

        # If the archive is missing, raise an exception
        if not os.path.exists(self.archive_path):
            raise FileNotFoundError(f"Sample archive not found at {self.archive_path}")

    def plan(self, query):
        """
        Main search function for matching text against archive records using fuzzy matching.

        🔍 Input: `query['document_text']` – the user-provided content to match.
        ⚙️ Processing: Loads archive CSV, computes fuzzy match scores.
        🧾 Output: List of matched rows with match score and matching column.

        Args:
            query (dict): Must contain a 'document_text' key.

        Returns:
            dict: A dictionary with matching results and metadata.
        """
        # 🔍 INPUT: Extract document_text from the query
        document_text = query.get('document_text', "")
        if not document_text:
            return {"error": "No document_text provided."}

        # Load the archive CSV file into a DataFrame
        df = pd.read_csv(self.archive_path)

        matches = []
        threshold = 60  # Minimum fuzzy match score (0-100)

        # Loop through each row in the archive
        for _, row in df.iterrows():
            # Loop through each column in the row
            for col, value in row.items():
                # Skip empty or null values
                if pd.isna(value) or str(value).strip() == "":
                    continue

                # Normalize to lowercase for case-insensitive comparison
                value_str = str(value).lower()
                doc_text_lower = document_text.lower()

                # ⚙️ PROCESSING: Calculate fuzzy match scores
                token_ratio = fuzz.token_set_ratio(doc_text_lower, value_str)
                partial_ratio = fuzz.partial_ratio(doc_text_lower, value_str)

                # Choose the best similarity score
                similarity = max(token_ratio, partial_ratio)

                # If the score is above the threshold, consider it a match
                if similarity >= threshold:
                    match_entry = {
                        "match_score": similarity,
                        "matched_on": col,
                        "matched_value": value,
                        **row.to_dict()
                    }

                    # Avoid duplicate entries for the same title
                    if not any(m.get('title') == row['title'] for m in matches):
                        matches.append(match_entry)
                    break  # Stop checking other columns for this row once matched

        # 🧾 OUTPUT: Prepare structured output with metadata
        result = {
            "agent": "ArchiveSearchAgent",
            "input": query,
            "output": matches if matches else "No matches found.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "source_file": self.archive_path
            }
        }

        return result

    def run(self, query):
        """
        Alias to `plan()` method. Enables compatibility with pipelines or workflows.

        Args:
            query (dict): Query with 'document_text'.

        Returns:
            dict: Same result as plan().
        """
        return self.plan(query)
