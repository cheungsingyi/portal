#!/usr/bin/env python3
"""
Minimal LiteLLM Client for GitHub Copilot API

This script demonstrates how to use LiteLLM with a local Copilot API server
that implements an OpenAI-compatible API.

LiteLLM is a lightweight library that provides a unified interface to multiple LLM providers
using the OpenAI API format. It's perfect for connecting to local API servers that
implement the OpenAI API specification.
"""

import os
import sys
import requests
import logging
import litellm
import time

# Set up logging to see request details and debug information
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get a logger for this module
logger = logging.getLogger(__name__)

# Configure the base URL for the local Copilot API server
BASE_URL = "http://localhost:8888/v1"

# Prevent any accidental calls to actual OpenAI API
os.environ["OPENAI_API_KEY"] = "dummy-key-for-local-only"

# Configure LiteLLM global settings
litellm.api_base = BASE_URL          # Set the base URL for all requests
litellm.drop_params = True           # Drop parameters not supported by the server
litellm.telemetry = False            # Disable telemetry to avoid any external calls
litellm.set_verbose = True           # Show detailed logs for debugging

def check_server_availability():
    """Check if the local server is available"""
    logger.info(f"Checking server availability at http://localhost:8888")
    try:
        # Make a simple GET request to the server root
        response = requests.get("http://localhost:8888/", timeout=5)
        logger.info(f"Server status: {response.status_code}")
        logger.info(f"Server response: {response.text[:100]}...")
        
        # Check if the server is authenticated (if applicable)
        if "Not authenticated" in response.text:
            logger.warning("Server requires authentication. Please authenticate first.")
            print("⚠️ Server requires authentication. Please authenticate first.")
            print("  Visit http://localhost:8888/auth in your browser to authenticate.")
            return False
            
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to the local server")
        print("❌ Error: Could not connect to the local server at http://localhost:8888")
        print("   Make sure your Copilot API server is running.")
        return False
    except requests.exceptions.Timeout:
        logger.error("Connection to server timed out")
        print("❌ Error: Connection to server timed out")
        print("   The server might be overloaded or not responding.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking server: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False

def test_chat_completion():
    """Test chat completion with LiteLLM"""
    print("\n=== Testing LiteLLM Chat Completion with Copilot API ===\n")
    
    # Check server availability first
    if not check_server_availability():
        print("Skipping test as server is not available.")
        return None
    
    prompt = "Explain what a binary search tree is in simple terms."
    print(f"Prompt: {prompt}")
    print(f"🔒 Connecting to local API at: {BASE_URL}")
    print("   No connection to OpenAI servers will be made.")
    
    try:
        start_time = time.time()
        
        # Create a chat completion using LiteLLM's completion function
        # This automatically formats the request in OpenAI's format
        response = litellm.completion(
            model="gpt-4",  # This is just a label, actual model is determined by Copilot
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            api_base=BASE_URL,  # Explicitly set the base URL for this request
            api_key="dummy-key-for-local-only",  # Use a dummy key for local server
            temperature=0.7,
            max_tokens=500,
            request_timeout=30  # Set a reasonable timeout
        )
        
        end_time = time.time()
        
        # Extract the content from the response
        content = response.choices[0].message.content
        
        print(f"\n✅ Request completed in {end_time - start_time:.2f} seconds")
        print("\nResponse:")
        print(content)
        return content
    except litellm.exceptions.ServiceUnavailableError:
        logger.error("Service unavailable")
        print("❌ Error: Service unavailable. The server might be overloaded.")
        return None
    except litellm.exceptions.RequestTimeoutError:
        logger.error("Request timed out")
        print("❌ Error: Request timed out. The server took too long to respond.")
        return None
    except litellm.exceptions.BadRequestError as e:
        logger.error(f"Bad request: {str(e)}")
        print(f"❌ Error: Bad request - {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return None

def test_code_completion():
    """Test code completion with LiteLLM"""
    print("\n=== Testing LiteLLM Code Completion with Copilot API ===\n")
    
    # Check server availability first
    if not check_server_availability():
        print("Skipping test as server is not available.")
        return None
    
    prompt = "def factorial(n):\n    # Calculate factorial of n recursively\n    "
    print(f"Prompt:\n{prompt}")
    print(f"🔒 Connecting to local API at: {BASE_URL}")
    print("   No connection to OpenAI servers will be made.")
    
    try:
        start_time = time.time()
        
        # Create a completion using the text completion endpoint
        # The completion_type parameter tells LiteLLM to use the legacy completions endpoint
        response = litellm.completion(
            model="copilot-codex",  # This should match the endpoint in your server
            prompt=prompt,
            api_base=BASE_URL,
            api_key="dummy-key-for-local-only",
            temperature=0.7,
            max_tokens=500,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            request_timeout=30,
            completion_type="completion"  # Use legacy completions endpoint
        )
        
        end_time = time.time()
        
        # Extract the completion
        completion = response.choices[0].text
        
        print(f"\n✅ Request completed in {end_time - start_time:.2f} seconds")
        print("\nCompletion:")
        print(prompt + completion)
        return completion
    except litellm.exceptions.ServiceUnavailableError:
        logger.error("Service unavailable")
        print("❌ Error: Service unavailable. The server might be overloaded.")
        return None
    except litellm.exceptions.RequestTimeoutError:
        logger.error("Request timed out")
        print("❌ Error: Request timed out. The server took too long to respond.")
        return None
    except litellm.exceptions.BadRequestError as e:
        logger.error(f"Bad request: {str(e)}")
        print(f"❌ Error: Bad request - {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return None

def test_streaming_chat():
    """Test streaming chat completion with LiteLLM"""
    print("\n=== Testing LiteLLM Streaming Chat with Copilot API ===\n")
    
    # Check server availability first
    if not check_server_availability():
        print("Skipping test as server is not available.")
        return None
    
    prompt = "Write a short story about a programmer who discovers an AI that can predict the future."
    print(f"Prompt: {prompt}")
    print(f"🔒 Connecting to local API at: {BASE_URL}")
    print("   No connection to OpenAI servers will be made.")
    
    try:
        start_time = time.time()
        
        # Create a streaming chat completion
        # Setting stream=True enables streaming mode
        response = litellm.completion(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            api_base=BASE_URL,
            api_key="dummy-key-for-local-only",
            temperature=0.7,
            max_tokens=500,
            request_timeout=60,  # Longer timeout for streaming
            stream=True  # Enable streaming
        )
        
        print("\nStreaming Response:")
        full_content = ""
        chunk_count = 0
        
        # Process the stream
        for chunk in response:
            chunk_count += 1
            # Extract content from the delta if it exists
            if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                full_content += content_chunk
                print(content_chunk, end="", flush=True)
        
        end_time = time.time()
        
        print(f"\n\n✅ Streaming completed in {end_time - start_time:.2f} seconds")
        print(f"   Received {chunk_count} chunks")
        return full_content
    except litellm.exceptions.ServiceUnavailableError:
        logger.error("Service unavailable")
        print("\n❌ Error: Service unavailable. The server might be overloaded.")
        return None
    except litellm.exceptions.RequestTimeoutError:
        logger.error("Request timed out")
        print("\n❌ Error: Request timed out. The server took too long to respond.")
        return None
    except litellm.exceptions.BadRequestError as e:
        logger.error(f"Bad request: {str(e)}")
        print(f"\n❌ Error: Bad request - {str(e)}")
        return None
    except KeyboardInterrupt:
        print("\n⚠️ Streaming interrupted by user.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        return None

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("LiteLLM Minimal Client for GitHub Copilot API".center(70))
    print("=" * 70)
    print(f"API URL: {BASE_URL}")
    print("SECURITY NOTE: This client will ONLY connect to your local API server.")
    print("No connections to OpenAI servers will be made.")
    print("-" * 70)
    
    # Check if any specific test was requested via command line
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name == "chat":
            test_chat_completion()
        elif test_name == "code":
            test_code_completion()
        elif test_name == "stream":
            test_streaming_chat()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: chat, code, stream")
    else:
        # Run all tests
        test_chat_completion()
        test_code_completion()
        test_streaming_chat()
    
    print("\n" + "=" * 70)
    print("Tests completed".center(70))
    print("=" * 70)

if __name__ == "__main__":
    main()
