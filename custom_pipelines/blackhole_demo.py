# pipelines/blackhole_demo.py
import datetime
from utils.multimodal.pdf_reader import read_pdf # You need to implement this
from integration.llm_router import run_with_model [cite: 10]
from utils.logger import log_task [cite: 10]
# For simplicity, directly using agent here. In reality, call mcp_bridge endpoint.
from registry.agent_registry import AGENT_REGISTRY

def run_demo_pipeline(pdf_path, llm_model_name="gemini"):
    print(f"--- Starting Blackhole Demo Pipeline for {pdf_path} ---")
    full_flow_status = "SUCCESS"
    final_output = {}

    # Step 1: Extract PDF [cite: 9]
    pdf_content = ""
    try:
        pdf_content = read_pdf(pdf_path)
        log_task("PDF_Reader", pdf_path, "PDF extraction successful", "SUCCESS")
        print("PDF Content Extracted.")
    except Exception as e:
        log_task("PDF_Reader", pdf_path, f"PDF extraction failed: {e}", "FAILED")
        full_flow_status = "FAILED"
        print(f"Error extracting PDF: {e}")
        return

    # Step 2: Pass to ArchiveSearchAgent [cite: 9]
    archive_agent_name = "ArchiveSearchAgent"
    archive_agent = AGENT_REGISTRY.get(archive_agent_name)
    archive_output = {}
    if archive_agent:
        try:
            archive_output = archive_agent.run(pdf_content)
            log_task(archive_agent_name, pdf_content, archive_output, "SUCCESS") [cite: 10]
            print("ArchiveSearchAgent completed.")
        except Exception as e:
            log_task(archive_agent_name, pdf_content, f"Agent run failed: {e}", "FAILED") [cite: 10]
            full_flow_status = "FAILED"
            print(f"Error running ArchiveSearchAgent: {e}")
    else:
        log_task(archive_agent_name, pdf_content, "Agent not found", "FAILED") [cite: 10]
        full_flow_status = "FAILED"
        print(f"Agent '{archive_agent_name}' not found.")
        return

    # Step 3: Pass that to LLM via llm_router.py 
    llm_input = archive_output # Assuming archive_output is text
    llm_output = {}
    try:
        llm_output = run_with_model(llm_model_name, llm_input) [cite: 10]
        log_task("LLM_Router", llm_input, llm_output, "SUCCESS") [cite: 10]
        print(f"{llm_model_name} processed.")
        final_output = {"agent_result": archive_output, "llm_result": llm_output}
    except Exception as e:
        log_task("LLM_Router", llm_input, f"LLM run failed: {e}", "FAILED") [cite: 10]
        full_flow_status = "FAILED"
        print(f"Error running LLM: {e}")

    # Log entire flow with timestamps (each step already logged, but overall status too)
    log_task("Full_Pipeline", pdf_path, final_output, full_flow_status, datetime.datetime.now()) [cite: 10]
    print(f"--- Blackhole Demo Pipeline Finished with status: {full_flow_status} ---")
    return final_output

# Example usage:
if __name__ == "__main__":
    # Create a dummy PDF reader for testing
    # utils/multimodal/pdf_reader.py
    # def read_pdf(file_path):
    #     print(f"Reading dummy PDF from {file_path}")
    #     return "This is dummy content from the PDF for testing the pipeline."

    # Ensure you have a dummy PDF file or mock the read_pdf function
    dummy_pdf_path = "path/to/your/dummy.pdf" # Replace with actual path or mock

    # Call the pipeline
    result = run_demo_pipeline(dummy_pdf_path, llm_model_name="gemini")
    print("\nPipeline Result:", result)