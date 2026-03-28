import json
import requests
import uuid
import time

class LLMClient:

    COHERE_DEFAULT_PARAMS = {"input_type": "clustering", "embedding_types": ["float"]}
    LLM_DEFAULT_PARAMS = {"max_tokens": 64, "temperature": 1}


    def __init__(self, params: dict = {}, model_name: str = "", endpoint_override: str=None, return_raw_response: bool=False,
                tools=None, tool_params=None, is_embedding=False):
        """
        Base LLMClient. This is designed to maintain consistent model/param calls across long jobs.
        ---
        params (dict): the call parameters for the model. Can be overriden later.
        model_name (str): the model/deployment name. Pass in 'random' (and endpoint_override='local') to instantiate a random model.
        endpoint_override (str, None): if enabled, it defauls to the AzureOpenAI API. Pass in 'local' to use transformers.
        return_raw_response (bool, False): return the raw response object instead of response.json()
        is_embedding (bool, False): is it an embedding or a regular thingy
        tools, tool_params: probably will delete this
        """

        self._params = params
        self._model_name = model_name
        self._tool_params = tool_params
        self._tools = tools
        self._return_raw_response = return_raw_response

        self._is_azure = False
        self._is_hf = False
        self._is_rest = False
        self._is_embedding = is_embedding
        if self._is_embedding and endpoint_override is not None:
            print("You can only call embeddings from LLMAPI")
            raise ValueError

        self.model_name = self._model_name.replace("dev-", "")

        if params == {}:
            self._params = self.LLM_DEFAULT_PARAMS
            if is_embedding:
                self._params = {}
            if "cohere" in self._model_name:
                self._params = self.COHERE_DEFAULT_PARAMS
            print(f"Params are empty. Replaced with {self._params}")

        if endpoint_override is not None:
            if endpoint_override == "local":
                from transformers import pipeline
                import transformers
                #import os
                #os.environ['HF_HOME'] = "<path to cache>"
                if self._model_name == "random":
                    from transformers import Qwen2ForCausalLM, AutoConfig, AutoTokenizer
                    configuration = AutoConfig.from_pretrained("Qwen/Qwen2-1.5B-Instruct")
                    model = Qwen2ForCausalLM(configuration)
                    self._tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-1.5B-Instruct")
                    self._pipeline = pipeline(
                        "text-generation",
                        model=model,
                        config=configuration,
                        tokenizer=self._tokenizer,
                        device=0
                    )
                else:
                    self._pipeline = pipeline(
                        "text-generation",
                        model=self._model_name,
                        device_map="auto",)
                self._is_hf = True
            else:
                # pip install openai azure-identity
                # ensure you did az login
                from openai import OpenAI
                from azure.identity import DefaultAzureCredential, get_bearer_token_provider
                self._is_azure = True
                self._app = get_bearer_token_provider(
                    DefaultAzureCredential(),
                    "https://cognitiveservices.azure.com/.default"
                )
                self._API_VERSION = "2024-05-01-preview"
                self._ENDPOINT = endpoint_override
        else:
            from msal import PublicClientApplication
            # REST API
            authority = 'https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47'
            GUID = "68df66a4-cad9-4bfd-872b-c6ddde00d6b2"
            #self._SCOPES = ['api://'+ GUID +'/access']
            self._SCOPES = ['https://substrate.office.com/llmapi/LLMAPI.dev']
            self._app = PublicClientApplication(GUID,  authority=authority, enable_broker_on_windows=True)
            self._ENDPOINT = 'https://fe-26.qas.bing.net/sdf/chat/completions'
            if is_embedding:
                self._ENDPOINT = 'https://fe-26.qas.bing.net/sdf/embeddings'
            self._is_rest = True


    def update_params(self, params: dict):
        """ Update the parameters for a call.
        """
        for k, v in params.items():
            self._params[k] = params[k]


    def send_request(self, prompt, endpoint_override: str=None, tool_params=None, record_xcv: bool=False, 
                     input_types: str="clustering", debug=False):
        """
        Call the endpoint directly. It can be a REST call or an AzureOpenAI/Huggingface pipeline call.

        prompt: the thing you are sending to the endpoint. Typically a list.
        endpoint_override: str: use this if you are calling something other than your usual endpoint (e.g., chat/completions) 
        tool_params is an array like {"tools": tools, "tool_choice": "auto"}
        record_xcv: create a UUID to keep tabs on calls. Works with REST, not with other stuff.
        input_types (str, "clustering"): for Cohere embeddings only
        """

        token = self._get_token()
        xcv = str(uuid.uuid4())
        if record_xcv:
            with open("xcv_record.txt", "a", encoding="utf-8") as f: f.write(xcv + "\n")
        if debug: print("XCV:", xcv)

        if self._is_azure:
            # Instantiate the OpenAI client
            from openai import OpenAI
            client =OpenAI(
                base_url=self._ENDPOINT,
                api_key=token  # This uses the bearer token
            )

        if self._is_rest:
            headers = {
                'Content-Type':'application/json', 
                'Authorization': 'Bearer ' + token,
                'X-ModelType': self._model_name }
            X_GUID = "30297a6a-a182-4cb8-a72d-95e2fc4fd8fc" 
            headers["X-ScenarioGUID"] = X_GUID 
            headers['X-CV'] = xcv
            headers['X-Policy-ID'] = "nil"

            request = {k:v for k,v in self._params.items()}
            if type(prompt) == list and type(prompt[0]) == dict:
                request["messages"] = prompt
                if tool_params is not None:
                    for k, v in tool_params.items():
                        request[k] = v
                elif self._tools is not None:
                    request["tools"] = self._tools
                    if self._tool_params is not None:
                        for k, v in self._tool_params.items():
                            request[k] = v
            if self._is_embedding:
                # OpenAI embeddings will override self._params unless I find any call params in their docu
                request = {"input": prompt}
                if "cohere" in self._model_name:
                    request = {k:v for k,v in self._params.items()}
                    if type(prompt) != list: print("Warning: Cohere's embeddings require lists")
                    request["texts"] = prompt

            if debug: print("Preparing to send", json.dumps(request))
            body = str.encode(json.dumps(request))

        if self._is_azure:
            try:
                raw_response = client.chat.completions.create(model=self._model_name, messages=prompt)
            except:
                return {"error": {"message": "Azure Foundry blocked it because it is stupid"}}
            response = raw_response.json()
        elif self._is_hf:
            #eos_token_id=terminators
            raw_response = None
            try:
                raw_response = self._pipeline(prompt, do_sample=False, temperature=self._params["temperature"], 
                                              max_new_tokens=self._params["max_tokens"],)
                                              #pad_token_id = self._pipeline.tokenizer.eos_token_id)
            except:
                raw_response = {"error": "This model's maximum context"}
            # Adapt this to the signature from the REST API (most code works with that)
            if type(prompt) == list:
                message = raw_response[0]["generated_text"][-1]
            else:
                message = raw_response[0]["generated_text"][len(prompt):]
            # TODO: add logprobs, finish_reason, to choice
            # TODO: add reasoning_content, tool_calls to message
            # TODO: add usage: {prompt_tokens, total_tokens, completion_tokens}
            response = {"id": xcv, "model": self._model_name, "choices": [{"index": 0, "message": message}]}
        else:
            ept = self._ENDPOINT
            # Really dislike inconsistent APIs, but here we are.
            if "cohere" in self._model_name: ept = self._ENDPOINT.replace('embeddings', 'completions')
            raw_response = requests.post(ept, 
                                         data=body if self._structured_output is not None else {"response_format": prompt}, 
                                         headers=headers)
            response = raw_response.json()

        if debug: print("got", raw_response)
        if self._return_raw_response: return raw_response
        return response

    def _get_token(self):
        """ Handle authorisation for various call schemes.
        """

        if self._is_azure: return self._app()
        if self._is_hf: return None # TODO: handle hub auth

        accounts = self._app.get_accounts()
        result = None
        if accounts:
            # Assuming the end user chose this one
            chosen = accounts[0]
            # Now let's try to find a token in cache for this account
            result = self._app.acquire_token_silent(self._SCOPES, account=chosen)
        if not result:
            result = self._app.acquire_token_interactive(scopes=self._SCOPES, parent_window_handle=self._app.CONSOLE_WINDOW_HANDLE)
            if 'error' in result:
                raise ValueError(
                    f"Failed to acquire token. Error: {json.dumps(result, indent=4)}"
                )
        return result["access_token"]

    def bind_tool_params(self, tool_params):
        if self._tool_params is None:
            self._tool_params = {}
        for k, v in tool_params.items():
            self._tool_params[k] = tool_params[k]

    def bind_tools(self, tools):
        self._tools = tools

    def _structured_output(self, struct):
        # This makes no sense. Gotta fix later
        self._structured_output = struct



