from typing import TypedDict, List, Optional

ClientInfoDict = TypedDict('ClientInfoDict', {'ID': int, 'TOKEN': str, 'POTATO_CHANNEL_ID': Optional[int]})

# Add a dict containing the ID, TOKEN, and POTATO_CHANNEL_ID for each client
CLIENT_INFO: List[ClientInfoDict] = []
