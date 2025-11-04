#!/usr/bin/env python3
"""
Script to analyze RAG design documents and compare with current implementation
"""
import PyPDF2
from pathlib import Path
import json
import re

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error reading {pdf_path}: {str(e)}"

def extract_key_concepts(text):
    """Extract key concepts and design patterns from text"""
    concepts = {
        "modular_rag": [],
        "agentic_design": [],
        "architectures": [],
        "workflows": [],
        "memory_systems": [],
        "multi_agent": []
    }

    # Search for key patterns
    if "modular rag" in text.lower():
        concepts["modular_rag"].append("Mentioned Modular RAG")
    if "agentic" in text.lower():
        concepts["agentic_design"].append("Agentic Design Pattern")
    if "multi-agent" in text.lower():
        concepts["multi_agent"].append("Multi-Agent System")
    if "memory" in text.lower() and "agent" in text.lower():
        concepts["memory_systems"].append("Agent Memory System")
    if "workflow" in text.lower():
        concepts["workflows"].append("Workflow Pattern")
    if "architecture" in text.lower():
        concepts["architectures"].append("Architecture Pattern")

    return concepts

def analyze_pdf_documents():
    """Main analysis function"""
    rag_designer_dir = Path("docs/rag-designer")
    pdf_files = sorted(rag_designer_dir.glob("*.pdf"))

    print("="*80)
    print("RAG DESIGN DOCUMENT ANALYSIS")
    print("="*80)
    print(f"\nFound {len(pdf_files)} PDF documents\n")

    all_concepts = {
        "modular_rag": set(),
        "agentic_design": set(),
        "architectures": set(),
        "workflows": set(),
        "memory_systems": set(),
        "multi_agent": set()
    }

    document_summaries = []

    for pdf_file in pdf_files:
        print(f"\n{'='*80}")
        print(f"DOCUMENT: {pdf_file.name}")
        print(f"{'='*80}")

        text = extract_pdf_text(pdf_file)

        # Extract preview (first 2000 chars)
        preview = text[:2000] if len(text) > 2000 else text

        # Extract key sections
        lines = text.split('\n')
        headings = [line for line in lines if line.isupper() or (len(line) > 0 and len(line) < 100 and ':' not in line)]

        print(f"\nDocument Length: {len(text)} characters")
        print(f"\nKey Preview:")
        print("-" * 80)
        print(preview)
        print("-" * 80)

        # Extract concepts
        concepts = extract_key_concepts(text)

        # Store document summary
        document_summaries.append({
            "filename": pdf_file.name,
            "length": len(text),
            "preview": preview,
            "concepts": concepts
        })

        # Aggregate concepts
        for key, values in concepts.items():
            if values:
                all_concepts[key].add(pdf_file.name)

    # Print summary
    print("\n\n")
    print("="*80)
    print("AGGREGATED CONCEPTS ACROSS ALL DOCUMENTS")
    print("="*80)

    for concept_type, documents in all_concepts.items():
        if documents:
            print(f"\n{concept_type.upper().replace('_', ' ')}:")
            for doc in sorted(documents):
                print(f"  - {doc}")

    # Save to JSON for further analysis
    with open("rag_design_analysis.json", "w") as f:
        json.dump({
            "total_documents": len(pdf_files),
            "document_summaries": document_summaries,
            "aggregated_concepts": {k: list(v) for k, v in all_concepts.items()}
        }, f, indent=2)

    print("\n\n")
    print("="*80)
    print("Analysis saved to: rag_design_analysis.json")
    print("="*80)

if __name__ == "__main__":
    analyze_pdf_documents()