def get_llm_response(model: LLMClient, assembled_prompt: list, structured_output=False,
                     debug=False, force=False, use_tools=False):
    """
    Basic helper function to retrieve code from the LLM API. Assembled prompt may be a str for embeddings.
    """
    resp = None
    if debug: print(f"Sending: {assembled_prompt} of type {type(assembled_prompt)}")
    while True:
        try:
            resp = model.send_request(assembled_prompt)
            if debug: print(f"Got: {resp}")
            if force: return resp
        except TypeError:
            if debug: print("Type error found")
            raise
        except:
            time.sleep(1)
            continue
        if resp is not None:
            # This is to handle Azure's stupidity
            if debug: print(">", model.model_name)
            if "mistral" in model.model_name or "oss" in model.model_name:
                if debug: f"Got: {type(resp)}"
                if type(resp) == str: resp = json.loads(resp)

            if any([q in resp for q in ["choices", "embeddings", "data"]]):
                if debug: print(f"Suceeded and got: {resp}")
                break
        if resp is not None and "error" in resp:
            if "This model's maximum context" in resp["error"]["message"]:
                return "FAIL OOT"
            if "your prompt was flagged as potentially violating" in resp["error"]["message"]:
                return "FAIL FLAG"
            if "The response was filtered due to the prompt triggering Azure OpenAI's" in resp["error"]["message"]:
                return "FAIL RAI"
            return "FAIL"

    if model._is_embedding:
        if "cohere" in model._model_name:
            return resp["embeddings"]["float"] # Shape of (len(prompt), embedding_dim)
        else:
            resp["data"].sort(key=lambda x:x["index"])
            return [p["embedding"] for p in resp["data"]] # Shape of (len(prompt), embedding_dim)
    if use_tools or structured_output:
        return resp["choices"][0]["message"]
    return resp["choices"][0]["message"]["content"]


