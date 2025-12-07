"""
Enhanced PDF Generator for NEET PG Timetable
Creates attractive, professionally styled PDFs with the same structure as the old system
"""

from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import random

# Motivational quotes for PDF pages
MOTIVATIONAL_QUOTES = [
    "Believe you can and you're halfway there.",
    "Your only limit is your mind.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Success doesn't just find you. You have to go out and get it.",
    "The harder you work for something, the greater you'll feel when you achieve it.",
    "Dream bigger. Do bigger.",
    "Don't stop when you're tired. Stop when you're done.",
    "Wake up with determination. Go to bed with satisfaction.",
    "Do something today that your future self will thank you for.",
    "Little things make big days.",
    "It's going to be hard, but hard does not mean impossible.",
    "Don't wait for opportunity. Create it.",
    "Sometimes we're tested not to show our weaknesses, but to discover our strengths.",
    "The key to success is to focus on goals, not obstacles.",
    "Dream it. Believe it. Build it.",
    "Motivation is what gets you started. Habit is what keeps you going.",
    "A little progress each day adds up to big results.",
    "There is no substitute for hard work.",
    "What you do today can improve all your tomorrows.",
    "Set a goal that makes you want to jump out of bed in the morning.",
    "You don't have to be great to start, but you have to start to be great.",
    "Success is what happens after you have survived all your mistakes.",
    "Reviewing is the key to retention.",
    "Consistency is the only cheat code.",
    "The pain you feel today will be the strength you feel tomorrow.",
    "Focus on the process, not just the outcome.",
    "Every pro was once an amateur.",
    "Your potential is endless."
]


