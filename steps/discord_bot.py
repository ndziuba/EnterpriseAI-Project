import pandas as pd
import requests
from zenml import step

@step(enable_cache=False)
def discord_alert(decision: bool, eval: float) -> int:
    """
    Send a message to the discord channel to report model status.
    """
    url = 'https://discord.com/api/webhooks/1128669713304662076/BE0-0j4d_q3-nkd5U-DFeouHzfmE9fxXgePJd_L8IDCK3Dxsw3BJlVPNPTWWjYBkfGub'
    
    data = {
        "content": "Model updated with an eval accuracy of: " + str(eval) if decision else "No performance increase achived, eval accuracy was:" + str(eval),
        "username": "Trainings Bot",
    }
    result = requests.post(url, json=data)
    print(result)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print(
            "Posted to discord successfully, code {}.".format(
                result.status_code
            )
        )
    print("Model updated" if decision else "No performance increase achived")
    return result.status_code

