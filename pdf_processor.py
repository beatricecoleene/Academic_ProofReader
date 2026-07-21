import fitz
import re

class PDFProcessor:
    def __init__(self):
        pass

    def load_pdf(self, pdf_path):
        self.original_doc = fitz.open(pdf_path)
        extracted_text = ""
        self.text_blocks = []
        
        for page_num in range(len(self.original_doc)):
            page = self.original_doc[page_num]
            
            # get text blocks with position information
            blocks = page.get_text("dict")
            
            for block in blocks["blocks"]:
                if "lines" in block:  # text block
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            text = span["text"]
                            line_text += text
                            
                            # store dets
                            self.text_blocks.append({
                                'page': page_num,
                                'text': text,
                                'bbox': span["bbox"], 
                                'font': span.get("font", ""),
                                'size': span.get("size", 12),
                                'flags': span.get("flags", 0),
                                'color': span.get("color", 0)
                            })
                        
                        extracted_text += line_text + "\n"
                    extracted_text += "\n"
        
        return extracted_text.strip()
    
    def create_changes(self, corrections, output_path):
        new_doc = fitz.open()

        try:
            # Process ALL pages first, then save at the end
            for page_num in range(len(self.original_doc)):
                original_page = self.original_doc[page_num] # original page num

                # set same dimension to new doc from orig doc
                new_page = new_doc.new_page(width=original_page.rect.width, height=original_page.rect.height)

                # copy content (images or drawings) from original page to new page
                new_page.show_pdf_page(new_page.rect, self.original_doc, page_num)

                text = original_page.get_text("dict") 

                for each in text["blocks"]:
                    if "lines" in each:
                        for line in each["lines"]:
                            for span in line["spans"]:
                                original_text = span["text"]
                                corrected_text = original_text

                                # appy changes
                                words = re.findall(r'\b\w+\b', original_text)
                                corrected_text = original_text
                                
                                # check for phrase corrections (GRAMMAR)
                                for correction_key, replacement in corrections.items():
                                    if ' ' in correction_key:  # ifphrase
                                        pattern = re.escape(correction_key)
                                        corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
                                

                                for word in words:
                                    if word.lower() in corrections:
                                        # replace
                                        replace = corrections[word.lower()]

                                        
                                        if word.isupper():
                                            replace = replace.upper()
                                        elif word.islower():
                                            replace = replace.lower()
                                        elif word.istitle():
                                            replace = replace.title()

                                        corrected_text = re.sub(r'\b' + re.escape(word) + r'\b', 
                                                                replace, 
                                                                corrected_text, 
                                                                flags=re.IGNORECASE)

                                # if text was corrected, update it in the PDF
                                if corrected_text != original_text:
                                    rectangle = fitz.Rect(span["bbox"])
                                    
                                    # clear original text by drawing white rectangle
                                    new_page.draw_rect(rectangle, color=(1, 1, 1), fill=(1, 1, 1))

                                    # insert corrected text
                                    fonts = { # fallback fonts
                                        "Times-Roman": "times",
                                        "Helvetica": "helv",
                                        "Courier": "cour",
                                    }
                                    font_name = span.get("font", "")
                                    font_name = fonts.get(font_name, "helv")

                                    font_size = span.get("size", 12)
                                    font_color = span.get("color", 0)

                                    try:
                                        new_page.insert_text(
                                            rectangle,
                                            corrected_text,
                                            fontsize=font_size,
                                            fontname=font_name,
                                            color=font_color
                                        )
                                    except Exception as e:
                                        # print(f"Error inserting text: {e}, using fallback method")
                                        new_page.insert_text(
                                            (rectangle.x0, rectangle.y0 + font_size * 0.8),
                                            corrected_text,
                                            fontsize=font_size,
                                            fontname="helv",
                                        )

            new_doc.save(output_path)
            print(f"Successfully saved PDF with {len(self.original_doc)} pages to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return False
            
        finally:
            # close new doc
            if new_doc:
                new_doc.close()

    def close(self):
        if hasattr(self, 'original_doc') and self.original_doc:
            self.original_doc.close()

if __name__ == "__main__":
    pdf_processor = PDFProcessor()
    text = pdf_processor.load_pdf("pdf_test/essay.pdf")
    print(text)