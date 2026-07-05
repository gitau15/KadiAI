"""Scraper for new.kenyalaw.org — downloads election-related PDFs."""

import asyncio
import logging
import re
import time
from pathlib import Path
from dataclasses import dataclass, field

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://new.kenyalaw.org"
CRAWL_DELAY = 5  # Respect robots.txt crawl-delay
HEADERS = {"User-Agent": "ElectionLawAI/1.0 (research bot)"}

# Election-relevant search terms
LEGISLATION_QUERIES = [
    "Elections",
    "IEBC",
    "Political Parties",
    "Constitution",
    "Voter",
    "Electoral",
    "Independent Electoral",
    "Election Offences",
    "Campaign Financing",
]

# Courts most likely to have election petitions
COURT_CODES = ["KESC", "KECA", "KEHC"]

# Keywords to filter election-related judgments
ELECTION_KEYWORDS = [
    "election", "electoral", "iebc", "voter", "ballot",
    "petition", "polling", "constituency", "political party",
    "campaign", "nomination", "vote", "electoral commission",
    "returning officer", "election petition",
]


@dataclass
class ScrapeResult:
    documents_found: int = 0
    documents_downloaded: int = 0
    documents_skipped: int = 0
    errors: list[str] = field(default_factory=list)
    downloaded_files: list[str] = field(default_factory=list)


class KenyaLawScraper:
    """Scrapes election-related legislation and case law from kenyalaw.org."""

    def __init__(self, output_dir: Path, max_pages: int = 3):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_pages = max_pages
        self._seen_urls: set[str] = set()
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                timeout=60,
                follow_redirects=True,
                headers=HEADERS,
            )
        return self._client

    def _safe_filename(self, title: str) -> str:
        """Convert a document title to a safe filename."""
        clean = re.sub(r'[<>:"/\\|?*]', '', title)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) > 200:
            clean = clean[:200]
        return f"{clean}.pdf"

    def _download_pdf(self, doc_url: str, title: str) -> str | None:
        """Download a PDF from the /source endpoint."""
        source_url = f"{BASE_URL}{doc_url}/source"
        if source_url in self._seen_urls:
            return None

        self._seen_urls.add(source_url)
        filename = self._safe_filename(title)
        filepath = self.output_dir / filename

        if filepath.exists() and filepath.stat().st_size > 0:
            logger.info(f"  SKIP (exists): {filename}")
            return None

        try:
            client = self._get_client()
            resp = client.get(source_url)
            if resp.status_code == 200 and "pdf" in resp.headers.get("content-type", ""):
                filepath.write_bytes(resp.content)
                size_kb = len(resp.content) / 1024
                logger.info(f"  OK ({size_kb:.0f} KB): {filename}")
                return str(filepath)
            else:
                logger.warning(f"  FAIL ({resp.status_code}): {source_url}")
                return None
        except Exception as e:
            logger.error(f"  ERROR: {source_url} - {e}")
            raise

    def scrape_legislation(self, result: ScrapeResult):
        """Search and download election-related legislation PDFs."""
        logger.info("=== Scraping legislation ===")
        client = self._get_client()

        for query in LEGISLATION_QUERIES:
            logger.info(f"  Searching: {query}")
            try:
                url = f"{BASE_URL}/legislation/all?q={query}"
                resp = client.get(url)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                links = soup.select('a[href*="/akn/ke/act/"]')

                for link in links:
                    href = link.get("href", "").rstrip()
                    text = link.get_text(strip=True)

                    # Skip navigation/duplicate links
                    if not href or text.endswith("\u2192") or len(text) < 3:
                        continue
                    if href in self._seen_urls:
                        result.documents_skipped += 1
                        continue

                    # Filter: skip unrelated regulations (e.g. Dairy/Nurses/Tea/Trade Union elections)
                    title_lower = text.lower()
                    _UNRELATED = ["nurse", "tea ", "dairy", "trade union", "council regulation",
                                  "human resource management", "youth representative"]
                    if any(u in title_lower for u in _UNRELATED):
                        continue
                    is_election_relevant = any(
                        kw in title_lower for kw in [
                            "election", "electoral", "iebc", "political party",
                            "voter", "constituenc", "campaign", "constitution",
                            "independent electoral",
                        ]
                    )
                    if not is_election_relevant:
                        continue

                    result.documents_found += 1
                    try:
                        downloaded = self._download_pdf(href, text)
                        if downloaded:
                            result.documents_downloaded += 1
                            result.downloaded_files.append(downloaded)
                        else:
                            result.documents_skipped += 1
                    except Exception as e:
                        result.errors.append(f"{text}: {e}")

                    time.sleep(1)  # Be gentle between downloads

                time.sleep(CRAWL_DELAY)

            except Exception as e:
                result.errors.append(f"Search '{query}': {e}")
                logger.error(f"  Error searching '{query}': {e}")

    def scrape_judgments(self, result: ScrapeResult):
        """Crawl Supreme Court & Court of Appeal judgments for election petitions."""
        logger.info("=== Scraping judgments ===")
        client = self._get_client()

        for court in COURT_CODES:
            for page in range(1, self.max_pages + 1):
                page_url = f"{BASE_URL}/judgments/{court}/"
                if page > 1:
                    page_url += f"?page={page}"

                logger.info(f"  {court} page {page}")
                try:
                    resp = client.get(page_url)
                    if resp.status_code != 200:
                        break

                    soup = BeautifulSoup(resp.text, "lxml")
                    links = soup.select('a[href*="/akn/ke/judgment/"]')

                    if not links:
                        break

                    for link in links:
                        href = link.get("href", "").rstrip()
                        text = link.get_text(strip=True)

                        if not href or text.endswith("\u2192") or len(text) < 10:
                            continue
                        if href in self._seen_urls:
                            result.documents_skipped += 1
                            continue

                        # Filter for election-related cases
                        title_lower = text.lower()
                        is_election_case = any(
                            kw in title_lower for kw in ELECTION_KEYWORDS
                        )
                        if not is_election_case:
                            continue

                        result.documents_found += 1
                        # Use case citation as filename
                        safe_title = text[:150].split("(")[0].strip()
                        if not safe_title:
                            safe_title = href.split("/")[-1]

                        try:
                            downloaded = self._download_pdf(href, safe_title)
                            if downloaded:
                                result.documents_downloaded += 1
                                result.downloaded_files.append(downloaded)
                            else:
                                result.documents_skipped += 1
                        except Exception as e:
                            result.errors.append(f"{safe_title}: {e}")

                        time.sleep(1)

                    time.sleep(CRAWL_DELAY)

                except Exception as e:
                    result.errors.append(f"{court} p{page}: {e}")
                    logger.error(f"  Error {court} p{page}: {e}")
                    break

    def run(self) -> ScrapeResult:
        """Run the full scraper."""
        result = ScrapeResult()
        try:
            self.scrape_legislation(result)
            self.scrape_judgments(result)
        finally:
            if self._client and not self._client.is_closed:
                self._client.close()

        logger.info(
            f"Scrape complete: {result.documents_found} found, "
            f"{result.documents_downloaded} downloaded, "
            f"{result.documents_skipped} skipped, "
            f"{len(result.errors)} errors"
        )
        return result
