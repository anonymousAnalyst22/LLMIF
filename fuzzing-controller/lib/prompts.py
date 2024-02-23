MISALIGNMENT_KEYWORD = "Misalignment found"
STATE_UNCHANGE_KEYWORD = "State unchanged"
DETERMINE_INTERESTING_CASE_PROMPT = """
You are a Zigbee expert.

Followings are descriptions of a Zigbee cluster command called "{}", which are enclosed by "+++".
+++
{}
+++

Following is the communication history with a freshly new Zigbee device, which are enclosed by "---".
---
{}
---

Based on the above command description and the communication history, please answer the following questions.
(1) Does the execution status for the command align with the command description? Think step-by-step and show your analysis. Finally summarize your answer in one verb: """\
+ f""" "Alignment detected" or "{MISALIGNMENT_KEYWORD}".""" \
+ f"""\n(2) Does the response imply any change of device's internal state? Think step-by-step and show your analysis. Finally summarize your answer in one verb: "State changed", "{STATE_UNCHANGE_KEYWORD}", or "State possibly changed".
"""