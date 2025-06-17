import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
from datetime import datetime
from src.settings.logging_config import configure_logging
import logging
import tempfile

configure_logging()
logger = logging.getLogger(__name__)



def get_temp_file_path(file_type: str) -> str:
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, f'job_items_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{file_type}')


def generate_excel_report(job_items) -> str:
    try:
        data = []
        for job in job_items:
            data.append({
                'ID': job.id,
                'URL': job.url,
                'Status': job.status,
                'Priority': job.priority,
                'Created Date': job.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        
        df = pd.DataFrame(data)
        filename = get_temp_file_path('xlsx')

        writer = pd.ExcelWriter(filename, engine='openpyxl')
        df.to_excel(writer, sheet_name='Job Applications', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Job Applications']
        
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
        
        writer.close()
        return filename
        
    except Exception as e:
        logger.error(f"Error creating Excel file: {str(e)}")
        raise


def generate_pdf_report(job_items) -> str:
    try:
        filename = get_temp_file_path('pdf')

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER
        ))
        
        # Add custom style for URLs
        styles.add(ParagraphStyle(
            name='URLStyle',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
            wordWrap='CJK'  # Better word wrapping for URLs
        ))
        
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elements = []
        
        # Title
        title = Paragraph(f"Job Applications Report", styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 30))
        
        # Table
        data = [['ID', 'URL (Display)', 'Status', 'Priority', 'Created Date']]
        for job in job_items:
            full_url = job.url if job.url else "N/A"
            # Create a clickable URL with proper wrapping
            display_url = Paragraph(
                f'<link href="{full_url}">{full_url}</link>',
                style=styles['URLStyle']
            )
            
            data.append([
                str(job.id),
                display_url,
                job.status,
                job.priority,
                job.created_at.strftime('%Y-%m-%d %H:%M'),
            ])
        
        # Calculate column widths - give more space to URL column
        available_width = doc.width
        col_widths = [
            0.8*inch,  # ID
            available_width * 0.5,  # URL - 50% of available width
            1.2*inch,  # Status
            1*inch,    # Priority
            1.5*inch   # Created Date
        ]
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # URL column specific styles
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Left align URLs
            ('LEFTPADDING', (1, 1), (1, -1), 10),  # More padding for URLs
            ('RIGHTPADDING', (1, 1), (1, -1), 10),
            ('WORDWRAP', (1, 1), (1, -1), True),  # Enable word wrap for URL column
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        return filename
        
    except Exception as e:
        logger.error(f"Error creating PDF file: {str(e)}")
        raise


def pack_job_analyse_report(data: str):
    try:
        file_path = get_temp_file_path("txt")
        with open(file_path, "w") as f:
            f.write(data)
        return file_path
    except Exception as ex:
        logger.error(f"Error creating job analysis report: {str(ex)}")
        raise

    

