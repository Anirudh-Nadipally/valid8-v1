"""
Gemini 2.5 Pro Grounding Service
Real-time market data enrichment using Google Search grounding
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import httpx


# Configuration
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-06-05:generateContent"


@dataclass
class MarketData:
    """Market size and growth data with sources"""
    tam: Optional[str] = None
    tam_raw: Optional[int] = None
    sam: Optional[str] = None
    som: Optional[str] = None
    growth_rate: Optional[str] = None
    source: Optional[str] = None
    source_year: Optional[int] = None


@dataclass
class CompetitorData:
    """Competitor information with funding"""
    name: str
    funding_total: Optional[str] = None
    last_round: Optional[str] = None
    last_round_date: Optional[str] = None
    focus: Optional[str] = None
    gap: Optional[str] = None  # Exploitable weakness
    source: Optional[str] = None


@dataclass
class TrendData:
    """Market trend with direction"""
    trend: str
    direction: str  # "up", "down", "stable"
    evidence: Optional[str] = None
    source: Optional[str] = None


@dataclass
class GroundingResult:
    """Complete grounding result with all market intelligence"""
    market: MarketData
    competitors: List[CompetitorData]
    trends: List[TrendData]
    google_trends_change: Optional[str] = None
    last_updated: str = ""
    sources: List[str] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()


class GroundingService:
    """
    Gemini 2.5 Pro with Google Search grounding for real-time market data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set. Add to .env file.")
    
    async def enrich_idea(
        self,
        industry: str,
        geography: str = "global",
        problem: str = "",
        solution: str = ""
    ) -> GroundingResult:
        """
        Run parallel grounding queries to enrich idea with real data
        
        Args:
            industry: Target industry (e.g., "construction tech")
            geography: Target market geography
            problem: Problem statement for context
            solution: Solution description for context
            
        Returns:
            GroundingResult with market, competitors, and trends
        """
        # Run queries in parallel
        tasks = [
            self._query_market_size(industry, geography),
            self._query_competitors(industry, geography),
            self._query_trends(industry),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results
        market_data = results[0] if not isinstance(results[0], Exception) else MarketData()
        competitors = results[1] if not isinstance(results[1], Exception) else []
        trends = results[2] if not isinstance(results[2], Exception) else []
        
        # Collect all sources
        all_sources = []
        if market_data.source:
            all_sources.append(market_data.source)
        for comp in competitors:
            if comp.source and comp.source not in all_sources:
                all_sources.append(comp.source)
        for trend in trends:
            if trend.source and trend.source not in all_sources:
                all_sources.append(trend.source)
        
        return GroundingResult(
            market=market_data,
            competitors=competitors,
            trends=trends,
            sources=all_sources
        )
    
    async def _query_market_size(self, industry: str, geography: str) -> MarketData:
        """Query for TAM/SAM/SOM data"""
        prompt = f"""
Search for current market size data for: {industry}

Find and return ONLY verified data with sources in this exact JSON format:
{{
    "tam": "$X billion" or "$X million",
    "tam_raw": number in dollars,
    "sam": "serviceable market for {geography}",
    "growth_rate": "X% CAGR",
    "source": "Report name, Publisher Year",
    "source_year": 2024
}}

Use the most recent report (2023 or 2024 preferred).
If data not found, return null for that field.
Return ONLY valid JSON, no explanation.
"""
        
        try:
            response = await self._call_gemini_with_grounding(prompt)
            data = self._extract_json(response)
            
            if data:
                return MarketData(
                    tam=data.get("tam"),
                    tam_raw=data.get("tam_raw"),
                    sam=data.get("sam"),
                    growth_rate=data.get("growth_rate"),
                    source=data.get("source"),
                    source_year=data.get("source_year")
                )
        except Exception as e:
            print(f"Market size query failed: {e}")
        
        return MarketData()
    
    async def _query_competitors(self, industry: str, geography: str) -> List[CompetitorData]:
        """Query for competitor funding data"""
        prompt = f"""
Search for funded startups in: {industry} in {geography}

Find top 3-5 funded competitors and return in this exact JSON format:
{{
    "competitors": [
        {{
            "name": "Company Name",
            "funding_total": "$X million raised",
            "last_round": "Series X",
            "last_round_date": "Month Year",
            "focus": "What they do",
            "gap": "Weakness or missing capability",
            "source": "Crunchbase or similar"
        }}
    ]
}}

Focus on recently funded companies (last 3 years).
Return ONLY valid JSON, no explanation.
"""
        
        try:
            response = await self._call_gemini_with_grounding(prompt)
            data = self._extract_json(response)
            
            if data and "competitors" in data:
                return [
                    CompetitorData(**comp)
                    for comp in data["competitors"][:5]  # Limit to 5
                ]
        except Exception as e:
            print(f"Competitor query failed: {e}")
        
        return []
    
    async def _query_trends(self, industry: str) -> List[TrendData]:
        """Query for industry trends"""
        prompt = f"""
Search for current trends in: {industry} for 2024-2025

Find top 3 emerging trends and return in this exact JSON format:
{{
    "trends": [
        {{
            "trend": "Trend name",
            "direction": "up" | "down" | "stable",
            "evidence": "Brief supporting data point",
            "source": "Article or report name"
        }}
    ]
}}

Focus on technology and market shifts.
Return ONLY valid JSON, no explanation.
"""
        
        try:
            response = await self._call_gemini_with_grounding(prompt)
            data = self._extract_json(response)
            
            if data and "trends" in data:
                return [
                    TrendData(**trend)
                    for trend in data["trends"][:3]  # Limit to 3
                ]
        except Exception as e:
            print(f"Trends query failed: {e}")
        
        return []
    
    async def _call_gemini_with_grounding(self, prompt: str) -> str:
        """
        Call Gemini 2.5 Pro with Google Search grounding enabled
        """
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "tools": [
                {"googleSearch": {}}  # Enable grounding
            ],
            "generationConfig": {
                "temperature": 0.1,  # Low for factual accuracy
                "maxOutputTokens": 2048
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={self.api_key}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from response
            candidates = result.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            
            return ""
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from response text"""
        if not text:
            return None
        
        # Try to find JSON in the text
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```") and not in_json:
                    in_json = True
                    continue
                elif line.startswith("```") and in_json:
                    break
                elif in_json:
                    json_lines.append(line)
            text = "\n".join(json_lines)
        
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON object in text
        import re
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return None


# Synchronous wrapper for non-async contexts
def enrich_idea_sync(
    industry: str,
    geography: str = "global",
    problem: str = "",
    solution: str = ""
) -> GroundingResult:
    """Synchronous wrapper for enrich_idea"""
    service = GroundingService()
    return asyncio.run(service.enrich_idea(industry, geography, problem, solution))


# Helper to convert result to dict for JSON serialization
def grounding_result_to_dict(result: GroundingResult) -> Dict[str, Any]:
    """Convert GroundingResult to JSON-serializable dict"""
    return {
        "market": asdict(result.market),
        "competitors": [asdict(c) for c in result.competitors],
        "trends": [asdict(t) for t in result.trends],
        "google_trends_change": result.google_trends_change,
        "last_updated": result.last_updated,
        "sources": result.sources
    }
