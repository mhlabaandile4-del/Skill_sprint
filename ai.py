import os
import re

from google import genai


GEMINI_API_KEY = "AQ.Ab8RN6JlfFhdcxeussDqYIwKAyJ67TL6ojq9x3OcEZdGJgiuDA"
GEMINI_MODEL = "gemini-1.5-flash"


def normalize_api_key(raw_key):
	value = str(raw_key or "").strip().strip('"').strip("'")
	if not value:
		return ""

	# Accept both AIza-prefixed keys and AQ. prefixed keys from Google AI Studio
	if value.startswith("AIza") or value.startswith("AQ."):
		return value

	return value


PROJECT_PROMPT = """You are an expert technical educator and career coach specializing in helping university students and recent graduates build job-ready portfolios.

Generate one clear, practical, industry-aligned project challenge for the current week.

Rules:
1. Give the same core challenge to every student.
2. Base it on a current high-demand technology skill.
3. Make it buildable in 5-10 hours.
4. Require a personal creative twist.
5. Make the deliverable suitable for a public GitHub repository.
6. Use this exact structure:

**Theme / Skill Domain:**
**Project Challenge:**
**Why this matters:**
**Minimum Requirements:**
-
**Your Twist (required):**
**Suggested Tech Stack:**
**Success Looks Like:**
"""

FALLBACK_PROJECT_IDEA = (
	"Build a small, polished project that demonstrates a current technical "
	"skill and publish it to GitHub."
)


def get_project_idea(prompt=PROJECT_PROMPT):
	try:
		key = normalize_api_key(GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", ""))
		if not key or len(key) < 20:
			print("AI key is missing or invalid. Set the GEMINI_API_KEY environment variable to a valid Google AI Studio key.")
			return FALLBACK_PROJECT_IDEA

		client = genai.Client(api_key=key)
		response = client.models.generate_content(
			model=GEMINI_MODEL,
			contents=prompt,
		)
		text = getattr(response, "text", "")
		return text.strip() if isinstance(text, str) and text.strip() else FALLBACK_PROJECT_IDEA
	except Exception as error:
		print(f"AI project request failed: {error}")
		return FALLBACK_PROJECT_IDEA