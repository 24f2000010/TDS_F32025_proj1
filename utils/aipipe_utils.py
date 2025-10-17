"""
AIPipe.org API utilities for code generation
"""

import requests
import logging
import json

logger = logging.getLogger(__name__)

class AIPipeClient:
    def __init__(self, api_token):
        self.api_token = api_token
        # Use AIPipe's OpenAI proxy endpoint
        self.base_url = "https://aipipe.org/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def generate_code(self, brief, attachments=None, round_num=1, model="gpt-3.5-turbo"):
        """
        Generate code using AIPipe.org API
        
        Args:
            brief (str): Description of the app to build
            attachments (list): List of attachment objects
            round_num (int): Round number (1 for initial build, 2 for revision)
            model (str): Model to use for generation
        
        Returns:
            str: Generated code or None if failed
        """
        try:
            # Prepare the prompt based on round
            if round_num == 1:
                prompt = self._create_initial_prompt(brief, attachments)
            else:
                prompt = self._create_revision_prompt(brief, attachments)
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert web developer. Create clean, modern, and functional web applications. Always return complete, working code."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }
            
            logger.info(f"Making request to AIPipe.org API for round {round_num}")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_code = result['choices'][0]['message']['content']
                
                # Clean up the response (remove markdown formatting if present)
                generated_code = self._clean_generated_code(generated_code)
                
                logger.info("Successfully generated code with AIPipe.org")
                return generated_code
            else:
                logger.error(f"AIPipe.org API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating code with AIPipe.org: {str(e)}")
            return None
    
    def _create_initial_prompt(self, brief, attachments):
        """Create prompt for initial app generation"""
        prompt = f"""
Create a complete, modern web application based on this brief: {brief}

Requirements:
1. Create a single HTML file (index.html) with embedded CSS and JavaScript
2. Use Bootstrap 5 from CDN for responsive design and modern styling
3. Make it fully functional and ready to deploy
4. Include proper error handling and user feedback
5. Write clean, well-commented code
6. Ensure the app is accessible and user-friendly
7. Handle any data processing or API calls mentioned in the brief
8. Make the interface intuitive and professional

"""
        
        if attachments:
            prompt += "\nAttachments available:\n"
            for attachment in attachments:
                prompt += f"- {attachment['name']}: {attachment['url'][:100]}...\n"
            prompt += "\nUse these attachments in your application as needed.\n"
        
        prompt += """
Return ONLY the complete HTML code. Do not include any explanations, markdown formatting, or code blocks. Just the raw HTML that can be saved as index.html and run immediately.
"""
        
        return prompt
    
    def _create_revision_prompt(self, brief, attachments):
        """Create prompt for app revision"""
        prompt = f"""
Modify the existing web application based on this revision brief: {brief}

This is a revision request. Update the existing code to:
1. Implement the new requirements from the brief
2. Maintain all existing functionality
3. Keep the same overall structure but enhance it
4. Ensure all previous features still work
5. Add any new features requested
6. Improve the user experience where possible
7. Maintain the same styling approach (Bootstrap 5)

"""
        
        if attachments:
            prompt += "\nNew attachments available:\n"
            for attachment in attachments:
                prompt += f"- {attachment['name']}: {attachment['url'][:100]}...\n"
            prompt += "\nUse these new attachments in your updated application.\n"
        
        prompt += """
Return ONLY the complete updated HTML code. Do not include any explanations, markdown formatting, or code blocks. Just the raw HTML that can be saved as index.html and run immediately.
"""
        
        return prompt
    
    def _clean_generated_code(self, code):
        """Clean up generated code by removing markdown formatting"""
        # Remove markdown code blocks
        if code.startswith('```html'):
            code = code[7:]
        elif code.startswith('```'):
            code = code[3:]
        
        if code.endswith('```'):
            code = code[:-3]
        
        # Remove any leading/trailing whitespace
        code = code.strip()
        
        return code
    
    def test_connection(self):
        """Test the connection to AIPipe.org API"""
        try:
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error testing AIPipe.org connection: {str(e)}")
            return False
