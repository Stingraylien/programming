#!/bin/bash
# examples/curl_examples.sh
# cURL command examples for Black Box API

# Example 1: Health Check
echo "=== Health Check ==="
curl -X GET http://localhost:8000/api/health
echo -e "\n\n"

# Example 2: Get Configuration
echo "=== Get Configuration ==="
curl -X GET http://localhost:8000/api/config | jq .
echo -e "\n\n"

# Example 3: Generate Question Bank
echo "=== Generate Question Bank ==="
curl -X POST http://localhost:8000/api/generate-question-bank \
  -F "materials=@sample_material.pdf" \
  -F "question_types=true_false" \
  -F "question_types=single_choice" \
  -F "difficulty=medium" \
  -F "language=zh-TW" | jq .
echo -e "\n\n"

# Example 4: Multiple Files
echo "=== Generate with Multiple Files ==="
curl -X POST http://localhost:8000/api/generate-question-bank \
  -F "materials=@material1.pptx" \
  -F "materials=@material2.pdf" \
  -F "question_types=single_choice" \
  -F "question_types=multiple_choice" \
  -F "difficulty=hard" \
  -F "language=en-US" | jq .
echo -e "\n\n"

# Example 5: Download File
echo "=== Download Generated File ==="
# Replace FILENAME with actual output filename from previous response
# curl -X GET http://localhost:8000/api/download/training_question_bank_20260324_120000.xlsx \
#   -o downloaded_file.xlsx