"""
Export functionality for results (CSV and PDF).
"""

import csv
import io
from datetime import datetime
from typing import Dict, List

import streamlit as st


def export_results_csv(results: List[Dict], job_description: str = "") -> bytes:
    """
    Export results to CSV format.
    
    Args:
        results: List of result dictionaries
        job_description: Job description text
    
    Returns:
        CSV file as bytes
    """
    output = io.StringIO()
    
    if not results:
        return output.getvalue().encode()
    
    # Prepare header
    fieldnames = [
        "Rank",
        "Filename",
        "Overall Score",
        "TF-IDF Score",
        "Entity Score",
        "Matched Skills",
        "Matched Keywords",
        "Match Quality",
        "Export Timestamp",
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    # Write results
    for idx, result in enumerate(results, 1):
        overall_score = result.get("overall_score", 0)
        
        # Determine match quality
        if overall_score >= 0.8:
            quality = "High"
        elif overall_score >= 0.6:
            quality = "Medium"
        else:
            quality = "Low"
        
        writer.writerow({
            "Rank": idx,
            "Filename": result.get("filename", ""),
            "Overall Score": f"{overall_score:.2%}",
            "TF-IDF Score": f"{result.get('tfidf_score', 0):.2%}",
            "Entity Score": f"{result.get('entity_score', 0):.2%}",
            "Matched Skills": "; ".join(result.get("matched_skills", [])),
            "Matched Keywords": "; ".join(result.get("matched_keywords", [])),
            "Match Quality": quality,
            "Export Timestamp": datetime.now().isoformat(),
        })
    
    return output.getvalue().encode()


def export_results_pdf(results: List[Dict], job_description: str = "") -> bytes:
    """
    Export results to PDF format.
    
    Args:
        results: List of result dictionaries
        job_description: Job description text
    
    Returns:
        PDF file as bytes
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
    except ImportError:
        st.error("❌ PDF export requires 'reportlab'. Install with: pip install reportlab")
        return b""
    
    # Create PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1f77b4"),
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("Resume Screening Results", title_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Metadata
    meta_style = styles["Normal"]
    elements.append(Paragraph(f"<b>Export Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
    elements.append(Paragraph(f"<b>Total Resumes:</b> {len(results)}", meta_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Results table
    table_data = [
        ["Rank", "Filename", "Overall Score", "TF-IDF", "Entity", "Match Quality"],
    ]
    
    for idx, result in enumerate(results, 1):
        overall_score = result.get("overall_score", 0)
        
        if overall_score >= 0.8:
            quality = "High"
        elif overall_score >= 0.6:
            quality = "Medium"
        else:
            quality = "Low"
        
        table_data.append([
            str(idx),
            result.get("filename", "")[:30],
            f"{overall_score:.1%}",
            f"{result.get('tfidf_score', 0):.1%}",
            f"{result.get('entity_score', 0):.1%}",
            quality,
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def show_export_options(results: List[Dict], job_description: str = "") -> None:
    """
    Display export buttons for results.
    
    Args:
        results: List of result dictionaries
        job_description: Job description text
    """
    if not results:
        return
    
    st.markdown("---")
    st.markdown("### 📥 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = export_results_csv(results, job_description)
        st.download_button(
            label="📊 Download as CSV",
            data=csv_data,
            file_name=f"resume_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    
    with col2:
        pdf_data = export_results_pdf(results, job_description)
        if pdf_data:
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_data,
                file_name=f"resume_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
