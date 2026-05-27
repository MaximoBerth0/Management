"""
# used by orders/ 
async def reserve_stock()         # atomic (SELECT FOR UPDATE)
async def release_reservation()   # atomic (SELECT FOR UPDATE)
async def fulfill_reservation()   # atomic (SELECT FOR UPDATE)
"""
