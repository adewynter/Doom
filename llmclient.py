import json
import base64
import random
import os
from openai import AzureOpenAI

    
api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment_name = '<your_deployment_name>'
api_version = '2023-12-01-preview'


class LLMClient:

    def __init__(self, params, model_name):
        """
        Mock class for the LLMClient. We can't share ours but you can write your own easily.
        """
        self._params = params
        self._model_name = model_name
        self._client = AzureOpenAI(api_key=api_key,
                                   api_version=api_version,
                                   base_url=f"{api_base}/openai/deployments/{deployment_name}"
                                   )


        
    def update_params(self, params):
        """
        Update params for the next call

        Parameters:
            params (Dict): call params to override in the next call
        """
        for k, v in params.items():
            self._params[k] = v

    def send_request(self, prompt):
        """
        Make a call

        Parameters:
            prompt (str): the prompt
        """
        response = self._client.completions.create(model=self._model_name,
                                                   prompt=prompt,
                                                   **self._params)
        return response
