import fitz
from app.core.logger import service_logger
import traceback
import os
from pathlib import Path

def process_resume_file(file_path: str) -> dict:
    """
    Process a resume file and extract its text content
    
    Args:
        file_path: Path to the resume file
    
    Returns:
        dict: Dictionary containing processed content with 'content' key
    """
    service_logger.info(f"Processing resume file: {file_path}")
    
    try:
        # Extract text from the file
        extracted_text = extract_text_from_pdf(file_path)
        
        if not extracted_text:
            service_logger.warning("No text content extracted from resume file")
            return {
                "content": "",
                "status": "empty",
                "message": "No text content found in the file"
            }
        
        service_logger.info(f"Successfully processed resume file with {len(extracted_text)} characters")
        
        return {
            "content": extracted_text,
            "status": "success",
            "message": f"Successfully extracted {len(extracted_text)} characters from resume",
            "file_path": file_path
        }
        
    except Exception as e:
        service_logger.error(f"Error processing resume file {file_path}: {str(e)}")
        service_logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "content": "",
            "status": "error",
            "message": f"Error processing file: {str(e)}",
            "file_path": file_path
        }

import os
import traceback
from pathlib import Path
import fitz  # PyMuPDF
import io

# Ensure service_logger is defined; you can replace with `print` if needed
import logging
service_logger = logging.getLogger("pdf_extractor")


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract enriched text content from a PDF file with embedded hyperlinks.

    Args:
        file_path: Path to the PDF file or file-like object

    Returns:
        str: Extracted and enriched text content, empty string on failure
    """
    service_logger.info(f"Starting PDF text extraction from: {file_path}")

    try:
        # Input validation
        if not file_path:
            service_logger.error("No file path provided for PDF extraction")
            return ""

        # Handle file-like objects (UploadFile)
        if hasattr(file_path, 'read'):
            service_logger.info("Processing file-like object (uploaded file)")
            try:
                file_content = file_path.read()
                if hasattr(file_content, "__await__"):  # for async file.read()
                    import asyncio
                    file_content = asyncio.run(file_content)

                service_logger.debug(f"Read {len(file_content)} bytes from uploaded file")
                doc = fitz.open(stream=file_content, filetype="pdf")
                service_logger.info(f"Successfully opened PDF with {len(doc)} pages")
            except Exception as e:
                service_logger.error(f"Failed to read from file-like object: {str(e)}")
                service_logger.error(f"Traceback: {traceback.format_exc()}")
                return ""

        # Handle file paths
        elif isinstance(file_path, (str, Path)):
            file_path = str(file_path)
            service_logger.info(f"Processing file path: {file_path}")
            if not os.path.exists(file_path):
                service_logger.error(f"File does not exist: {file_path}")
                return ""

            if not file_path.lower().endswith('.pdf'):
                service_logger.warning(f"File does not have .pdf extension: {file_path}")

            file_size = os.path.getsize(file_path)
            service_logger.debug(f"File size: {file_size} bytes")

            try:
                doc = fitz.open(file_path)
                service_logger.info(f"Successfully opened PDF with {len(doc)} pages")
            except Exception as e:
                service_logger.error(f"Failed to open PDF file {file_path}: {str(e)}")
                service_logger.error(f"Traceback: {traceback.format_exc()}")
                return ""

        else:
            service_logger.error(f"Invalid file_path type: {type(file_path)}")
            return ""

        # Extract and enrich text from each page
        text = ""
        total_pages = len(doc)
        service_logger.info(f"Extracting text and links from {total_pages} pages")

        for page_num, page in enumerate(doc, 1):
            try:
                text_blocks = page.get_text("dict")["blocks"]
                links = page.get_links()
                enriched_text = ""

                for block in text_blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            span_text = span["text"]
                            span_bbox = span["bbox"]
                            matched_uri = None

                            for link in links:
                                if "uri" in link:
                                    link_bbox = link["from"]
                                    if (
                                        span_bbox[0] < link_bbox[2]
                                        and span_bbox[2] > link_bbox[0]
                                        and span_bbox[1] < link_bbox[3]
                                        and span_bbox[3] > link_bbox[1]
                                    ):
                                        matched_uri = link["uri"]
                                        break

                            if matched_uri:
                                enriched_text += f"{span_text} ({matched_uri})"
                            else:
                                enriched_text += span_text
                        enriched_text += "\n"
                    enriched_text += "\n"

                text += enriched_text
                service_logger.debug(f"Enriched text length from page {page_num}: {len(enriched_text)}")

            except Exception as e:
                service_logger.error(f"Failed to enrich text from page {page_num}: {str(e)}")
                continue

        try:
            doc.close()
            service_logger.debug("PDF document closed successfully")
        except Exception as e:
            service_logger.warning(f"Failed to close PDF document: {str(e)}")

        extracted_text = text.strip()
        if not extracted_text:
            service_logger.warning("No text extracted from PDF")
        else:
            service_logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
            service_logger.debug(f"First 100 characters: {extracted_text[:100]}")

        return extracted_text

    except Exception as e:
        service_logger.error(f"Unexpected error during PDF text extraction: {str(e)}")
        service_logger.error(f"Traceback: {traceback.format_exc()}")
        return ""
