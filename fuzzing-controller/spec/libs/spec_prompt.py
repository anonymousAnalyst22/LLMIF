DEPENDENCY_KEYWORD = "Statement does hold"

GENERAL_DESCRIPTION_SUMMARY_PROMPT = """
Followings are descriptions of a communication protocol's message called "{}".

{}

You are requried to summarize the description to the message within 500 words.
In particular, you are required summarize the payload fields, the message's execution prerequisite, and influence on the target once the message is successfully received and executed.
"""

GENERAL_CMD_FORMAT_INFERENCE_PROMPT = """
Followings contain the description to a commnication protocol message called "{}".

{}

# Instructions
According to the description, please list the field names and field data types in the payload of the message, which are usually displayed in a Table or Figure.
Strictly follow the description, and do not generate any fake field names or field types. Note that a message payload may contain zero fields.
In order to keep the answer as concise as possible, use Python list grammar to display your answer. Followings are several examples for your reference.

# Example Outputs
Example Output 1 (Two fields):
[("Enable": "1 bits"), ("Magic Code", "N bytes")]

Example Output 2 (Empty payloads):
[]
"""

GENERAL_HEADER_PARSING_PROMPT = """
# Role

Followings contain the structure description for the message header of a communication protocol.

{}

# Instructions
You are required to summarize the structure of the message header.
Specifically, the header should contain several fields, each of which takes up several bits or bytes. You are required to identify these fields and their data types.
In order to keep the answer as concise as possible, use Python list grammar to display your answer. Following is an example for your reference.
[("Field 1", "2 bits"), ("Field 2", "1 bytes")]
"""

GENERAL_CMD_DEPENDENCY_PROMPT = """
Followings are descriptions of a communication protocol message called "{}".
"{}"

Followings are descriptions of another message called "{}".
"{}"

Please base on the above command description and determine if the following statement holds: "The consequence of the first message execution explicitly updates some device properties which the second message explicitly checks/examines before execution".
Think step by step and show your thought.
Finally, summarize your answer in one sentence: """ + f""" "{DEPENDENCY_KEYWORD}" or "Statement does not hold"."""