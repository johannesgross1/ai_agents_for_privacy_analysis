#This is the module for the AI Implementation.
#We will use the OpenAI Batch processing API to process the traffic data

import os
import json
import time
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional
from datetime import datetime

# getter for structured output of the detection #
def get_detection_schema(patterns):
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "pii_detection",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "detections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "pattern": {"type": "string"},
                                "detected": {"type": "boolean"},
                                "reasoning": {"type": "string"}
                            },
                            "required": ["pattern", "detected", "reasoning"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["detections"],
                "additionalProperties": False
            }
        }
    }


def get_validation_schema():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "pii_validation",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "confirmed": {"type": "boolean"},
                    "reasoning": {"type": "string"}
                },
                "required": ["confirmed", "reasoning"],
                "additionalProperties": False
            }
        }
    }




load_dotenv()  # Environment Variables laden
class AI_Agent:
    def __init__(self, model: str, temperature: float, max_tokens: int, data_dir: str = "data_thesis"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No OPENAI_API_KEY in the .env found.")
        self.client = OpenAI(api_key=api_key)
        
        # Config-Parameter aus Funktionsargumenten
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.data_dir = data_dir
        

    def create_detection_batch_file(self, traffic: pd.DataFrame, patterns: List[Dict], 
                                    batch_file_path: str) -> str:
        pattern_names = [p['name'] for p in patterns]
        pattern_list = ', '.join(pattern_names)
        tasks = []
        for idx, row in traffic.iterrows():
            if pd.notna(row['request_content']) and str(row['request_content']).strip():
                request_text = str(row['request_content'])
                prompt = f"""Analyze this HTTP request body for PII/PHI patterns.

Pattern-specific test values to detect (search semantically):

Device IDs:
- Device model: Pixel 6A, bluejay
- Resolution: 1080
- Carrier name: nettokom
- OS build: TP1A.220624.021.A1
- API level: 33

Location:
- City: Berlin
- Latitude: 52.5, 52.6
- Longitude: 13.3, 13.4

User Info:
- Name: Freya
- Email address: mhealthcrawl2024@gmail.com
- Advertising ID: 30f17059
- Age: 34
- Date of birth: 1990
- Gender: female

Body Measurements & Fitness:
- Body height: 170 cm
- Body weight: 65 kg
- Body weight goal: 60 kg
- BMI: 22
- Step count: 271 steps, step goals
- Eating habits: vegetarian, diet
- Fitness goals: lose weight, weight loss
- Fitness level: medium, beginner
- Mental wellbeing: stress, lack of sleep, forgetful
- Sleep habits: sleep between 5-6 hours, sleep quality

Female Health:
- Cycle length: 29 days
- Period start date: menstruation start dates
- Period length: 5 days
- Period symptoms: acne, dysmenorrhea, discharge, cravings, mucus
- Birth control: birth control pills, contraception

Medical Info:
- Sexual activity: sexual activity data, condom use
- Body temperature: 37°C
- Heart rate: 70 bpm
- Blood pressure: 100/75 (systolic/diastolic)
- Glucose levels: blood sugar data
- Medical conditions: diabetes, allergies, headache

Request Content: {request_text}

Detect these PII/PHI types: {pattern_list}

For EACH type, return: detected (true/false) and brief reasoning (max 150 chars).
Search semantically - the exact values may appear in different formats or encodings."""
                
                task = {
                    "custom_id": f"detection-{idx}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": self.model,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "response_format": get_detection_schema(patterns),
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a PII/PHI detection expert analyzing mobile health app traffic. Use semantic understanding, not just exact string matching."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                }
                tasks.append(task)
        
        print("Creating detection batch file...")
        os.makedirs(os.path.dirname(batch_file_path) or '.', exist_ok=True)
        with open(batch_file_path, 'w', encoding='utf-8') as f:
            for task in tasks:
                f.write(json.dumps(task) + '\n')
        print(f"Created {batch_file_path} with {len(tasks)} detection requests")
        return batch_file_path
    

###################for debugging of this method, cursor was used to generate parts of the following method##############################################
    def create_validation_batch_file(self, traffic_with_detection: pd.DataFrame, patterns: List[Dict],
                                    batch_file_path: str) -> str:
        tasks = []
        for idx, row in traffic_with_detection.iterrows():
            if pd.notna(row['request_content']) and str(row['request_content']).strip():
                request_text = str(row['request_content'])
                for pattern in patterns:
                    name = pattern['name']
                    if row.get(f'ai_detected_{name}', False):
                        initial_reasoning = row.get(f'ai_reasoning_{name}', '')
###################until this part for debugging of this method, cursor was used to generate parts of the ##############################################
                        
                        prompt = f"""Validate this PII detection.

Pattern-specific test values to detect (search semantically):

Device IDs:
- Device model: Pixel 6A, bluejay
- Resolution: 1080
- Carrier name: nettokom
- OS build: TP1A.220624.021.A1
- API level: 33

Location:
- City: Berlin
- Latitude: 52.5, 52.6
- Longitude: 13.3, 13.4

User Info:
- Name: Freya
- Email address: mhealthcrawl2024@gmail.com
- Advertising ID: 30f17059
- Age: 34
- Date of birth: 1990
- Gender: female

Body Measurements & Fitness:
- Body height: 170 cm
- Body weight: 65 kg
- Body weight goal: 60 kg
- BMI: 22
- Step count: 271 steps, step goals
- Eating habits: vegetarian, diet
- Fitness goals: lose weight, weight loss
- Fitness level: medium, beginner
- Mental wellbeing: stress, lack of sleep, forgetful
- Sleep habits: sleep between 5-6 hours, sleep quality

Female Health:
- Cycle length: 29 days
- Period start date: menstruation start dates
- Period length: 5 days
- Period symptoms: acne, dysmenorrhea, discharge, cravings, mucus
- Birth control: birth control pills, contraception

Medical Info:
- Sexual activity: sexual activity data, condom use
- Body temperature: 37°C
- Heart rate: 70 bpm
- Blood pressure: 100/75 (systolic/diastolic)
- Glucose levels: blood sugar data
- Medical conditions: diabetes, allergies, headache

Pattern: {name}
Initial Detection: True
Initial Reasoning: {initial_reasoning}

Request Content: {request_text}

Is this a TRUE POSITIVE or FALSE POSITIVE?
Verify the detected value matches the pattern semantically.
Provide reasoning (max 150 chars)."""
                        
                        task = {
                            "custom_id": f"validation-{idx}-{name}",
                            "method": "POST",
                            "url": "/v1/chat/completions",
                            "body": {
                                "model": self.model,
                                "temperature": self.temperature,
                                "max_tokens": 1000,
                                "response_format": get_validation_schema(),
                                "messages": [
                                    {
                                        "role": "system",
                                        "content": "You are a PII validation expert. Verify detections are accurate using semantic understanding."
                                    },
                                    {
                                        "role": "user",
                                        "content": prompt
                                    }
                                ]
                            }
                        }
                        tasks.append(task)
        
        print("Creating validation batch file...")
        os.makedirs(os.path.dirname(batch_file_path) or '.', exist_ok=True)
        with open(batch_file_path, 'w', encoding='utf-8') as f:
            for task in tasks:
                f.write(json.dumps(task) + '\n')
        
        print(f"Created {batch_file_path} with {len(tasks)} validation requests")
        return batch_file_path
    
    def upload_batch_file(self, batch_file_path: str) -> str:
        batch_file = self.client.files.create(
            file=open(batch_file_path, "rb"),
            purpose="batch"
        )
        print(f"File uploaded: {batch_file.id}")
        batch_job = self.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )
        print(f"Batch job started: {batch_job.id}")
        return batch_job.id
    
    def check_batch_status(self, batch_job_id: str) -> Dict:
        batch_job = self.client.batches.retrieve(batch_job_id)
        return {
            'id': batch_job.id,
            'status': batch_job.status,
            'request_counts': {
                'total': batch_job.request_counts.total,
                'completed': batch_job.request_counts.completed,
                'failed': batch_job.request_counts.failed
            },
            'output_file_id': getattr(batch_job, 'output_file_id', None)
        }
###################in the following method, the retry logic implementation was generated by cursor##############################################
    def download_results(self, batch_job_id: str, output_file: Optional[str] = None) -> str:
        status = self.check_batch_status(batch_job_id)
        if status['status'] != 'completed':
            raise ValueError(f"Job not completed yet. Status: {status['status']}")
        result_file_id = status['output_file_id']
        max_retries = 10
        retry_count = 0      
        while result_file_id is None and retry_count < max_retries:
            print(f"Waiting for output file to be ready... (attempt {retry_count + 1}/{max_retries})")
            time.sleep(2) 
            status = self.check_batch_status(batch_job_id)
            result_file_id = status['output_file_id']
            retry_count += 1       
        if result_file_id is None:
            raise ValueError("Output file ID not available after job completion.")
        result_content = self.client.files.content(result_file_id).content    
        if output_file is None:
            output_file = self._get_detection_results_path()       
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        with open(output_file, 'wb') as f:
            f.write(result_content)       
        print(f"Results saved: {output_file}")
        return output_file
 

 ###################for debugging of the integration functionality, cursor was used to generate parts of the following method##############################################

    def integrate_detection_results(self, results_file_path: str, traffic: pd.DataFrame, 
                                    patterns: List[Dict]) -> pd.DataFrame:
        if not os.path.exists(results_file_path):
            raise FileNotFoundError(f"Results file not found: {results_file_path}")
        results = []
        with open(results_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                results.append(json.loads(line))
        result_dict = {}
        for result in results:
            idx = int(result['custom_id'].split('-')[1])
            result_dict[idx] = result
        traffic_copy = traffic.copy()
        for pattern in patterns:
            name = pattern['name']
            traffic_copy[f'ai_detected_{name}'] = False
            traffic_copy[f'ai_reasoning_{name}'] = ''
            traffic_copy[f'ai_validation_reasoning_{name}'] = None
        success_count = 0
        error_count = 0
        
        for idx in result_dict:
            result = result_dict[idx]
            if result['response']['status_code'] == 200:
                try:
                    content = result['response']['body']['choices'][0]['message']['content']
                    detection_data = json.loads(content)
                    
                    for item in detection_data.get('detections', []):
                        pattern_name = item['pattern']
                        traffic_copy.at[idx, f'ai_detected_{pattern_name}'] = item['detected']
                        traffic_copy.at[idx, f'ai_reasoning_{pattern_name}'] = item['reasoning']
                    
                    success_count += 1
                except Exception as e:
                    print(f"Error parsing result for row {idx}: {e}")
                    error_count += 1
            else:
                error_count += 1
        print(f"Integration complete: {success_count} successful, {error_count} errors")
        return traffic_copy

    def integrate_validation_results(self, results_file_path: str, traffic_with_detection: pd.DataFrame) -> pd.DataFrame:
        if not os.path.exists(results_file_path):
            raise FileNotFoundError(f"Results file not found: {results_file_path}")
        results = []
        with open(results_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                results.append(json.loads(line))
        traffic_copy = traffic_with_detection.copy()
        false_positive_count = 0
        for result in results:
            parts = result['custom_id'].split('-', 2)
            idx = int(parts[1])
            pattern_name = parts[2]
            if result['response']['status_code'] == 200:
                try:
                    content = result['response']['body']['choices'][0]['message']['content']
                    validation_data = json.loads(content)
                    confirmed = validation_data['confirmed']
                    reasoning = validation_data['reasoning']
                    traffic_copy.at[idx, f'ai_validation_reasoning_{pattern_name}'] = reasoning
                    if not confirmed:
                        # False positive - flip detection to False
                        traffic_copy.at[idx, f'ai_detected_{pattern_name}'] = False
                        false_positive_count += 1
                except Exception as e:
                    print(f"Error parsing validation for row {idx}, pattern {pattern_name}: {e}")
        print(f"Validation complete: {false_positive_count} false positives removed")
        return traffic_copy



