from netrunner.netrunnerdb.decklist import Decklist

decklist = Decklist(id=79610)

print(decklist.id)
print(decklist.uuid)
print(decklist.date_creation)
print(decklist.date_update)
print(decklist.name)
print(decklist.description)
print(decklist.user_id)
print(decklist.user_name)
print(decklist.tournament_badge)
print(decklist.cards)
print(decklist.mwl_code)

decklist2 = Decklist(uuid="4493cfda-8cc3-4498-bff7-d249e039b681")
decklist3 = Decklist(uuid="b4d11875-27d9-4550-97d2-c99d218970fa")
print(decklist == decklist2)
print(decklist != decklist3)