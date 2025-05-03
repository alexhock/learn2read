"""
EPUB Generator - Creates EPUB files from book layouts
"""

import os
import tempfile
import shutil
import zipfile
from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET
from datetime import datetime
import uuid
import html

class EPUBGenerator:
    """Generates EPUB files from book content"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.uuid = str(uuid.uuid4())
        
    def generate_epub(self, book_content: Dict[str, Any], output_path: str) -> str:
        """
        Generate an EPUB file from book content
        
        Args:
            book_content: Dictionary with metadata and content sections
            output_path: Path where the EPUB file will be saved
            
        Returns:
            Path to the generated EPUB file
        """
        # Create a temporary directory to build the EPUB structure
        with tempfile.TemporaryDirectory() as epub_dir:
            # Create the standard EPUB directory structure
            os.makedirs(os.path.join(epub_dir, "META-INF"))
            os.makedirs(os.path.join(epub_dir, "OEBPS"))
            os.makedirs(os.path.join(epub_dir, "OEBPS", "images"))
            os.makedirs(os.path.join(epub_dir, "OEBPS", "styles"))
            
            # Create required files
            self._create_mimetype_file(epub_dir)
            self._create_container_xml(epub_dir)
            
            # Create content
            metadata = book_content.get("metadata", {})
            sections = book_content.get("sections", [])
            
            # Create OPF file (package document)
            self._create_opf_file(epub_dir, metadata, sections)
            
            # Create CSS
            self._create_css_file(epub_dir)
            
            # Create HTML content files
            self._create_content_files(epub_dir, sections, metadata)
            
            # Create NCX file (navigation)
            self._create_ncx_file(epub_dir, metadata, sections)
            
            # Copy images
            self._process_images(epub_dir, sections)
            
            # Create the EPUB zip file
            self._create_epub_zip(epub_dir, output_path)
            
            # Validate EPUB (in a production version, you might use epubcheck)
            # self._validate_epub(output_path)
            
        return output_path
        
    def _create_mimetype_file(self, epub_dir: str):
        """Create the mimetype file (must be first in the ZIP and uncompressed)"""
        with open(os.path.join(epub_dir, "mimetype"), 'w') as f:
            f.write("application/epub+zip")
            
    def _create_container_xml(self, epub_dir: str):
        """Create META-INF/container.xml pointing to the OPF file"""
        container = ET.Element("container", version="1.0", xmlns="urn:oasis:names:tc:opendocument:xmlns:container")
        rootfiles = ET.SubElement(container, "rootfiles")
        ET.SubElement(rootfiles, "rootfile", 
                     {"full-path": "OEBPS/content.opf", 
                      "media-type": "application/oebps-package+xml"})
        
        tree = ET.ElementTree(container)
        tree.write(os.path.join(epub_dir, "META-INF", "container.xml"), 
                  encoding="utf-8", xml_declaration=True)
                  
    def _create_opf_file(self, epub_dir: str, metadata: Dict, sections: List):
        """Create the OPF file with metadata, manifest, and spine"""
        package = ET.Element("package", 
                           {"xmlns": "http://www.idpf.org/2007/opf",
                            "version": "3.0",
                            "unique-identifier": "book-id"})
                            
        # Metadata
        meta_elem = ET.SubElement(package, "metadata", 
                               {"xmlns:dc": "http://purl.org/dc/elements/1.1/",
                                "xmlns:opf": "http://www.idpf.org/2007/opf"})
        
        # Required metadata elements
        ET.SubElement(meta_elem, "dc:identifier", id="book-id").text = metadata.get("identifier", self.uuid)
        ET.SubElement(meta_elem, "dc:title").text = metadata.get("title", "Untitled")
        ET.SubElement(meta_elem, "dc:language").text = metadata.get("language", "en")
        ET.SubElement(meta_elem, "dc:creator").text = metadata.get("creator", "Unknown Author")
        ET.SubElement(meta_elem, "meta", {"property": "dcterms:modified"}).text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Manifest - list all files
        manifest = ET.SubElement(package, "manifest")
        
        # Add NCX (required for legacy reading systems)
        ET.SubElement(manifest, "item", 
                    {"id": "ncx", 
                     "href": "toc.ncx", 
                     "media-type": "application/x-dtbncx+xml"})
                     
        # Add CSS
        ET.SubElement(manifest, "item", 
                    {"id": "css", 
                     "href": "styles/style.css", 
                     "media-type": "text/css"})
                     
        # Add all HTML files
        ET.SubElement(manifest, "item", 
                    {"id": "title-page", 
                     "href": "title.xhtml", 
                     "media-type": "application/xhtml+xml",
                     "properties": "nav"})  # title page includes navigation
                     
        for i, section in enumerate(sections):
            ET.SubElement(manifest, "item", 
                        {"id": f"section-{i}", 
                         "href": f"section-{i}.xhtml", 
                         "media-type": "application/xhtml+xml"})
        
        # Add images
        for i, section in enumerate(sections):
            if section.get("image"):
                # In a real implementation, you'd handle the actual image path and format
                image_ext = "jpg"  # Would determine from actual image
                ET.SubElement(manifest, "item", 
                           {"id": f"image-{i}", 
                            "href": f"images/image-{i}.{image_ext}", 
                            "media-type": f"image/{image_ext}"})
        
        # Spine - reading order
        spine = ET.SubElement(package, "spine", toc="ncx")
        ET.SubElement(spine, "itemref", idref="title-page")
        
        for i in range(len(sections)):
            ET.SubElement(spine, "itemref", idref=f"section-{i}")
            
        # Write to file
        tree = ET.ElementTree(package)
        tree.write(os.path.join(epub_dir, "OEBPS", "content.opf"), 
                 encoding="utf-8", xml_declaration=True)
                 
    def _create_css_file(self, epub_dir: str):
        """Create a CSS file for styling"""
        css = """
        body {
            font-family: sans-serif;
            line-height: 1.5;
            margin: 1em;
        }
        h1, h2, h3 {
            color: #333;
            line-height: 1.2;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        .image-container {
            text-align: center;
            margin: 1em 0;
        }
        """
        
        with open(os.path.join(epub_dir, "OEBPS", "styles", "style.css"), 'w') as f:
            f.write(css)
            
    def _create_content_files(self, epub_dir: str, sections: List, metadata: Dict):
        """Create HTML content files for title page and each section"""
        # Create title page
        self._create_title_page(epub_dir, metadata, sections)
        
        # Create content sections
        for i, section in enumerate(sections):
            self._create_section_page(epub_dir, section, i)
            
    def _create_title_page(self, epub_dir: str, metadata: Dict, sections: List):
        """Create the title page with navigation"""
        xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
        <head>
            <title>{html.escape(metadata.get('title', 'Untitled'))}</title>
            <link rel="stylesheet" type="text/css" href="styles/style.css" />
            <meta charset="utf-8"/>
        </head>
        <body>
            <header>
                <h1>{html.escape(metadata.get('title', 'Untitled'))}</h1>
                <h2>{html.escape(metadata.get('creator', 'Unknown Author'))}</h2>
            </header>
            
            <nav epub:type="toc" id="toc">
                <h2>Table of Contents</h2>
                <ol>
                    <li><a href="title.xhtml">Title Page</a></li>
        """
        
        # Add TOC entries for sections
        for i, section in enumerate(sections):
            first_text = next((chunk.get('text', '') for chunk in section.get('text_chunks', []) if chunk.get('text')), f"Section {i+1}")
            # Use first few words as title
            title = " ".join(first_text.split()[:5]) + "..."
            xhtml += f'            <li><a href="section-{i}.xhtml">{html.escape(title)}</a></li>\n'
            
        xhtml += """        </ol>
            </nav>
        </body>
        </html>"""
        
        with open(os.path.join(epub_dir, "OEBPS", "title.xhtml"), 'w', encoding='utf-8') as f:
            f.write(xhtml)
            
    def _create_section_page(self, epub_dir: str, section: Dict, index: int):
        """Create an HTML file for a content section"""
        text_chunks = section.get('text_chunks', [])
        image = section.get('image')
        
        xhtml = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <title>Section</title>
            <link rel="stylesheet" type="text/css" href="styles/style.css" />
            <meta charset="utf-8"/>
        </head>
        <body>
        """
        
        # Add image if present
        if image:
            alt_text = self._get_alt_text(image, text_chunks)
            image_ext = "jpg"  # Would determine from actual image
            xhtml += f"""    <div class="image-container">
                <img src="images/image-{index}.{image_ext}" alt="{html.escape(alt_text)}" />
            </div>
            """
            
        # Add text content
        for chunk in text_chunks:
            text = chunk.get('text', '')
            style = chunk.get('style', 'normal')
            
            if not text:
                continue
                
            if style == 'heading':
                xhtml += f"    <h1>{html.escape(text)}</h1>\n"
            elif style == 'subheading':
                xhtml += f"    <h2>{html.escape(text)}</h2>\n"
            else:
                xhtml += f"    <p>{html.escape(text)}</p>\n"
                
        xhtml += """</body>
        </html>"""
        
        with open(os.path.join(epub_dir, "OEBPS", f"section-{index}.xhtml"), 'w', encoding='utf-8') as f:
            f.write(xhtml)
            
    def _create_ncx_file(self, epub_dir: str, metadata: Dict, sections: List):
        """Create NCX navigation file (for legacy e-readers)"""
        ncx = ET.Element("ncx", 
                       {"xmlns": "http://www.daisy.org/z3986/2005/ncx/",
                        "version": "2005-1"})
        
        # Head
        head = ET.SubElement(ncx, "head")
        ET.SubElement(head, "meta", name="dtb:uid", content=metadata.get("identifier", self.uuid))
        ET.SubElement(head, "meta", name="dtb:depth", content="1")
        ET.SubElement(head, "meta", name="dtb:totalPageCount", content="0")
        ET.SubElement(head, "meta", name="dtb:maxPageNumber", content="0")
        
        # Title
        ET.SubElement(ncx, "docTitle").text = metadata.get("title", "Untitled")
        
        # Nav map
        nav_map = ET.SubElement(ncx, "navMap")
        
        # Title page
        nav_point = ET.SubElement(nav_map, "navPoint", id="title", playOrder="1")
        ET.SubElement(nav_point, "navLabel").text = "Title Page"
        ET.SubElement(nav_point, "content", src="title.xhtml")
        
        # Sections
        for i, section in enumerate(sections):
            first_text = next((chunk.get('text', '') for chunk in section.get('text_chunks', []) if chunk.get('text')), f"Section {i+1}")
            # Use first few words as title
            title = " ".join(first_text.split()[:5]) + "..."
            
            nav_point = ET.SubElement(nav_map, "navPoint", id=f"section-{i}", playOrder=str(i+2))
            ET.SubElement(nav_point, "navLabel").text = title
            ET.SubElement(nav_point, "content", src=f"section-{i}.xhtml")
            
        tree = ET.ElementTree(ncx)
        tree.write(os.path.join(epub_dir, "OEBPS", "toc.ncx"),
                 encoding="utf-8", xml_declaration=True)
                 
    def _process_images(self, epub_dir: str, sections: List):
        """Process and copy images to the EPUB"""
        for i, section in enumerate(sections):
            image = section.get('image')
            if image:
                # In a real implementation, you'd handle actual image processing
                # This would copy the image file to the EPUB
                image_path = getattr(image, 'path', str(image))
                if os.path.exists(image_path):
                    # Determine image type and copy
                    ext = os.path.splitext(image_path)[1].lower()
                    if ext.startswith('.'):
                        ext = ext[1:]
                    
                    # Copy the image
                    shutil.copy(
                        image_path, 
                        os.path.join(epub_dir, "OEBPS", "images", f"image-{i}.{ext}")
                    )
                    
    def _get_alt_text(self, image, text_chunks):
        """Get alt text for an image (accessibility)"""
        # Use existing alt text if available
        if hasattr(image, 'alt_text') and image.alt_text:
            return image.alt_text
            
        # Generate from surrounding text
        for chunk in text_chunks:
            text = chunk.get('text', '')
            if text:
                # Extract first sentence or up to 100 chars
                alt_text = text.split('.')[0]
                if len(alt_text) > 100:
                    alt_text = alt_text[:97] + "..."
                return alt_text
                
        return "Book illustration"
                
    def _create_epub_zip(self, epub_dir: str, output_path: str):
        """Create the final EPUB zip file with proper order"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub_zip:
            # mimetype must be first and uncompressed
            epub_zip.write(
                os.path.join(epub_dir, "mimetype"),
                "mimetype", 
                compress_type=zipfile.ZIP_STORED
            )
            
            # Add all other files
            for root, dirs, files in os.walk(epub_dir):
                for file in files:
                    if file != "mimetype":  # already handled
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, epub_dir)
                        epub_zip.write(full_path, rel_path)