class FooterCanvas(canvas.Canvas):
    """Custom canvas to add page numbers and quotes"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            self.draw_page_footer(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_page_footer(self, page_num, page_count):
        """Draw page number and quote in footer"""
        page_width = landscape(A4)[0]
        
        # Page number on the right
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor('#64748b'))
        self.drawRightString(
            page_width - 0.5*inch,
            0.4*inch,
            f"Page {page_num} of {page_count}"
        )
        
        # Quote centered (skip cover page)
        if page_num > 1:
            quote = MOTIVATIONAL_QUOTES[(page_num - 2) % len(MOTIVATIONAL_QUOTES)]
            self.setFont("Helvetica-Oblique", 10)
            self.setFillColor(colors.HexColor('#64748b'))
            # Center the quote
            self.drawCentredString(
                page_width / 2,
                0.4*inch,
                f'"{quote}"'
            )


def generate_pdf(main_data, rev_data, stats, time_cols):
    """
    Generate enhanced PDF with attractive styling
    
    Args:
        main_data: dict with 'days' and 'summary' for main timetable
        rev_data: dict with 'days' and 'summary' for revision timetable
        stats: dict with 'total_days', 'main_days', 'rev_days'
        time_cols: list of time slot strings
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        topMargin=0.6*inch,
        bottomMargin=0.6*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles with enhanced aesthetics
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=20,
        spaceBefore=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=34
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=15,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderPadding=8,
        borderColor=colors.HexColor('#3b82f6'),
        borderRadius=4,
        backColor=colors.HexColor('#eff6ff')
    )
    
    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#059669'),
        spaceAfter=12,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    quote_style = ParagraphStyle(
        'Quote',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        spaceAfter=10,
        spaceBefore=10
    )
    
    # Cover Page
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("NEET PG PREPARATION SCHEDULE", title_style))
    elements.append(Paragraph("Personalized Study Timetable", subtitle_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Stats summary on cover
    stats_data = [
        ['Study Period Overview', ''],
        ['Total Duration:', f"{stats['total_days']} Days"],
        ['Main Phase:', f"{stats['main_days']} Days"],
        ['Revision Phase:', f"{stats['rev_days']} Days"]
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white]),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e40af'))
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph(f'"{random.choice(MOTIVATIONAL_QUOTES)}"', quote_style))
    elements.append(PageBreak())
    
    # Main Timetable
    if main_data['days']:
        elements.append(Paragraph("Part I: Main Timetable", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Main schedule table - paginated
        rows_per_page = 12
        for i in range(0, len(main_data['days']), rows_per_page):
            batch = main_data['days'][i:i+rows_per_page]
            
            # Create table data
            table_data = [['Date (Day)'] + time_cols]
            
            for day in batch:
                row = [Paragraph(day['date_display'], ParagraphStyle('DateCell', fontSize=8, fontName='Helvetica-Bold'))]
                
                if day.get('is_special'):
                    # Special day - merge cells
                    cell_text = day['special_label']
                    row.append(Paragraph(cell_text, ParagraphStyle('Special', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER)))
                else:
                    # Normal day - show subjects
                    for time_slot in time_cols:
                        subject = day['slots_map'].get(time_slot, '-')
                        row.append(Paragraph(subject, ParagraphStyle('Cell', fontSize=7, leading=9)))
                
                table_data.append(row)
            
            # Calculate column widths
            date_col_width = 1.2*inch
            remaining_width = landscape(A4)[0] - 1*inch - date_col_width
            slot_col_width = remaining_width / len(time_cols)
            col_widths = [date_col_width] + [slot_col_width] * len(time_cols)
            
            schedule_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Enhanced table styling
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#1e40af')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
            ]
            
            # Handle special days (merged cells)
            for row_idx, day in enumerate(batch, 1):
                if day.get('is_special'):
                    table_style.append(('SPAN', (1, row_idx), (-1, row_idx)))
                    if 'Grand Test' in day.get('special_label', ''):
                        table_style.append(('BACKGROUND', (1, row_idx), (-1, row_idx), colors.HexColor('#fee2e2')))
                        table_style.append(('TEXTCOLOR', (1, row_idx), (-1, row_idx), colors.HexColor('#991b1b')))
                    else:
                        table_style.append(('BACKGROUND', (1, row_idx), (-1, row_idx), colors.HexColor('#d1fae5')))
                        table_style.append(('TEXTCOLOR', (1, row_idx), (-1, row_idx), colors.HexColor('#065f46')))
            
            schedule_table.setStyle(TableStyle(table_style))
            elements.append(schedule_table)
            
            if i + rows_per_page < len(main_data['days']):
                elements.append(PageBreak())
        
        # Main summary
        elements.append(PageBreak())
        elements.append(Paragraph("Main Phase - Subject Breakdown", subheading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        summary_data = [['Subject', 'Total Hours']]
        for subject, hours in main_data['summary'].items():
            summary_data.append([subject, str(hours)])
        
        summary_table = Table(summary_data, colWidths=[4*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')])
        ]))
        
        elements.append(summary_table)
        elements.append(PageBreak())
    
    # Revision Timetable
    if rev_data['days']:
        elements.append(Paragraph("Part II: Revision Timetable", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Revision schedule table - paginated
        rows_per_page = 12
        for i in range(0, len(rev_data['days']), rows_per_page):
            batch = rev_data['days'][i:i+rows_per_page]
            
            table_data = [['Date (Day)'] + time_cols]
            
            for day in batch:
                row = [Paragraph(day['date_display'], ParagraphStyle('DateCell', fontSize=8, fontName='Helvetica-Bold'))]
                
                if day.get('is_special'):
                    cell_text = day['special_label']
                    row.append(Paragraph(cell_text, ParagraphStyle('Special', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER)))
                else:
                    for time_slot in time_cols:
                        subject = day['slots_map'].get(time_slot, '-')
                        row.append(Paragraph(subject, ParagraphStyle('Cell', fontSize=7, leading=9)))
                
                table_data.append(row)
            
            date_col_width = 1.2*inch
            remaining_width = landscape(A4)[0] - 1*inch - date_col_width
            slot_col_width = remaining_width / len(time_cols)
            col_widths = [date_col_width] + [slot_col_width] * len(time_cols)
            
            schedule_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#059669')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')])
            ]
            
            for row_idx, day in enumerate(batch, 1):
                if day.get('is_special'):
                    table_style.append(('SPAN', (1, row_idx), (-1, row_idx)))
                    if 'Grand Test' in day.get('special_label', ''):
                        table_style.append(('BACKGROUND', (1, row_idx), (-1, row_idx), colors.HexColor('#fee2e2')))
                        table_style.append(('TEXTCOLOR', (1, row_idx), (-1, row_idx), colors.HexColor('#991b1b')))
                    else:
                        table_style.append(('BACKGROUND', (1, row_idx), (-1, row_idx), colors.HexColor('#d1fae5')))
                        table_style.append(('TEXTCOLOR', (1, row_idx), (-1, row_idx), colors.HexColor('#065f46')))
            
            schedule_table.setStyle(TableStyle(table_style))
            elements.append(schedule_table)
            
            if i + rows_per_page < len(rev_data['days']):
                elements.append(PageBreak())
        
        # Revision summary
        elements.append(PageBreak())
        elements.append(Paragraph("Revision Phase - Subject Breakdown", subheading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        summary_data = [['Subject', 'Total Hours']]
        for subject, hours in rev_data['summary'].items():
            summary_data.append([subject, str(hours)])
        
        summary_table = Table(summary_data, colWidths=[4*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecfdf5')])
        ]))
        
        elements.append(summary_table)
    
    # Build PDF
    doc.build(elements, canvasmaker=FooterCanvas)
    buffer.seek(0)
    
    return buffer
