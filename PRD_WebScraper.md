Product Requirements Document: WebScrapeToolkit
Version: 1.0
Date: May 30, 2025
Document Owner: AI Assistant (Gemini)

1. Introduction
1.1 Purpose of the Document
This document outlines the product requirements for the WebScrapeToolkit, a comprehensive Python-based system designed for web scraping with integrated AI-powered content analysis. It defines the product's purpose, features, target audience, user stories, and functional/non-functional requirements based on the existing codebase.

1.2 Product Overview
WebScrapeToolkit is an advanced tool that enables users to extract data from websites efficiently and responsibly. Beyond basic scraping, it leverages Large Language Models (LLMs) from providers like OpenAI, Anthropic, and Google Gemini to perform intelligent analysis on the scraped content. This includes tasks such as summarization, sentiment analysis, content categorization, entity extraction, and language detection. The toolkit offers multiple user interfaces (Web UI, CLI Chatbot, Direct CLI) to cater to different user preferences and use cases. Scraped data and analysis results are persisted in a PostgreSQL database for history, analytics, and further use.

1.3 Goals and Objectives
Primary Goal: To provide a robust, flexible, and intelligent solution for web scraping and content analysis.

Empower Users: Enable users with varying technical skills to extract and understand web data effectively.

Leverage AI: Integrate cutting-edge AI capabilities to derive meaningful insights from raw web content.

Promote Responsible Scraping: Incorporate features like rate limiting and robots.txt compliance.

Offer Versatility: Provide multiple interaction methods (Web UI, Chatbot, CLI) and configurable options.

Ensure Data Persistence: Store scraped data and analysis for historical review and trend analysis.

2. Target Audience
Data Analysts & Researchers: Individuals who need to gather and analyze large volumes of web data for research, market analysis, or trend identification.

Developers & Programmers: Users who require a programmable toolkit for integrating web scraping and AI analysis into their applications or workflows.

Content Curators & Marketers: Professionals looking to monitor web content, understand sentiment, categorize information, and summarize articles.

Technical Users: Individuals comfortable with command-line interfaces or web applications for specialized scraping tasks.

Students & Educators: For learning and teaching web scraping and AI concepts.

3. User Stories
As a Data Analyst, I want to scrape multiple articles from a list of URLs so that I can perform a comparative analysis of their content and sentiment.

As a Developer, I want to use a CLI to trigger scraping tasks and receive structured JSON output so that I can integrate the scraped data into my custom applications.

As a Content Marketer, I want to use a web UI to scrape competitor blog posts and get AI-generated summaries and key topics so that I can quickly understand their content strategy.

As a Researcher, I want to interact with a chatbot to scrape academic papers and extract named entities (like authors and institutions) so that I can build a knowledge base.

As a Technical User, I want to configure the AI provider (OpenAI, Gemini, Anthropic) for content analysis so that I can choose the model that best suits my needs and budget.

As any User, I want to view a history of my scraping tasks and their results so that I can refer back to previously extracted information.

As any User, I want to be assured that the scraper respects robots.txt and uses rate limiting so that I can scrape responsibly.

As a Web UI User, I want to easily switch between scraping single URLs and multiple URLs so that I can adapt to different scraping tasks.

As a Chatbot User, I want to use natural language commands to initiate scraping and analysis so that I can interact with the tool conversationally.

As an Administrator/Developer, I want to see analytics on scraping activity so that I can understand usage patterns and popular domains.

4. Product Features (Functional Requirements)
4.1 Core Web Scraping (web_scraper.py)
FR1.1 URL Fetching: The system must fetch HTML content from specified URLs using HTTP/HTTPS.

FR1.2 HTML Parsing: The system must parse HTML content to enable data extraction (using BeautifulSoup).

FR1.3 Text Extraction: The system must extract clean textual content from web pages.

FR1.4 Link Extraction: The system must extract all hyperlinks ( tags) from web pages, including their URLs, anchor text, and titles.

FR1.5 Image Extraction: The system must extract image information ( tags), including source URLs, alt text, and titles.

FR1.6 Metadata Extraction: The system must extract page metadata (e.g., title, meta description, keywords, Open Graph tags).

FR1.7 Robots.txt Compliance: The system must check and respect robots.txt directives for specified URLs (configurable).

FR1.8 Rate Limiting: The system must implement configurable delays between requests to avoid overloading servers.

FR1.9 Session Management (Requests): The system must use HTTP sessions for connection pooling and cookie persistence.

FR1.10 URL Normalization: The system must automatically normalize URLs (e.g., add https:// if missing) before fetching.

4.2 AI-Powered Content Analysis (ai_enhanced_scraper.py, chatbot.py)
FR2.1 Multi-Provider AI Support: The system must support integration with multiple AI providers (OpenAI, Anthropic, Google Gemini).

FR2.1.1 Provider Selection: Users must be able to select or configure their preferred AI provider.

FR2.2 Content Summarization: The system must generate concise AI summaries of scraped text content.

FR2.3 Sentiment Analysis: The system must perform sentiment analysis on scraped text, providing a score and confidence level.

FR2.4 Content Categorization: The system must automatically categorize scraped content into predefined or AI-determined categories.

FR2.5 Named Entity Recognition (NER): The system must extract named entities (e.g., people, places, organizations) from text content.

FR2.6 Language Detection: The system must detect the primary language of the scraped text content.

FR2.7 Content Quality Assessment: The system must provide an AI-based assessment of content quality or readability.

FR2.8 AI Client Initialization: The system must securely initialize AI clients using API keys (loaded from environment variables).

4.3 User Interfaces
#### 4.3.1 Web UI (`web_ui.py`, `templates/scraper.html`, `templates/chat.html`)
* **FR3.1.1 Single URL Scraping:** The Web UI must provide an interface to scrape a single URL with options for AI provider and image extraction.
* **FR3.1.2 Multiple URL Scraping:** The Web UI must allow users to input a list of URLs (one per line) for batch scraping, with options for AI provider and delay.
* **FR3.1.3 Real-time Feedback:** The Web UI must display scraping progress and results dynamically.
* **FR3.1.4 Scraping History View:** The Web UI must display a history of scraped pages for the current session.
* **FR3.1.5 Analytics Dashboard:** The Web UI must present an analytics dashboard showing overall scraping statistics and popular domains.
* **FR3.1.6 Chat Interface:** The Web UI must include a chat interface (`chat.html`) for conversational interaction with the scraping and AI functionalities.
* **FR3.1.7 Session Management (Web):** The Web UI must manage user sessions to maintain context and history.
* **FR3.1.8 Clear Session/History:** The Web UI must provide an option to clear the current session data or history.
* **FR3.1.9 AI Provider Selection (UI):** The Web UI scraper interface must allow users to select the AI provider for analysis.

#### 4.3.2 CLI Chatbot (`chatbot.py`)
* **FR3.2.1 Conversational Interaction:** The chatbot must allow users to initiate scraping and analysis tasks using natural language commands.
* **FR3.2.2 Intent Recognition:** The chatbot must parse user input to identify intents (e.g., scrape, analyze, show links) and extract parameters (e.g., URLs).
* **FR3.2.3 Contextual Responses:** The chatbot must maintain conversation context to provide relevant responses.
* **FR3.2.4 Command Help:** The chatbot must provide a help command listing available functionalities.
* **FR3.2.5 Session Statistics (Chatbot):** The chatbot must be able to display statistics for the current session.
* **FR3.2.6 AI Provider Selection (Chatbot):** The chatbot must allow configuration or selection of the AI provider for its operations.

#### 4.3.3 Direct CLI (`main.py`)
* **FR3.3.1 Single URL Scraping (CLI):** The CLI must allow scraping a single URL via command-line arguments.
* **FR3.3.2 Multiple URL Scraping (CLI):** The CLI must allow scraping multiple URLs specified as arguments or from a file.
* **FR3.3.3 Output Options (CLI):** The CLI must support saving results to a JSON file.
* **FR3.3.4 Verbose Mode (CLI):** The CLI must offer a verbose mode for detailed output.
* **FR3.3.5 Interactive Mode (CLI):** The CLI must provide an interactive prompt for executing commands.
* **FR3.3.6 Example Execution (CLI):** The CLI must allow running predefined example scraping scenarios.

4.4 Data Management & Persistence (database_service.py, models.py)
FR4.1 Database Storage: The system must use a PostgreSQL database (via SQLAlchemy) to store data.

FR4.2 Session Persistence: Scraping session information (ID, creation time, activity, stats) must be stored.

FR4.3 Scraped Page Data Storage: Detailed information for each scraped page must be stored, including URL, domain, title, status code, content length, text content, metadata, and any errors.

FR4.4 AI Analysis Storage: AI-generated results (summary, sentiment, category, entities, language, quality score) must be stored in relation to the scraped page.

FR4.5 Extracted Links Storage: Information about links extracted from pages must be stored.

FR4.6 Extracted Entities Storage: Named entities extracted by AI must be stored.

FR4.7 Aggregated Statistics: The system must store and update aggregated statistics (e.g., total pages scraped, popular domains).

FR4.8 Data Retrieval: The system must provide functions to retrieve session history, page details, and analytics data.

FR4.9 Database Schema: The database schema must be defined using SQLAlchemy models (ScrapingSession, ScrapedPage, ExtractedLink, ExtractedEntity, ScrapingStatistics, PopularDomain).

4.5 Configuration & Customization
FR5.1 API Key Management: AI API keys must be configurable via environment variables for security.

FR5.2 Scraping Delay Configuration: Users must be able to configure the delay between scraping requests.

FR5.3 Custom Headers: The core scraper must allow users to specify custom HTTP headers.

FR5.4 Selective Data Extraction: Users should be able to specify (programmatically or via UI options) whether to extract images, links, etc.

FR5.5 Custom CSS Selectors (Web UI): The Web UI should allow users to specify custom CSS selectors for targeted scraping.

4.6 Error Handling & Reporting
FR6.1 Network Error Handling: The system must gracefully handle common network errors (timeouts, DNS issues, connection errors).

FR6.2 HTTP Error Handling: The system must handle HTTP error status codes (e.g., 404, 500) and report them.

FR6.3 AI API Error Handling: The system must handle errors from AI API calls (e.g., invalid key, rate limits, API downtime) and provide informative messages or fallbacks.

FR6.4 Parsing Error Handling: The system must handle potential errors during HTML parsing.

FR6.5 User Feedback: Errors must be clearly communicated to the user through the respective interface.

FR6.6 Logging: The system should implement logging for debugging and monitoring purposes.

4.7 Utility Functions (utils.py)
FR7.1 Text Cleaning: Provide functions to clean and normalize extracted text.

FR7.2 URL Validation & Parsing: Provide functions to validate, normalize, and parse URLs (extract domain, path, etc.).

FR7.3 Link Filtering: Provide functions to filter links (e.g., internal vs. external).

FR7.4 Data Extraction Utilities: Provide helper functions to extract specific patterns like emails or phone numbers from text (though current utils.py focuses more on URL and text cleaning).

5. Non-Functional Requirements
NFR1. Performance:

NFR1.1 Response Time (Web UI): Web UI interactions for scraping single, simple pages should ideally complete within 5-15 seconds (excluding AI analysis time, which depends on external APIs).

NFR1.2 Batch Processing: The system should efficiently process batches of URLs, respecting configured delays.

NFR1.3 AI API Latency: The system should handle potential latency from external AI APIs gracefully, providing feedback to the user.

NFR2. Scalability:

NFR2.1 Concurrent Users (Web UI): The Flask web server should handle a reasonable number of concurrent users (e.g., 5-10 for a development setup) without significant degradation.

NFR2.2 Database Growth: The database schema should support a growing amount of scraped data and session history.

NFR3. Reliability:

NFR3.1 Uptime: The web UI should aim for high availability if deployed.

NFR3.2 Error Recovery: The system should recover gracefully from non-fatal errors (e.g., failure to scrape one URL in a batch should not stop the entire batch).

NFR3.3 Data Integrity: Data stored in the database must be accurate and consistent.

NFR4. Usability:

NFR4.1 Web UI Intuition: The web interface should be intuitive and easy to navigate for users with basic web literacy.

NFR4.2 Chatbot Naturalness: The chatbot should understand common phrasings for scraping and analysis requests.

NFR4.3 CLI Clarity: The direct CLI should have clear arguments, help messages, and output.

NFR4.4 URL Input Flexibility: Users should not be required to input "http://" or "https://" for URLs.

NFR5. Security:

NFR5.1 API Key Protection: API keys for AI services must be stored securely (e.g., environment variables) and not exposed in client-side code or logs.

NFR5.2 Input Sanitization (Web UI): Inputs in the Web UI should be sanitized to prevent common web vulnerabilities (e.g., XSS), although this is not explicitly detailed in the current Python backend code.

NFR5.3 Database Security: Standard database security practices should be followed for the PostgreSQL instance.

NFR6. Maintainability:

NFR6.1 Code Modularity: The codebase is organized into distinct modules (UI, core scraper, AI enhancement, database, utils), which should be maintained.

NFR6.2 Code Readability: Code should be well-commented and follow Python best practices (PEP 8).

NFR6.3 Dependency Management: Project dependencies should be clearly defined (e.g., in a requirements.txt file - not provided but implied).

NFR7. Extensibility:

NFR7.1 Adding New AI Providers: The architecture should facilitate the addition of new AI service providers with relative ease.

NFR7.2 Adding New Scraping Features: The WebScraper class should be extensible for new data extraction methods.

NFR7.3 Adding New UI Features: The Flask structure should allow for adding new web pages or API endpoints.

6. Assumptions and Dependencies
Python Environment: Python 3.8+ is assumed.

External Libraries: Dependencies like Flask, SQLAlchemy, Requests, BeautifulSoup, OpenAI, Anthropic, Google Generative AI client libraries must be installed.

PostgreSQL Database: A running PostgreSQL instance is required and accessible for data persistence.

AI API Access: Valid API keys for the selected AI providers (OpenAI, Anthropic, Google Gemini) are required for AI features to function. These must be configured as environment variables.

Network Connectivity: The system requires internet access to fetch web pages and communicate with AI APIs.

User Knowledge: Users are expected to understand basic web concepts (URLs) and the ethical implications of web scraping.

7. Future Considerations / Potential Enhancements
Advanced Scraping Techniques:

JavaScript rendering support (e.g., using Selenium or Playwright).

Proxy rotation and management.

Handling CAPTCHAs (though this is complex and often discouraged).

Login and session management for authenticated scraping.

Enhanced AI Capabilities:

More sophisticated content understanding (e.g., relationship extraction, event detection).

Image analysis using multimodal AI models.

AI-assisted selector generation.

Improved User Interface & UX:

Interactive data visualization in the Web UI analytics.

User authentication and multi-user support.

Saving and managing scraping configurations/projects.

Real-time collaborative scraping sessions.

Deployment & Operations:

Dockerization for easier deployment.

Scheduled scraping tasks (cron jobs).

More detailed logging and monitoring dashboards.

Output & Export:

Exporting data in various formats (CSV, Excel, etc.).

Direct integration with data analysis tools or platforms.

Distributed Scraping:

Ability to distribute scraping tasks across multiple workers for large-scale operations.

8. Success Metrics
User Adoption: Number of active users or sessions (if deployed and trackable).

Task Completion Rate: Percentage of scraping and analysis tasks completed successfully.

Feature Usage: Frequency of use for different features (e.g., AI analysis, batch scraping, specific UI).

User Satisfaction: Qualitative feedback from users (if surveys or feedback mechanisms are implemented).

Data Throughput: Volume of data successfully scraped and analyzed over time.

Stability: Low error rates and system crashes.

Performance: Adherence to defined response time targets.
