#NFTs are always part of a collection.

collection_name = Variable() # The name of the collection for display
collection_owner = Variable() # Only the owner can mint new NFTs for this collection
collection_nfts = Hash(default_value=0) # All NFTs of the collection
collection_balances = Hash(default_value=0) # All user balances of the NFTs
collection_balances_approvals = Hash(default_value=0) # Approval amounts of certain NFTs

@construct
def seed(name: str):
    collection_name.set(name) # Sets the name
    collection_owner.set(ctx.caller) # Sets the owner

# function to mint a new NFT
@export
def mint_nft(name: str, description: str, ipfs_image_url: str, specials: dict, amount: int):
    assert name != "", "Name cannot be empty"
    assert name not in collection_nfts, "Name already exists"
    assert amount > 0, "You cannot transfer negative amounts"
    assert collection_owner == ctx.caller, "Only the collection owner can mint NFTs"

    collection_nfts[name] = {"description": description, "ipfs_image_url": ipfs_image_url, "specials": specials, "amount": amount} # Adds NFT to collection with all details
    collection_balances[ctx.caller, name] = amount # Mints the NFT

# standard transfer function
@export
def transfer(name: str, amount:int, to: str):
    assert amount > 0, "You cannot transfer negative amounts"
    assert name != "", "Please specify the name of the NFT you want to transfer"
    assert collection_balances[ctx.caller, name] >= amount, "You don't have enough NFTs to send"

    collection_balances[ctx.caller, name] -= amount # Removes amount from sender
    collection_balances[to, name] += amount # Adds amount to receiver

# allows other account to spend on your behalf
@export
def approve(amount: int, name: str, to: str):
    assert amount > 0, "Cannot approve negative amounts"

    collection_balances_approvals[ctx.caller, to, name] += amount # Approves certain amount for spending by another account

# transfers on your behalf
@export
def transfer_from(name:str, amount:int, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'

    assert collection_balances_approvals[main_account, to, name] >= amount, "Not enough NFTs approved to send! You have {} and are trying to spend {}"\
        .format(collection_balances_approvals[main_account, to, name], amount)
    assert collection_balances[main_account, name] >= amount, "Not enough NFTs to send!"

    collection_balances_approvals[main_account, to, name] -= amount # Removes Approval Amount
    collection_balances[main_account, name] -= amount # Removes amount from sender

    collection_balances[to, name] += amount # Adds amount to receiver