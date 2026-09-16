import os
import random
import re

from google import genai


GEMINI_API_KEY = "AQ.Ab8RN6K7dhgGc4Mvnf5uXtrCwKQ0qBdOKKyBPMcfqwRynTi8Jw"
GEMINI_MODEL = "gemini-3.5-flash"


def normalize_api_key(raw_key):
	value = str(raw_key or "").strip().strip('"').strip("'")
	if not value:
		return ""

	
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

FALLBACK_PROJECT_IDEAS = [
	"""Theme / Skill Domain:

AI-Powered Full-Stack Web Apps (LLM integration + modern frontend)
Project Challenge:

Build a small, public web application that uses a large language model API to help users generate, refine, or explore personalized content around a single useful task (examples: study notes, meal ideas, workout plans, code explanations, travel itineraries, or interview prep). The app must accept user input, call an LLM, and display structured, useful output.
Why this matters:

Companies are hiring for people who can ship real products that combine solid web engineering with practical AI. This project proves you can integrate an external API, handle user input safely, structure LLM responses, and ship something usable—skills that appear in almost every modern product role.
Minimum Requirements:

A clean, responsive single-page (or multi-page) web interface
User can enter a prompt or parameters and receive generated output from an LLM
At least one structured output format (cards, lists, markdown, or simple tables—not just raw text)
Basic error handling and loading states
Clear README that explains the project, how to run it, and what your personal twist is
Deployed version (Vercel, Netlify, or similar) + public GitHub repo

Your Twist (required):

Theme the entire app around something personal to you (your major, a hobby, a side interest, a problem you actually face as a student, or a niche domain you care about). The UI, the example prompts, the tone of the generated content, and the name of the app should all reflect that personal angle. Generic “AI chatbot” clones are not accepted.
Suggested Tech Stack:

Frontend: Next.js (App Router) + TypeScript + Tailwind CSS
LLM: OpenAI API, Groq, or any free/low-cost alternative
Deployment: Vercel
Optional but welcome: simple local storage or a free database for saving past generations

Success Looks Like:

A polished, deployable project in a public GitHub repo that a hiring manager can open, understand in under two minutes, and immediately see both technical competence and personal creativity. Someone should be able to use the app and say “this feels useful and made by a real person,” not “this is another generic AI demo.”""",
	""" Theme / Skill Domain: RAG & Knowledge Systems

Project Challenge: Build a personal RAG (Retrieval-Augmented Generation) app that answers questions from a small set of documents you choose.

Why this matters: RAG is one of the most requested skills in AI product roles right now.

Minimum Requirements: Upload or hard-code 3–10 documents → embed them → retrieve relevant chunks → answer with an LLM. Simple UI + clear citations.

Your Twist (required): Theme the knowledge base around something personal (your lecture notes, a hobby, a side project, family recipes, etc.).

Suggested Tech Stack: Next.js + TypeScript + free embedding model (or OpenAI) + simple vector store (in-memory or free tier).

Success Looks Like: A working “ask my notes” tool that feels useful to you and is easy for others to try.""",
	""" Theme / Skill Domain: AI Agents & Tool Use

Project Challenge: Create a simple multi-step AI agent that can use 2–3 tools (e.g., search, calculator, weather, or a custom function) to complete a task.

Why this matters: Companies want engineers who understand agentic workflows, not just single LLM calls.

Minimum Requirements: Agent that plans → calls tools → returns a final answer. Visible step-by-step reasoning or logs.

Your Twist (required): Make the agent solve a real problem you care about (student life, fitness, travel planning, coding help, etc.).

Suggested Tech Stack: Next.js or simple Python (FastAPI/Streamlit) + LLM with tool calling.

Success Looks Like: You can watch the agent use tools and produce a useful result.""",
	"""Theme / Skill Domain: Data Visualization + Storytelling

Project Challenge: Build an interactive dashboard that visualizes a public dataset and tells a clear story.

Why this matters: Data storytelling is a core skill in product, analytics, and growth roles.

Minimum Requirements: At least 3 chart types, filters or interactions, and a short written narrative.

Your Twist (required): Choose a dataset and angle that reflects your interests or background.

Suggested Tech Stack: Next.js + Recharts/Chart.js or Observable/Plotly + Tailwind.

Success Looks Like: Someone can explore the data and immediately understand the insight. """,
	"""Theme / Skill Domain: Full-Stack CRUD + Auth

Project Challenge: Build a small personal productivity or tracking app with user accounts and full CRUD.

Why this matters: Most real products need auth + database operations.

Minimum Requirements: Sign-up/login, create/read/update/delete items, protected routes.

Your Twist (required): Theme it around something you actually use or want (habit tracker, reading list, job applications, workout log, etc.).

Suggested Tech Stack: Next.js + NextAuth/Clerk + Prisma + SQLite/PostgreSQL (free tier).

Success Looks Like: A polished mini-SaaS you could actually use daily. """,
	"""Theme / Skill Domain: Real-time Web Apps

Project Challenge: Create a real-time collaborative or live-updating experience (chat, shared board, live poll, or multiplayer mini-game).

Why this matters: Real-time features appear in almost every modern product.

Minimum Requirements: Multiple users can see updates without refreshing.

Your Twist (required): Make the theme personal or niche.

Suggested Tech Stack: Next.js + Socket.io or Partykit / Liveblocks / Supabase Realtime.

Success Looks Like: Two browser windows show live updates instantly. """,
	""" Theme / Skill Domain: Real-time Web Apps

Project Challenge: Create a real-time collaborative or live-updating experience (chat, shared board, live poll, or multiplayer mini-game).

Why this matters: Real-time features appear in almost every modern product.

Minimum Requirements: Multiple users can see updates without refreshing.

Your Twist (required): Make the theme personal or niche.

Suggested Tech Stack: Next.js + Socket.io or Partykit / Liveblocks / Supabase Realtime.

Success Looks Like: Two browser windows show live updates instantly.""",
	"""Theme / Skill Domain: AI Image + Text Generation

Project Challenge: Build a web app that generates images (or image + text) based on user prompts and displays them in a gallery.

Why this matters: Multimodal AI is exploding in product roles.

Minimum Requirements: Prompt → generate → display + simple history or favorites.

Your Twist (required): Constrain the style or domain to something personal (your art style, your city’s aesthetic, your major, a fictional world you like, etc.).

Suggested Tech Stack: Next.js + Replicate / Fal.ai / OpenAI Images + Tailwind.

Success Looks Like: A beautiful, themed image generator that feels unique. """,
	"""Theme / Skill Domain: API Design & Backend

Project Challenge: Design and build a clean REST or GraphQL API for a useful domain, then consume it from a simple frontend.

Why this matters: Strong API design is a differentiator in backend and full-stack interviews.

Minimum Requirements: Well-documented endpoints, proper status codes, validation, and a basic frontend that uses the API.

Your Twist (required): Choose a domain you care about.

Suggested Tech Stack: FastAPI or Next.js Route Handlers / Hono + simple frontend.

Success Looks Like: Clear API docs + working consumer that feels intentional. """,
	"""Theme / Skill Domain: Browser Extensions

Project Challenge: Build a useful Chrome/Firefox extension that solves a small daily friction.

Why this matters: Extensions demonstrate practical product thinking and browser APIs.

Minimum Requirements: Popup or content script, one clear feature, works on real pages.

Your Twist (required): Solve a problem you personally have (studying, shopping, coding, accessibility, etc.).

Suggested Tech Stack: Manifest V3 + vanilla JS or React + Tailwind.

Success Looks Like: You actually install and use it yourself. """,
	"""Theme / Skill Domain: Mobile-First Progressive Web App

Project Challenge: Build a fast, installable PWA focused on a single mobile use case.

Why this matters: Mobile experience and offline capability are still high-value skills.

Minimum Requirements: Works offline (or with cached data), installable, good mobile UX.

Your Twist (required): Theme it around a personal need or interest.

Suggested Tech Stack: Next.js or Vite + PWA plugin + Tailwind.

Success Looks Like: Feels native on a phone and is genuinely useful offline. """,
]


def get_fallback_project_idea():
	return random.choice(FALLBACK_PROJECT_IDEAS)


def get_project_idea(prompt=PROJECT_PROMPT):
	try:
		key = normalize_api_key(GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", ""))
		if not key or len(key) < 20:
			print("AI key is missing or invalid. Set the GEMINI_API_KEY environment variable to a valid Google AI Studio key.")
			return get_fallback_project_idea()

		client = genai.Client(api_key=key)
		response = client.models.generate_content(
			model=GEMINI_MODEL,
			contents=prompt,
		)
		
		# Properly extract text from Gemini API response
		# The response object has a .text attribute that contains the generated content
		text = response.text if hasattr(response, 'text') else ""
		
		# Debug logging to diagnose issues
		print(f"DEBUG: Response type: {type(response)}")
		print(f"DEBUG: Response text length: {len(text) if text else 0}")
		
		# Return the text if it's valid, otherwise use fallback
		if text and isinstance(text, str) and text.strip():
			return text.strip()
		else:
			print("WARNING: Received empty response from Gemini API")
			return get_fallback_project_idea()
			
	except Exception as error:
		print(f"AI project request failed: {error}")
		import traceback
		traceback.print_exc()
		return get_fallback_project_idea()