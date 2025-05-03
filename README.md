# Auto Publisher

This repo automatically takes content and creates a pdf file or kindle file that can be used for publishing a book. 

The initial books of interest are for learning to read by little children and for SEND kids.

It does the following:

1. Automatically generates images to appear in the book - based on the content which could be in word of text format.
2. Automatically generates page layouts and book layouts.
3. Automatically creates a PDF file that can be used for publishing.
4. Automatically creates an EPUB file for digital reading.
5. (Optional) Automatically converts EPUB to Kindle-compatible formats.

## Development Plan

1.  **Input Processing:** Read and parse input content (Word, text). Extract key information for image generation and layout.
2.  **Image Generation:** Use an AI model to generate images based on the parsed content.
3.  **Layout Generation:** Design page layouts, placing text and images appropriately.
4.  **Output Generation (PDF):** Compile the laid-out content and images into a print-ready PDF file.
5.  **Output Generation (EPUB):** Create standard-compliant EPUB files for digital reading.
6.  **Output Generation (Kindle - Optional):** Convert EPUB to Kindle-compatible format.

## Detailed Task List

*   **Project Setup:**
    *   Initialize Git repository.
    *   Set up project structure (folders for source, assets, output).
    *   Choose programming language and set up environment (e.g., Python with venv).
    *   Define dependencies (libraries for text processing, image generation, PDF creation).
*   **Input Module:**
    *   Implement plain text file reader.
    *   Implement Word (.docx) file reader (e.g., using `python-docx`).
    *   Develop content parsing logic (identify chapters, paragraphs, image prompts/keywords).
*   **Image Generation Module:**
    *   Select and integrate with an AI image generation API/library (e.g., Stable Diffusion, DALL-E API).
    *   Implement logic to generate prompts from parsed content.
    *   Handle API calls, image retrieval, and basic processing (resizing).
    *   Manage API keys and potential costs/rate limits.
*   **Layout Module:**
    *   Define basic page templates (e.g., title page, content page with image, text-only page).
    *   Integrate with an LLM (like GPT-4, Claude) to assist with layout decisions:
        *   Generating appropriate layout templates based on content type
        *   Determining optimal text-to-image ratios for children's books
        *   Suggesting age-appropriate typography and spacing
        *   Adapting layouts for SEND accessibility requirements
    *   Implement logic to flow text onto pages.
    *   Implement logic to place images relative to text.
    *   Handle pagination, margins, and basic styling.
*   **PDF Generation Module:**
    *   Select and integrate a PDF generation library (e.g., ReportLab, FPDF2, WeasyPrint).
    *   Implement logic to render the designed layouts (text, images) into PDF pages.
    *   Ensure correct resolution and print-ready settings.
*   **EPUB Generation Module:**
    *   Select and integrate an EPUB generation library (e.g., EbookLib, Calibre's ebook-convert).
    *   Implement HTML/CSS templates for EPUB content.
    *   Ensure responsive layouts that work well on different screen sizes.
    *   Add proper metadata, table of contents, and navigation.
    *   Implement accessibility features (alt text, semantic markup).
    *   Validate EPUB output against standards.
*   **Kindle Generation Module (Optional):**
    *   Convert EPUB to Kindle formats (KF8/MOBI) using tools like Calibre or Amazon's KindleGen.
    *   Test compatibility across Kindle devices and apps.
    *   Optimize for Kindle-specific features and limitations.
*   **Configuration & CLI:**
    *   Implement configuration file handling (e.g., YAML, JSON) for settings (API keys, layout styles, output formats).
    *   Create a command-line interface (CLI) to run the tool (e.g., using `argparse`).
*   **Testing:**
    *   Write unit tests for individual modules (parsing, image generation logic, layout logic).
    *   Write integration tests for the end-to-end workflow.
*   **Documentation:**
    *   Update README with detailed usage instructions.
    *   Add code comments and potentially generate API documentation.

## Open Questions / Challenges

*   **Content Parsing Robustness:** How to reliably extract meaningful image prompts and structure from diverse and potentially messy input documents?
*   **Image Quality & Relevance:** How to ensure generated images are high quality, stylistically consistent, and accurately reflect the text content? Prompt engineering will be key.
*   **Automated Layout Sophistication:** Creating truly *good* automated layouts that adapt well to varying amounts of text and image sizes is complex. How much manual control vs. automation is needed?
*   **Handling Complex Word Docs:** Parsing Word documents with complex formatting (tables, footnotes, styles) can be challenging.
*   **Image Generation Costs & Speed:** AI image generation can be slow and potentially costly depending on the service and volume.
*   **Kindle Formatting Fidelity:** Achieving consistent and high-quality formatting across different Kindle devices/apps, especially with complex layouts, can be difficult. EPUB might be a more flexible intermediate target than direct MOBI/KDP generation.
*   **Dependency Management:** Integrating various external libraries and APIs requires careful dependency management.
*   **Error Handling:** Robustly handling errors like API failures, file not found, parsing errors, layout conflicts.


