"""
Professional PDF Report Generator for KIA Lead Conversion Intelligence
Generates a styled, publication-ready A4 PDF document using ReportLab.
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# ---------------------------------------------------------------------------
# Numbered Canvas for Dynamic "Page X of Y" and Running Headers
# ---------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Suppress running header on Page 1 (Cover / Header)
        if self._pageNumber > 1:
            # Running Header
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#0A1128"))
            self.drawString(40, 805, "KIA BHUBANESWAR DEALERSHIP")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(185, 805, "|  Lead Conversion Intelligence & AI Copilot — Practical Report")
            
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(40, 798, 555, 798)

        # Running Footer (on all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 42, 555, 42)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(40, 30, "Confidential — Prepared for Dealership Executive Leadership & Technical Evaluation")

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 30, page_str)
        
        self.restoreState()


# ---------------------------------------------------------------------------
# Main Report Builder
# ---------------------------------------------------------------------------
def generate_pdf(output_path="docs/practical_project_report.pdf"):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Palette
    KIA_RED = colors.HexColor("#EA0029")
    KIA_NAVY = colors.HexColor("#0A1128")
    KIA_DARK = colors.HexColor("#0F172A")
    TEXT_MUTED = colors.HexColor("#475569")
    BG_LIGHT = colors.HexColor("#F8FAFC")
    BORDER_LIGHT = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=KIA_NAVY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=KIA_RED,
        spaceAfter=12
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=KIA_NAVY
    )

    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=TEXT_MUTED
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=KIA_NAVY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=KIA_RED,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=KIA_DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=KIA_DARK,
        leftIndent=12,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=KIA_NAVY
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.white,
        alignment=1 # Center
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=KIA_DARK,
        alignment=0 # Left
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=KIA_DARK,
        alignment=1 # Center
    )

    table_cell_bold_center = ParagraphStyle(
        'TableCellBoldCenter',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=KIA_NAVY,
        alignment=1 # Center
    )

    story = []

    # -----------------------------------------------------------------------
    # Document Header Banner
    # -----------------------------------------------------------------------
    story.append(Paragraph("PRACTICAL PROJECT REPORT", subtitle_style))
    story.append(Paragraph("Automotive CRM Lead Conversion Intelligence, Predictive ML & AI Copilot", title_style))
    story.append(Spacer(1, 4))
    
    # Metadata Block Table
    meta_data = [
        [
            Paragraph("<b>Entity:</b>", meta_label_style),
            Paragraph("Bhubaneswar Kia Dealership", meta_val_style),
            Paragraph("<b>Author / Lead:</b>", meta_label_style),
            Paragraph("Anmol Kumar (<code>Anmolkr001</code>)", meta_val_style)
        ],
        [
            Paragraph("<b>Dataset Scope:</b>", meta_label_style),
            Paragraph("6,967 Validated Leads (Jan–Jun 2026)", meta_val_style),
            Paragraph("<b>Live Vercel URL:</b>", meta_label_style),
            Paragraph("kia-data-analytics.vercel.app", meta_val_style)
        ],
        [
            Paragraph("<b>Core Stack:</b>", meta_label_style),
            Paragraph("React 19, FastAPI, XGBoost, LangChain", meta_val_style),
            Paragraph("<b>GitHub Repo:</b>", meta_label_style),
            Paragraph("github.com/Anmolkr001/KIA-Data-Analytics", meta_val_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[80, 175, 85, 175])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=KIA_RED, spaceAfter=12))

    # -----------------------------------------------------------------------
    # Section 1: Executive Summary
    # -----------------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "This project engineers an end-to-end commercial intelligence platform for the <b>Bhubaneswar Kia Dealership</b>. "
        "Modern automotive retail suffers from high digital acquisition spend coupled with poor downstream lead visibility. "
        "By ingesting and analyzing <b>6,967 actual CRM leads</b> across 86 attributes, this system introduces: "
        "(1) rigorous empirical funnel attribution, (2) an XGBoost classification engine with local SHAP feature attributions, "
        "(3) a sandboxed natural-language query agent (LangChain AI Copilot), and (4) an interactive React 19 web dashboard "
        "with an immersive 360° vehicle showroom, strictly secured by credential gates.",
        body_style
    ))

    # Callout Box: High-Impact Findings
    callout_data = [[
        Paragraph(
            "<b>Key Highlights:</b><br/>"
            "• <b>Overall Conversion:</b> 6,967 Enquiries resulted in 786 Retail Deliveries (<b>11.28% Conversion Rate</b>).<br/>"
            "• <b>Test Drive Multiplier:</b> Prospects completing a Test Drive convert at <b>19.11% vs. 4.44%</b> without (<b>4.30× lift</b>).<br/>"
            "• <b>Follow-up Sweet Spot:</b> Optimal retail conversion peaks at <b>2 to 4 follow-ups</b> (19.06%); collapses to <1.6% past 5 calls.<br/>"
            "• <b>ML Predictor Accuracy:</b> XGBoost achieves <b>ROC-AUC of 0.9804</b> with 97.8% recall on retail conversion prospects.",
            callout_style
        )
    ]]
    callout_table = Table(callout_data, colWidths=[515])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#FECACA")),
        ('LINELEFT', (0,0), (0,0), 3.5, KIA_RED),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 10))

    # -----------------------------------------------------------------------
    # Section 2: End-to-End System Architecture
    # -----------------------------------------------------------------------
    story.append(Paragraph("2. Technical Architecture & Data Pipeline", h1_style))
    story.append(Paragraph(
        "The application is organized into four decoupled architectural tiers ensuring speed, sandbox safety, and clean separation of concerns:",
        body_style
    ))
    story.append(Paragraph("• <b>Data Engineering Layer:</b> Raw CRM exports (6,967 rows × 86 columns) are cleaned via <code>src/clean_data.py</code>, normalized for phone formatting, postal codes, and sales cycle timing, and mirrored into a local SQLite database (<code>data/leads.db</code>).", bullet_style))
    story.append(Paragraph("• <b>Machine Learning Engine:</b> An <code>XGBClassifier</code> trained on 15 demographic, behavioral, and engagement features, addressing the 7.86:1 negative-to-positive class imbalance via cost-sensitive learning.", bullet_style))
    story.append(Paragraph("• <b>Microservice Backend:</b> FastAPI running on port 8000 exposes REST endpoints for analytical trends, paginated lead tables, real-time ML inference (<code>POST /predict</code>), and natural language LangChain execution.", bullet_style))
    story.append(Paragraph("• <b>Client Experience Layer:</b> React 19 single-page application built on Vite and TailwindCSS, deployed globally on Vercel with role-authenticated access, 8 analytical views, and 3D car showroom.", bullet_style))
    story.append(Spacer(1, 8))

    # -----------------------------------------------------------------------
    # Section 3: Empirical CRM Analytical Findings
    # -----------------------------------------------------------------------
    story.append(Paragraph("3. Empirical CRM Analytical Findings", h1_style))
    story.append(Paragraph(
        "Quantitative analysis across all stages of the customer acquisition lifecycle yielded distinct empirical benchmarks:",
        body_style
    ))

    # Table 3.1: Funnel Performance
    story.append(Paragraph("3.1 Full Funnel Conversion & Drop-off Rates", h2_style))
    funnel_headers = ["Funnel Stage", "Total Leads", "Stage Conversion", "Cumulative Conv.", "Drop-off Rate"]
    funnel_rows = [
        ["Enquiry", "6,967", "100.0%", "100.0%", "0.0%"],
        ["Test Drive", "3,249", "46.63%", "46.63%", "53.37%"],
        ["Booking", "721", "22.19%", "10.35%", "77.81% (Peak Drop)"],
        ["Retail Delivery", "786", "109.02%*", "11.28%", "Fulfillment >95%"]
    ]
    t_data = [[Paragraph(h, table_header_style) for h in funnel_headers]]
    for r in funnel_rows:
        t_data.append([
            Paragraph(r[0], table_cell_style),
            Paragraph(r[1], table_cell_center),
            Paragraph(r[2], table_cell_center),
            Paragraph(r[3], table_cell_bold_center),
            Paragraph(r[4], table_cell_center)
        ])
    t_funnel = Table(t_data, colWidths=[120, 95, 100, 100, 100])
    t_funnel.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), KIA_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_funnel)
    story.append(Paragraph("<font size='7' color='#64748B'>*Retail deliveries exceed active bookings due to direct walk-in spot deliveries and pre-booked backlog rollovers.</font>", body_style))
    story.append(Spacer(1, 6))

    # Table 3.2: Test Drive Multiplier
    story.append(Paragraph("3.2 Test Drive Impact Analysis", h2_style))
    td_headers = ["Test Drive Completed", "Enquiries", "Bookings", "Retail Units", "Retail Conversion Rate"]
    td_rows = [
        ["Yes (Completed)", "3,249", "579", "621", "19.11% (4.30x Multiplier)"],
        ["No (Not Done)", "3,718", "142", "165", "4.44%"]
    ]
    t_td_data = [[Paragraph(h, table_header_style) for h in td_headers]]
    for r in td_rows:
        t_td_data.append([
            Paragraph(r[0], table_cell_style),
            Paragraph(r[1], table_cell_center),
            Paragraph(r[2], table_cell_center),
            Paragraph(r[3], table_cell_center),
            Paragraph(r[4], table_cell_bold_center)
        ])
    t_td = Table(t_td_data, colWidths=[135, 95, 95, 95, 95])
    t_td.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), KIA_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_td)
    story.append(Spacer(1, 6))

    # Table 3.3: Sourcing Channel Performance
    story.append(Paragraph("3.3 Lead Sourcing Channel Efficiency vs. Volume", h2_style))
    src_headers = ["Channel", "Enquiries", "Share %", "Test Drives", "Retails", "TD Rate", "Retail Conv. Rate"]
    src_rows = [
        ["Referral", "1,097", "15.7%", "645", "303", "58.80%", "27.62% (Highest)"],
        ["Walk-in", "1,627", "23.4%", "1,191", "219", "73.20%", "13.46%"],
        ["Field Marketing", "941", "13.5%", "610", "122", "64.82%", "12.96%"],
        ["Telephone Direct", "384", "5.5%", "191", "29", "49.74%", "7.55%"],
        ["Online / Central CRM", "676", "9.7%", "197", "36", "29.14%", "5.33%"],
        ["Hyperlocal Paid Ads", "2,232", "32.0%", "412", "77", "18.46%", "3.45% (Lowest)"]
    ]
    t_src_data = [[Paragraph(h, table_header_style) for h in src_headers]]
    for r in src_rows:
        t_src_data.append([
            Paragraph(r[0], table_cell_style),
            Paragraph(r[1], table_cell_center),
            Paragraph(r[2], table_cell_center),
            Paragraph(r[3], table_cell_center),
            Paragraph(r[4], table_cell_center),
            Paragraph(r[5], table_cell_center),
            Paragraph(r[6], table_cell_bold_center)
        ])
    t_src = Table(t_src_data, colWidths=[115, 65, 55, 70, 65, 65, 80])
    t_src.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), KIA_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_src)
    story.append(Spacer(1, 6))

    # Table 3.4: Vehicle Model Demand
    story.append(Paragraph("3.4 Vehicle Model Commercial Demand & Conversion", h2_style))
    mod_headers = ["Vehicle Model", "Enquiries", "Test Drives", "Bookings", "Retail Deliveries", "Retail Conversion"]
    mod_rows = [
        ["SONET", "2,115", "1,123", "279", "344", "16.26% (Top Anchor)"],
        ["CARENS", "1,326", "656", "159", "195", "14.71%"],
        ["NEW SELTOS", "2,155", "1,241", "226", "187", "8.68%"],
        ["SYROS", "332", "87", "18", "16", "4.82%"],
        ["CARENS CLAVIS EV", "441", "110", "17", "20", "4.54%"],
        ["SELTOS (Legacy)", "566", "32", "22", "24", "4.24%"],
        ["CARNIVAL / EV6 / EV9", "32", "0", "0", "0", "0.00%"]
    ]
    t_mod_data = [[Paragraph(h, table_header_style) for h in mod_headers]]
    for r in mod_rows:
        t_mod_data.append([
            Paragraph(r[0], table_cell_style),
            Paragraph(r[1], table_cell_center),
            Paragraph(r[2], table_cell_center),
            Paragraph(r[3], table_cell_center),
            Paragraph(r[4], table_cell_center),
            Paragraph(r[5], table_cell_bold_center)
        ])
    t_mod = Table(t_mod_data, colWidths=[125, 75, 75, 75, 85, 80])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), KIA_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_mod)
    story.append(Spacer(1, 6))

    # Table 3.5: Follow-Up Cadence
    story.append(Paragraph("3.5 Consultant Follow-Up Cadence & Diminishing Returns", h2_style))
    fu_headers = ["Follow-up Bucket", "Enquiries", "Retail Deliveries", "Conversion Rate", "Operational Status"]
    fu_rows = [
        ["0 Calls", "372", "0", "0.00%", "Uncontacted Leads (Leakage)"],
        ["1 Call", "1,591", "5", "0.31%", "Under-contacted"],
        ["2 Calls", "2,203", "420", "19.06%", "Peak Conversion Window"],
        ["3 – 4 Calls", "2,034", "351", "17.26%", "High Efficiency Window"],
        ["5 – 6 Calls", "487", "8", "1.64%", "Diminishing Returns (Drop 90%)"],
        ["7+ Calls", "280", "2", "0.71%", "Unviable / Reassign to Drip"]
    ]
    t_fu_data = [[Paragraph(h, table_header_style) for h in fu_headers]]
    for r in fu_rows:
        t_fu_data.append([
            Paragraph(r[0], table_cell_style),
            Paragraph(r[1], table_cell_center),
            Paragraph(r[2], table_cell_center),
            Paragraph(r[3], table_cell_bold_center),
            Paragraph(r[4], table_cell_style)
        ])
    t_fu = Table(t_fu_data, colWidths=[115, 85, 95, 95, 125])
    t_fu.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), KIA_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_fu)
    story.append(Spacer(1, 10))

    # -----------------------------------------------------------------------
    # Section 4: Machine Learning & SHAP Explainability
    # -----------------------------------------------------------------------
    story.append(Paragraph("4. Predictive Machine Learning & Explainable AI", h1_style))
    story.append(Paragraph(
        "To prioritize incoming leads dynamically, an <b>Extreme Gradient Boosting (XGBoost)</b> model was trained to predict "
        "the probability of retail delivery. Stratified 5-Fold Cross Validation was employed to prevent data leakage.",
        body_style
    ))

    ml_headers = ["Metric", "Cross-Validation (Mean ± Std)", "Holdout Test Set", "Operational Interpretation"]
    ml_rows = [
        ["ROC-AUC", "0.9771 ± 0.0039", "0.9804", "Near-perfect ranking discrimination"],
        ["PR-AUC (Avg Precision)", "0.8377", "0.8642", "High precision in skewed positive class"],
        ["Recall (Lead Capture)", "0.9784", "0.9810", "Captures 98.1% of all true buyers"],
        ["F1 Score", "0.7057", "0.7214", "Harmonic balance of precision and recall"]
    ]
    t_ml_data = [[Paragraph(h, table_header_style) for h in ml_headers]]
    for r in ml_rows:
        t_ml_data.append([
            Paragraph(r[0], table_cell_style),
            Paragraph(r[1], table_cell_center),
            Paragraph(r[2], table_cell_bold_center),
            Paragraph(r[3], table_cell_style)
        ])
    t_ml = Table(t_ml_data, colWidths=[115, 120, 95, 185])
    t_ml.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), KIA_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_ml)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Top SHAP Local Feature Attribution Factors:</b>", body_style))
    story.append(Paragraph("1. <code>lead_warmth_Hot</code> (+3.08 SHAP): Primary initial positive signal for confirmed intent.", bullet_style))
    story.append(Paragraph("2. <code>followup_count</code> (+0.49 SHAP): Active two-way engagement strongly drives conversion probability.", bullet_style))
    story.append(Paragraph("3. <code>exchange_interest_Yes</code> (+0.40 SHAP): Trade-in intent provides an immediate 4.5× conversion lift.", bullet_style))
    story.append(Paragraph("4. <code>customer_type_Corporate</code> (+0.36 SHAP): B2B fleet approvals convert at 80.86%.", bullet_style))
    story.append(Paragraph("5. <code>aging_days</code> (+0.27 SHAP): Indicates sustained showroom negotiation and financing approvals.", bullet_style))
    story.append(Spacer(1, 10))

    # -----------------------------------------------------------------------
    # Section 5: AI Copilot & Benchmark Evaluation
    # -----------------------------------------------------------------------
    story.append(Paragraph("5. LangChain AI Copilot & Security Sandbox", h1_style))
    story.append(Paragraph(
        "The conversational assistant enables dealership personnel to query the database using plain natural language. "
        "To ensure production stability, an <b>AST Static Security Validator</b> strictly disallows code injection, filesystem modification, "
        "and infinite loops, enforced with a 5-second execution deadline.",
        body_style
    ))

    eval_headers = ["Benchmark Category", "Questions Tested", "Accuracy (%)", "Avg. Latency (ms)", "Test Result"]
    eval_rows = [
        ["Funnel KPIs", "5", "100.0%", "262.4 ms", "All 5 Passed"],
        ["Sourcing Channels", "3", "100.0%", "145.2 ms", "All 3 Passed"],
        ["Funnel Impact (Test Drives)", "2", "100.0%", "178.6 ms", "All 2 Passed"],
        ["Vehicle Models", "2", "100.0%", "148.9 ms", "All 2 Passed"],
        ["Geography (Bhubaneswar)", "1", "100.0%", "143.2 ms", "Passed"],
        ["CRM Operations (Follow-ups)", "2", "100.0%", "157.6 ms", "All 2 Passed"],
        ["Overall Test Suite", "15", "100.0%", "190.8 ms", "15 / 15 Passed (Zero Errors)"]
    ]
    t_ev_data = [[Paragraph(h, table_header_style) for h in eval_headers]]
    for r in eval_rows:
        t_ev_data.append([
            Paragraph(r[0], table_cell_style),
            Paragraph(r[1], table_cell_center),
            Paragraph(r[2], table_cell_bold_center),
            Paragraph(r[3], table_cell_center),
            Paragraph(r[4], table_cell_style)
        ])
    t_ev = Table(t_ev_data, colWidths=[130, 85, 80, 100, 120])
    t_ev.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), KIA_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_ev)
    story.append(Spacer(1, 10))

    # -----------------------------------------------------------------------
    # Section 6: Actionable Managerial Recommendations
    # -----------------------------------------------------------------------
    story.append(Paragraph("6. Actionable Managerial & Strategic Directives", h1_style))
    recs = [
        "<b>1. Enforce Mandatory Test Drive Scheduling within 4 Hours:</b> With test-drives yielding a 4.3× conversion multiplier, dealership management should set a KPI targeting 60% test-drive completion. This alone would generate an estimated +180 incremental retail sales annually.",
        "<b>2. Restructure Digital Sourcing Budgets:</b> Reduce low-intent Hyperlocal ad spend (3.45% conversion) by 25% and reallocate those funds into customer referral reward programs (27.62% conversion) and dedicated B2B fleet outreach (80.86% conversion).",
        "<b>3. Automate Cadence Rules after 4 Follow-ups:</b> Reassign leads with 5+ unsuccessful follow-ups to automated WhatsApp/email nurturing sequences, preventing consultant burnout and redirecting attention to high-scoring prospects.",
        "<b>4. Launch an Instant Trade-in Appraisal Counter:</b> Offer free 10-minute certified vehicle valuations on every showroom entry; capturing trade-in intent boosts conversion from 6.11% to 27.61%."
    ]
    for rec in recs:
        story.append(Paragraph(rec, bullet_style))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_LIGHT, spaceAfter=8))
    story.append(Paragraph(
        "<b>Document Information:</b> Generated for technical and operational evaluation. "
        "Interactive dashboard live at <b>kia-data-analytics.vercel.app</b>. "
        "Full source repository: <b>github.com/Anmolkr001/KIA-Data-Analytics</b>.",
        ParagraphStyle('DocInfo', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, textColor=TEXT_MUTED)
    ))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully at: {output_path}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/practical_project_report.pdf"
    generate_pdf(out)
