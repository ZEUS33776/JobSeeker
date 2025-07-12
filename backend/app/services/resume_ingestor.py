import fitz
from app.core.logger import service_logger
import traceback
import os
from pathlib import Path

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from PDF file
    
    Args:
        file_path: Path to the PDF file or file-like object
    
    Returns:
        str: Extracted text content, empty string on failure
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
                # Read the file content
                file_content = file_path.read()
                service_logger.debug(f"Read {len(file_content)} bytes from uploaded file")
                
                # Open PDF from bytes
                doc = fitz.open(stream=file_content, filetype="pdf")
                service_logger.info(f"Successfully opened PDF document with {len(doc)} pages")
                
            except Exception as e:
                service_logger.error(f"Failed to read from file-like object: {str(e)}")
                service_logger.error(f"Traceback: {traceback.format_exc()}")
                return ""
        
        # Handle file paths
        elif isinstance(file_path, (str, Path)):
            file_path = str(file_path)
            service_logger.info(f"Processing file path: {file_path}")
            
            # Validate file exists
            if not os.path.exists(file_path):
                service_logger.error(f"File does not exist: {file_path}")
                return ""
            
            # Validate file extension
            if not file_path.lower().endswith('.pdf'):
                service_logger.warning(f"File does not have .pdf extension: {file_path}")
            
            # Get file size for logging
            file_size = os.path.getsize(file_path)
            service_logger.debug(f"File size: {file_size} bytes")
            
            try:
                # Open PDF file
                doc = fitz.open(file_path)
                service_logger.info(f"Successfully opened PDF document with {len(doc)} pages")
                
            except Exception as e:
                service_logger.error(f"Failed to open PDF file {file_path}: {str(e)}")
                service_logger.error(f"Traceback: {traceback.format_exc()}")
                return ""
        
        else:
            service_logger.error(f"Invalid file_path type: {type(file_path)}")
            return ""
        
        # Extract text from all pages
        text = ""
        total_pages = len(doc)
        service_logger.info(f"Extracting text from {total_pages} pages")
        
        for page_num, page in enumerate(doc, 1):
            try:
                page_text = page.get_text()
                text += page_text
                service_logger.debug(f"Extracted {len(page_text)} characters from page {page_num}")
                
            except Exception as e:
                service_logger.error(f"Failed to extract text from page {page_num}: {str(e)}")
                service_logger.warning(f"Continuing with remaining pages...")
                continue
        
        # Close the document
        try:
            doc.close()
            service_logger.debug("PDF document closed successfully")
        except Exception as e:
            service_logger.warning(f"Failed to close PDF document: {str(e)}")
        
        # Final text processing
        extracted_text = text.strip()
        text_length = len(extracted_text)
        
        if text_length == 0:
            service_logger.warning("No text content extracted from PDF")
        else:
            service_logger.info(f"Successfully extracted {text_length} characters from PDF")
            service_logger.debug(f"First 100 characters: {extracted_text[:100]}")
        
        return extracted_text
        
    except fitz.FileDataError as fde:
        service_logger.error(f"PDF file data error: {str(fde)}")
        service_logger.error("The file might be corrupted or not a valid PDF")
        service_logger.error(f"Traceback: {traceback.format_exc()}")
        return ""
    
    except fitz.FileNotFoundError as fnfe:
        service_logger.error(f"PDF file not found: {str(fnfe)}")
        service_logger.error(f"Traceback: {traceback.format_exc()}")
        return ""
    
    except MemoryError as me:
        service_logger.error(f"Memory error while processing PDF: {str(me)}")
        service_logger.error("PDF file might be too large")
        service_logger.error(f"Traceback: {traceback.format_exc()}")
        return ""
    
    except Exception as e:
        service_logger.error(f"Unexpected error during PDF text extraction: {str(e)}")
        service_logger.error(f"Error type: {type(e).__name__}")
        service_logger.error(f"File path: {file_path}")
        service_logger.error(f"Traceback: {traceback.format_exc()}")
        return ""


