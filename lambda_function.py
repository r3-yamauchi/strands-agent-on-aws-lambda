import json
from typing import Dict, Any
from strands import Agent
from strands_tools import http_request, calculator, datetime_tool

ASSISTANT_SYSTEM_PROMPT = """You are a helpful AI assistant with access to various tools.
You can perform HTTP requests, calculate mathematical expressions, and get current date/time information.
Always be helpful and provide accurate information based on the tools available to you."""

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function that processes requests using Strands Agents SDK.
    
    Args:
        event: Lambda event containing the request data
        context: Lambda context object
        
    Returns:
        Response dictionary with statusCode and body
    """
    try:
        # Extract prompt from the event
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        prompt = body.get('prompt', event.get('prompt', ''))
        
        if not prompt:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No prompt provided',
                    'message': 'Please provide a prompt in the request body or event'
                })
            }
        
        # Optional: Extract model configuration from event
        model_config = body.get('model_config', {})
        
        # Create the agent with available tools
        agent = Agent(
            system_prompt=ASSISTANT_SYSTEM_PROMPT,
            tools=[http_request, calculator, datetime_tool],
            **model_config  # Allow custom model configuration
        )
        
        # Process the prompt
        response = agent(prompt)
        
        # Format the response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'response': str(response),
                'prompt': prompt,
                'success': True
            })
        }
        
    except json.JSONDecodeError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Invalid JSON',
                'message': f'Failed to parse request body: {str(e)}'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': f'An error occurred: {str(e)}',
                'type': type(e).__name__
            })
        }

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "body": json.dumps({
            "prompt": "What is the current date and time? Also, calculate 25 * 4 for me."
        })
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))