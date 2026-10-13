import os
import json
import re
from io import BytesIO
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from duckduckgo_search import DDGS

# --- Constants ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-3-pro-preview"

# --- Helper Functions ---

def clean_json_response(response_text: str) -> str:
    """
    Strips Markdown code blocks (```json ... ```) from the response.
    """
    match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
    if match:
        return match.group(1)
    match = re.search(r"```\s*(.*?)\s*```", response_text, re.DOTALL)
    if match:
        return match.group(1)
    return response_text.strip()

# --- Services ---

class GeminiClient:
    def __init__(self):
        if not GOOGLE_API_KEY:
            print("WARNING: GOOGLE_API_KEY is not set.")
        self.client = genai.Client(api_key=GOOGLE_API_KEY)

    def generate_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                )
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            raise e

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        response_text = self.generate_completion(system_prompt, user_prompt, temperature=0.5)
        cleaned_json = clean_json_response(response_text)
        try:
            return json.loads(cleaned_json)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {cleaned_json}")
            raise ValueError("AI returned invalid JSON")

class PDFProcessor:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"PDF Extraction Error: {e}")
            raise ValueError("Failed to extract text from PDF")

class SearchService:
    @staticmethod
    def search(query: str, max_results: int = 3) -> str:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return "\n\n".join([f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}" for r in results])
        except Exception as e:
            print(f"Search Error: {e}")
            return ""

class ReportGenerator:
    @staticmethod
    def create_pdf_report(idea_title: str, analysis: Dict[str, Any]) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        h2_style = styles["Heading2"]
        h3_style = styles["Heading3"]
        normal_style = styles["Normal"]
        
        # Custom Styles
        verdict_style = ParagraphStyle(
            'Verdict',
            parent=styles['Normal'],
            fontSize=12,
            leading=16,
            textColor=colors.whitesmoke,
            backColor=colors.darkslateblue,
            borderPadding=10,
            spaceAfter=20
        )

        elements = []

        # Header
        elements.append(Paragraph(f"Validation Report: {idea_title}", title_style))
        elements.append(Spacer(1, 12))
        
        # Verdict
        verdict_text = f"<b>VERDICT:</b> {analysis.get('verdict', 'N/A')} (Score: {analysis.get('overallScore', 0)})"
        elements.append(Paragraph(verdict_text, verdict_style))
        
        # Scores Table
        scores = analysis.get('scores', {})
        score_data = [
            ["Metric", "Score"],
            ["Problem", scores.get('problem', 0)],
            ["Solution", scores.get('solution', 0)],
            ["Market", scores.get('market', 0)],
            ["Moat", scores.get('moat', 0)],
            ["Feasibility", scores.get('feasibility', 0)]
        ]
        t = Table(score_data, colWidths=[4*inch, 2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))

        # Lean Canvas
        elements.append(Paragraph("Lean Business Canvas", h2_style))
        lc = analysis.get('leanCanvas', {})
        
        canvas_items = [
            ("Problem", lc.get('problemSummary', '')),
            ("Solution", lc.get('solutionSummary', '')),
            ("Metrics", lc.get('metrics', '')),
            ("Channels", lc.get('channels', '')),
            ("Revenue", lc.get('revenue', '')),
            ("Costs", lc.get('costs', ''))
        ]
        
        for title, content in canvas_items:
            elements.append(Paragraph(title, h3_style))
            elements.append(Paragraph(content, normal_style))
            elements.append(Spacer(1, 6))
            
        elements.append(PageBreak())
        
        # Go To Market
        elements.append(Paragraph("Go-To-Market Strategy", h2_style))
        gtm = analysis.get('goToMarket', {})
        
        elements.append(Paragraph("First Customers", h3_style))
        for c in gtm.get('firstCustomers', []):
            elements.append(Paragraph(f"• <b>{c.get('persona')}</b>: {c.get('details')}", normal_style))
            
        elements.append(Spacer(1, 12))
        
        for h in gtm.get('marketingHooks', []):
            elements.append(Paragraph(f"• <i>\"{h.get('hook')}\"</i> - {h.get('details')}", normal_style))

        # Strategy Flow
        if 'strategyFlow' in analysis:
            elements.append(PageBreak())
            elements.append(Paragraph("Strategy Flow", h2_style))
            sf = analysis['strategyFlow']
            if 'vision' in sf:
                elements.append(Paragraph("Vision & Mission", h3_style))
                elements.append(Paragraph(f"<b>Vision:</b> {sf['vision']}", normal_style))
                elements.append(Paragraph(f"<b>Mission:</b> {sf['mission']}", normal_style))
                elements.append(Spacer(1, 12))
            
            if 'objectives' in sf:
                elements.append(Paragraph("Objectives (OKRs)", h3_style))
                for okr in sf['objectives']:
                    elements.append(Paragraph(f"• <b>{okr.get('objective')}</b>", normal_style))
                    for kr in okr.get('keyResults', []):
                        elements.append(Paragraph(f"  - {kr}", normal_style))
                    elements.append(Spacer(1, 6))

        # Market Intel
        if 'marketIntel' in analysis:
            elements.append(PageBreak())
            elements.append(Paragraph("Go-To-Market Intel", h2_style))
            mi = analysis['marketIntel']
            
            if 'segments' in mi:
                elements.append(Paragraph("Market Segments", h3_style))
                for seg in mi['segments']:
                    elements.append(Paragraph(f"<b>{seg.get('name')}</b> ({seg.get('size')})", normal_style))
                    elements.append(Paragraph(f"Pain: {seg.get('pain')} | Willingness: {seg.get('willingness')}", normal_style))
                    elements.append(Paragraph(seg.get('description'), normal_style))
                    elements.append(Spacer(1, 6))

            if 'channels' in mi:
                elements.append(Paragraph("Acquisition Channels", h3_style))
                channel_data = [["Channel", "Type", "Cost", "Reach"]]
                for ch in mi['channels']:
                    channel_data.append([ch.get('name'), ch.get('type'), ch.get('cost'), ch.get('reach')])
                
                t = Table(channel_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 12))

            if 'pricing' in mi:
                elements.append(Paragraph("Pricing Strategy", h3_style))
                for p in mi['pricing']:
                    elements.append(Paragraph(f"<b>{p.get('tier')}</b>: ${p.get('price')}/{p.get('period')}", normal_style))
                    elements.append(Paragraph(f"Features: {', '.join(p.get('features', []))}", normal_style))
                    elements.append(Spacer(1, 6))

        # Scenario Lab
        if 'scenarioLab' in analysis:
            elements.append(PageBreak())
            elements.append(Paragraph("Scenario Lab Analysis", h2_style))
            sl = analysis['scenarioLab']
            elements.append(Paragraph(f"<b>Scenario:</b> {sl.get('scenarioInput', 'N/A')}", normal_style))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"<b>Viability Score:</b> {sl.get('viabilityScore')}/100", normal_style))
            elements.append(Paragraph(f"<b>Analysis:</b> {sl.get('analysis')}", normal_style))
            
            if 'actions' in sl:
                elements.append(Paragraph("Recommended Actions:", h3_style))
                for action in sl['actions']:
                    elements.append(Paragraph(f"• {action}", normal_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer
