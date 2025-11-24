---
name: web_scraper
description: A skill to scrape content from web pages
version: 1.0.0
author: Test Developer
tags: [web, scraping, content]
---

# Web Scraper Skill

This skill allows Claude to scrape content from web pages.

## Instructions

When a user requests to scrape content from a web page:

1. Extract the URL from the user's request
2. Validate that the URL is well-formed
3. Scrape the content from the page
4. Return the scraped content in a structured format

## Examples

- "Scrape content from https://example.com"
- "Get the text content from this page: https://news.example.com/article"

## Guidelines

- Always validate URLs before attempting to scrape
- Handle errors gracefully if scraping fails
- Respect robots.txt and rate limiting
- Return content in a readable format
