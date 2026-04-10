# AI Invoice Analyzer

This project is an AI-powered invoice processing system designed to automatically extract key information from invoice images using OCR and intelligent parsing techniques.

## Overview
The system processes invoice images, extracts textual data using OCR (Doctr), and applies rule-based intelligence to identify important fields such as company name, GST number, total amount, and date.

## Features
- Automatic invoice data extraction
- OCR-based text recognition using Doctr
- Intelligent field detection (Company, GST, Date, Total)
- Advanced total amount detection using anchor-based logic
- Visual output with bounding box highlighting
- Supports multiple invoice formats

## Technologies Used
- Python
- OCR (Doctr)
- Image Processing (PIL)
- Flask (Web Application)
- Regular Expressions (Regex)

## Description
The system uses OCR to extract all textual content from invoices and then applies intelligent parsing techniques to identify relevant fields. It uses anchor-based logic to accurately detect the final total amount, even in complex invoice layouts. The output is structured and displayed along with a visual preview highlighting detected fields.

## Output
The system successfully extracts key invoice details and highlights detected regions on the invoice image. It provides structured output without manual intervention.

## Note
This repository contains a simplified version of the project for demonstration purposes.

## Result
The system successfully extracts key information such as company name, GST number, date, and total amount from invoice images with high accuracy. It works across different invoice formats and provides structured output along with a visual preview highlighting detected fields.
