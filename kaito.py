from typing import Any, Dict, Iterator, List, Mapping, Optional
import requests
import json
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk


class Kaito(LLM):
    """A Kaito hosted model that echoes the first `n` characters of the input.

    When contributing an implementation to LangChain, carefully document
    the model including the initialization parameters, include
    an example of how to initialize the model and include any relevant
    links to the underlying models documentation or API.

    Example:

        .. code-block:: python

            model = KaitoChatModel(n=2)
            result = model.invoke([HumanMessage(content="hello")])
            result = model.batch([[HumanMessage(content="hello")],
                                 [HumanMessage(content="world")]])
    """

    endpoint: str
    """The endpoint of the model that Kaito is hosting."""

    model_name: str
    """The name of the model that Kaito is hosting."""

    temperature: float = 0.0
    """The temperature to use when generating text."""

    top_k: int = -1
    """The number of top tokens to consider. Set to -1 to consider all tokens."""

    top_p: float = 0.0
    """he cumulative probability threshold for nucleus sampling."""

    repetition_penalty: float = 1.0
    """The repetition penalty to use when generating text."""

    max_tokens: int = 1000
    """The maximum number of tokens to generate in the response."""

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given input.

        Override this method to implement the LLM logic.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of the stop substrings.
                If stop tokens are not supported consider raising NotImplementedError.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            The model output as a string. Actual completions SHOULD NOT include the prompt.
        """
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        # Set the headers and URL
        headers = {"Content-Type": "application/json"}
        url = ""
        if self.endpoint is not None:
            url = self.endpoint
        else:
            raise ValueError("No endpoint provided.")

        # Create the payload
        payload = {
            "model": self.model_name,
            "messages": json.loads(prompt),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "repetition_penalty": self.repetition_penalty,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "stream": True,
        }
        
        # make the request
        response = requests.request("POST", url=url, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                # Decode the line and parse the json
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    # Remove 'data: ' prefix
                    data = decoded_line[5:].strip()

                    # Check if it's the [DONE] signal
                    if data == '[DONE]':
                        break  # End the stream

                    try:
                        # Parse the JSON content
                        chunk = json.loads(data)

                        # Extract the content
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0]['delta']
                            if 'content' in delta:
                                content = delta['content']
                                yield content
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON: {data}")
                        continue

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": "KaitoModel",
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "kaito"