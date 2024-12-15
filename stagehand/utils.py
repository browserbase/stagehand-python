EXTRACT_SCHEMA_PROMPT = """
Convert the following schema to a JSON schema as required by the Stagehand API:

{schema}
 
**Instructions for providing the schema:**

- The \`schema\` should be a valid JSON Schema object that defines the structure of the data to extract.
- Use standard JSON Schema syntax.
- The server will convert the JSON Schema to a Zod schema internally.

**Example schemas:**

1. **Extracting a list of search result titles:**

\`\`\`json
{
"type": "object",
"properties": {
    "searchResults": {
    "type": "array",
    "items": {
        "type": "string",
        "description": "Title of a search result"
    }
    }
},
"required": ["searchResults"]
}
\`\`\`

2. **Extracting product details:**

\`\`\`json
{
"type": "object",
"properties": {
    "name": { "type": "string" },
    "price": { "type": "string" },
    "rating": { "type": "number" },
    "reviews": {
    "type": "array",
    "items": { "type": "string" }
    }
},
"required": ["name", "price", "rating", "reviews"]
}
\`\`\`

**Example usage:**

- **Instruction**: "Extract the titles and URLs of the main search results, excluding any ads."
- **Schema**:
\`\`\`json
{
    "type": "object",
    "properties": {
    "results": {
        "type": "array",
        "items": {
        "type": "object",
        "properties": {
            "title": { "type": "string", "description": "The title of the search result" },
            "url": { "type": "string", "description": "The URL of the search result" }
        },
        "required": ["title", "url"]
        }
    }
    },
    "required": ["results"]
}
\`\`\`

**Note:**

- Ensure the schema is valid JSON.
- Use standard JSON Schema types like \`string\`, \`number\`, \`array\`, \`object\`, etc.
- You can add descriptions to help clarify the expected data.

"""