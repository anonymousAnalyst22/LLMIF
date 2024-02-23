import sys
import asyncio
import re
import shutil
import fitz
import json
from pprint import pprint
import numpy as np
from pathlib import Path
from tempfile import NamedTemporaryFile
import logging
import re

def create_temporary_pdf(original_pdf):
   tmp_path = None
   suffix = Path(original_pdf).suffix
   with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
       with open(original_pdf, 'rb') as original_content:
           shutil.copyfileobj(original_content, tmp)
       tmp_path = Path(tmp.name)
   return str(tmp_path)


def preprocess(text:'str'):
   text_segs = text.split('\n')
   filter_lineno_texts = []
   for text_seg in text_segs:
       text_seg = text_seg.strip()
       try:
           dummy_number = int(text_seg)
       except:
           filter_lineno_texts.append(text_seg)
   text = ' '.join(filter_lineno_texts)
   text = text.replace('\n', ' ')
   text = re.sub('\s+', ' ', text)
   return text

def pdf_to_text(path, start_page=1, end_page=None):
   doc = fitz.open(path)
   total_pages = doc.page_count

   if end_page is None:
       end_page = total_pages
   text_list = []
   for i in range(start_page - 1, end_page):
       text = doc.load_page(i).get_text("text")
       text = preprocess(text)
       text_list.append(text)
   doc.close()
   return text_list

def get_pdf_outline(path):
    doc = fitz.open(path)
    outline = doc.get_toc()
    return outline


def text_to_chunks(texts:'list[str]', word_length=300, start_page=1):
   text_toks = [t.split(' ') for t in texts]
   chunks = []
   for idx, words in enumerate(text_toks):
       for i in range(0, len(words), word_length):
           chunk = words[i : i + word_length]
           if (
               (i + word_length) > len(words)
               and (len(chunk) < word_length)
               and (len(text_toks) != (idx + 1))
           ):
               text_toks[idx + 1] = chunk + text_toks[idx + 1]
               continue
           chunk = ' '.join(chunk).strip()
           chunk = f'[Page no. {idx+start_page}]' + ' ' + '"' + chunk + '"'
           chunks.append(chunk)
   return chunks


def split_pdf_pages(spec_file):
   page_texts = pdf_to_text(spec_file)
   n_characters = len(''.join(page_texts))
   print(f"Total # characters : {n_characters}. Total # pages: {len(page_texts)}")
   return page_texts

def text_purify(txt:str):
   return txt.strip().replace(' ', '').lower()


