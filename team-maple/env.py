from typing import TypedDict, List, Optional

ClientInfoDict = TypedDict('ClientInfoDict', {'ID': int, 'TOKEN': str, 'PREFIX': Optional[str], 'POTATO_CHANNEL_ID': Optional[int]}, total=False)

# Default prefix for all bots
PREFIX = 'm.'

# Add a dict containing the ID, TOKEN, and POTATO_CHANNEL_ID for each client
CLIENT_INFO: List[ClientInfoDict] = []