def retrieve(prompt: list, llm: LLMClient, DEFAULT_RESPONSE: dict={"Label": 0}, assert_fn=None, 
            return_raw=False, max_tries=5, debug=False) -> tuple:
    """ 
    Code to retrieve an output and validate it. Returns the response (or `DEFAULT_RESPONSE`) and a boolean (failed true/false).

    ---
    prompt (list): a prompt in ChatML form.
    llm (LLMClient): the LLM
    DEFAULT_RESPONSE (dict): the default response in case this thing fails.
    assert_fn (Callable): if not None, must return True if a test passes; False otherwise.
    return_raw (bool, False): return the raw response instead of parsing it.
    max_tries (int, 5): maximum times to attempt the call (default: 5)
    debug (bool, False): print stuff.
    """
    response = None
    tmp_response = None
    tries = 0
    while True:
        if debug: print("tries", tries)
        if tries > max_tries: break
        if response is not None: break
        try:
            response = get_llm_response(llm, prompt, debug=debug)
            if debug: print("finished resp", response, type(response))
            tmp_response = response
            y = "}".join(response.rsplit("}")[:-1]) + "}"
            y = "{" + "{".join(y.split("{")[1:])
            response = json.loads(y)
            if debug: print("parsed resp", response)
            # Hotfix for LLMAPI's dumbassery
            if "error" in response or response in ["FAIL", "FAIL OOT", "FAIL FLAG", "FAIL"]:
                tries += 1
                response = None
            if response is not None:
                if assert_fn is not None:
                    if not assert_fn(response):
                        if debug: print("assertion error")
                        response = None
                        tries += 1
                    else: 
                        if debug: print("assertion success returning")
                        break
                else:
                    if debug: print("resp is not none, returning")
                    break
        except:
            response = None
            tries += 1
    if return_raw:
        return tmp_response, None
    if response is None:
        return DEFAULT_RESPONSE, True
    return response, False
