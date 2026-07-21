
from pdf2image import convert_from_path
import pytesseract


class File_Extraction:
    def __init__(self, file_input):
        
        self.file = file_input
        self.output_file = "text_files/booksAndresearches.txt"
        
    def write_file(self, text):
        with open (self.output_file, "a", encoding= "utf-8") as outfile:
            
            outfile.write(text + "\n")
            
        
    def extract_file(self):
        
        pages = convert_from_path(self.file, 300)
        
        for i, page in enumerate(pages):
            
            text = pytesseract.image_to_string(page, config = "--psm 6")
            
    
            
            f_text = f"------Page {i+1}------- \n {text}"
            
        
            self.write_file(text)
    # def main():
    #     fe = File_Extraction
        
# "C:\Users\asus\Downloads\researh1.pdf"
paths =['/mnt/c/Users/asus/Downloads/researh1.pdf', 
        '/mnt/c/Users/asus/Downloads/rs2.pdf',
        '/mnt/c/Users/asus/Downloads/rs3.pdf',
        '/mnt/c/Users/asus/Downloads/r4.pdf',
        '/mnt/c/Users/asus/Downloads/r5.pdf',
        ]

for path in paths:
    

    fe = File_Extraction(path)
    fe.extract_file()





