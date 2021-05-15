#
# Blank Module For Discord Bot
################################
import pickle, sys

"""
For a Custom Command !commandMe
"""

async def commandMe(Data, payload, *text):
    pass


"""
Initiate New Player
"""
async def on_member_join(Data,payload):
    pass


"""
Function Called on Reaction
"""
async def on_reaction(Data, payload):
    pass


"""
Main Run Function On Messages
"""
async def on_message(Data, payload):
    pass


"""
Update Function Called Every 10 Seconds
"""
async def update(Data, payload):
    pass


"""
Setup Log Parameters and Channel List And Whatever You Need to Check on a Bot Reset.
Handles Change In Server Structure and the like. Probably Can Leave Alone.
"""
async def setup(Data,payload):
    pass
