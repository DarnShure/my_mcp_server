## TLDR: This package changes pdfs to element-aware markdown documents for LLM to injest.


## Introduction

Pdf is a document format oriented around portability, and consistent graphical representation. This means that it can can handle documents with hundreds of pages, and it will look the same on all devices. This makes it an obvious choice for business documents, but this makes it hard to work with for serial information extraction.

spatial representations of documents. It was created by Adobe as a proprietary format, but is used as a standard for representing graphical information such as:
- Datasheets for firmware
- Company finanial statements
- Academic papers
All word documents can be exported to pdfs, as printers naturally take pdfs.

In such documents, key information is often embedded in tables and graphs, so reliable extraction of such elements -into nodes- is a neccesary condition for accurate document retrieval in RAG.
In this module, we will use pdfplumber to programatically extract a plain-text table representations from pdfs and docxs.

Note that while it is imporant for RAG in LLM's, multimodal language models naturally circumvent this issue.

### Method 0:
We will approach this naively by just collating the tables at the bottom of each page, regardless of redundancy.

### Method 1:
Diving deeper into the implementation of pdfplumber, we extend the page class to:
     Filter out the objects in the table bounding boxes, extract, format, and inject markdown-formatted-tables into the final string returned by page.extract_text() 

### Method 2:
We try to extract images and table elements in the correct order.

Conclusion:
We hope to understand pdf document formatting more, and maybe write a module that works with all pdfs that we encounter.
However, there are problems with the universality of this tool.

Journal:
There are parts of the pdfminer that I don't understand. There are a couple levels of abstraction that are not finding traction in my mind.